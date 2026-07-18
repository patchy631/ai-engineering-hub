# Code Snippets for Twitter Thread

## Snippet 1: Setting up the tools

```python
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
```

## Snippet 2: Creating the SQL database

```python
from llama_index.core import SQLDatabase, Settings
from llama_index.llms.openai import OpenAI
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer

# Create engine and metadata
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

# Create SQL query engine
sql_database = SQLDatabase(engine, include_tables=["city_stats"])
sql_query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=["city_stats"]
)
```

## Snippet 3: Creating the RAG index

```python
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex

# Create LlamaCloud index
index = LlamaCloudIndex(
    name="us-cities-index",
    project_name="demo-project",
    organization_id="your-org-id",
    api_key="your-api-key"
)

# Create RAG query engine
llama_cloud_query_engine = index.as_query_engine()
```

## Snippet 4: The core workflow class

```python
class RouterOutputAgentWorkflow(Workflow):
    """Custom router output agent workflow."""

    def __init__(self,
        tools: List[BaseTool],
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

        # No tool calls, return chat message
        if not tool_calls:
            return StopEvent(result=chat_res.message.content)

        return GatherToolsEvent(tool_calls=tool_calls)
```

## Snippet 5: Running the workflow

```python
# Create the workflow instance
wf = RouterOutputAgentWorkflow(
    tools=[sql_tool, llama_cloud_tool],
    verbose=True
)

# Run the workflow with a user query
result = await wf.run(message="Which city has the highest population?")
print(result)
# Output: "New York City has the highest population."

result = await wf.run(message="What attractions are in Miami?")
print(result)
# Output: "Here are some places to visit in Miami: Beaches and parks, Zoo Miami, Jungle Island..."
```

## Snippet 6: Streamlit UI code

```python
import streamlit as st

# App title and description
st.title("🦙 RAG + Text-to-SQL Unified Query Interface")
st.markdown("""
This application demonstrates how to combine Retrieval-Augmented Generation (RAG)
and Text-to-SQL capabilities in a single query interface.
""")

# Chat input
if prompt := st.chat_input("Ask a question about US cities..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # In a real app, this would call the workflow
            result = await wf.run(message=prompt)
            st.markdown(result)
```
