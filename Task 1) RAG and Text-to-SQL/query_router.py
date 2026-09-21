import os
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert
from llama_index.core import SQLDatabase, Settings
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_index.core.tools import QueryEngineTool
from llama_index.core.workflow import Workflow, Event, StartEvent, StopEvent, step
from llama_index.core.llms import ChatMessage
from llama_index.core.llms.llm import ToolSelection, LLM
from typing import Dict, List, Any, Optional

class InputEvent(Event):
    """Input event."""

class GatherToolsEvent(Event):
    """Gather Tools Event"""
    tool_calls: Any

class ToolCallEvent(Event):
    """Tool Call event"""
    tool_call: ToolSelection

class ToolCallEventResult(Event):
    """Tool call event result."""
    msg: ChatMessage

class RouterOutputAgentWorkflow(Workflow):
    """Custom router output agent workflow."""

    def __init__(self,
                tools: List[QueryEngineTool],
                timeout: Optional[float] = 10.0,
                disable_validation: bool = False,
                verbose: bool = False,
                llm: Optional[LLM] = None,
                chat_history: Optional[List[ChatMessage]] = None,
                ):
        """Constructor."""
        super().__init__(timeout=timeout, disable_validation=disable_validation, verbose=verbose)
        
        self.tools = tools
        self.tools_dict = {tool.metadata.name: tool for tool in self.tools}
        self.llm = llm or OpenAI(temperature=0, model="gpt-3.5-turbo")
        self.chat_history = chat_history or []

    def reset(self) -> None:
        """Resets Chat History"""
        self.chat_history = []

    @step()
    async def prepare_chat(self, ev: StartEvent) -> InputEvent:
        message = ev.get("message")
        if message is None:
            raise ValueError("'message' field is required.")
        
        # add msg to chat history
        chat_history = self.chat_history
        chat_history.append(ChatMessage(role="user", content=message))
        return InputEvent()

    @step()
    async def chat(self, ev: InputEvent) -> GatherToolsEvent | StopEvent:
        """Appends msg to chat history, then gets tool calls."""
        
        # Put msg into LLM with tools included
        chat_res = await self.llm.achat_with_tools(
            self.tools,
            chat_history=self.chat_history,
            verbose=self._verbose,
            allow_parallel_tool_calls=True
        )
        tool_calls = self.llm.get_tool_calls_from_response(chat_res, error_on_no_tool_call=False)
        
        ai_message = chat_res.message
        self.chat_history.append(ai_message)
        
        # no tool calls, return chat message.
        if not tool_calls:
            return StopEvent(result=ai_message.content)
        
        return GatherToolsEvent(tool_calls=tool_calls)

    @step()
    async def dispatch_calls(self, ev: GatherToolsEvent) -> Event:
        """Dispatches calls."""
        tool_calls = ev.tool_calls
        
        # trigger tool call events
        tool_call_results = []
        for tool_call in tool_calls:
            # call tool
            tool = self.tools_dict[tool_call.tool_name]
            output = await tool.acall(**tool_call.tool_kwargs)
            
            # create chat message from result
            msg = ChatMessage(
                name=tool_call.tool_name,
                content=str(output),
                role="tool",
                additional_kwargs={
                    "tool_call_id": tool_call.tool_id,
                    "name": tool_call.tool_name
                }
            )
            tool_call_results.append(msg)
        
        # add all tool call results to chat history
        for msg in tool_call_results:
            self.chat_history.append(msg)
        
        return Event()

    @step()
    async def generate_response(self, ev: Event) -> StopEvent:
        # generate final response based on updated chat history
        chat_res = await self.llm.achat(
            self.chat_history,
            verbose=self._verbose
        )
        
        ai_message = chat_res.message
        self.chat_history.append(ai_message)
        
        return StopEvent(result=ai_message.content)

def setup_database():
    """Setup in-memory SQL database with city statistics"""
    engine = create_engine("sqlite:///:memory:", future=True)
    metadata_obj = MetaData()
    
    # Create city SQL table
    city_stats_table = Table(
        "city_stats",
        metadata_obj,
        Column("city_name", String(16), primary_key=True),
        Column("population", Integer),
        Column("state", String(16), nullable=False),
    )
    
    metadata_obj.create_all(engine)
    
    # Insert data
    rows = [
        {"city_name": "New York City", "population": 8336000, "state": "New York"},
        {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
        {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
        {"city_name": "Houston", "population": 2303000, "state": "Texas"},
        {"city_name": "Miami", "population": 449514, "state": "Florida"},
        {"city_name": "Seattle", "population": 749256, "state": "Washington"},
    ]
    
    for row in rows:
        stmt = insert(city_stats_table).values(**row)
        with engine.begin() as connection:
            connection.execute(stmt)
    
    return engine

def create_query_engines(engine, llama_cloud_api_key, llama_cloud_index_name, 
                         llama_cloud_project_name, llama_cloud_org_id):
    """Create SQL and LlamaCloud query engines"""
    # Setup SQL query engine
    sql_database = SQLDatabase(engine, include_tables=["city_stats"])
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=["city_stats"]
    )
    
    # Setup LlamaCloud query engine
    index = LlamaCloudIndex(
        name=llama_cloud_index_name,
        project_name=llama_cloud_project_name,
        organization_id=llama_cloud_org_id,
        api_key=llama_cloud_api_key
    )
    
    llama_cloud_query_engine = index.as_query_engine()
    
    # Create query engine tools
    sql_tool = QueryEngineTool.from_defaults(
        query_engine=sql_query_engine,
        description=(
            "Useful for translating a natural language query into a SQL query over"
            " a table containing: city_stats, containing the population/state of"
            " each city located in the USA."
        ),
        name="sql_tool"
    )
    
    llama_cloud_tool = QueryEngineTool.from_defaults(
        query_engine=llama_cloud_query_engine,
        description=(
            "Useful for answering semantic questions about certain cities in the US."
        ),
        name="llama_cloud_tool"
    )
    
    return sql_tool, llama_cloud_tool

async def process_query(workflow, query):
    """Process a query through the workflow"""
    result = await workflow.run(message=query)
    return result

def create_workflow(tools, llm=None, verbose=False):
    """Create the router workflow"""
    workflow = RouterOutputAgentWorkflow(
        tools=tools,
        verbose=verbose,
        timeout=120,
        llm=llm
    )
    return workflow