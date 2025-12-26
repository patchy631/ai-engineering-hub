from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from config.settings import WORKFLOW_TIMEOUT
from .sql_tool import create_sql_tool
from .rag_tool import create_rag_tool

def create_workflow():
    sql_tool = create_sql_tool()
    llama_cloud_tool = create_rag_tool()
    
    llm = OpenAI(model="gpt-3.5-turbo")
    
    return OpenAIAgent.from_tools(
        tools=[sql_tool, llama_cloud_tool],
        llm=llm,
        verbose=True,
        timeout=WORKFLOW_TIMEOUT
    )

async def run_workflow(workflow, question: str):
    result = await workflow.achat(question)
    return str(result) 