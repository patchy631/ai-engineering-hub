from langgraph.graph import StateGraph, END ,START
from pydantic import BaseModel, Field
from langchain_core.runnables import Runnable
from typing import TypedDict, Literal, Optional
from langchain_core.messages import AIMessage, HumanMessage
import ast
from IPython.display import Image, display
from typing import Dict
from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv
from langgraph.errors import NodeInterrupt
import yfinance as yf
load_dotenv()


llm = AzureChatOpenAI(
    azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT'],
    azure_deployment=os.environ['AZURE_OPENAI_DEPLOYMENT_NAME'],
    openai_api_version=os.environ['AZURE_OPENAI_API_VERSION'],
    openai_api_key=os.environ['AZURE_OPENAI_API_KEY']  
)



class QueryFields(BaseModel):
    symbol: str = Field(..., description="Stock ticker symbol (e.g., TSLA, AAPL).")
    timeframe: str = Field(..., description="Time period (e.g., '1d', '1mo', '1y').")
    action: str = Field(..., description="Action to be performed (e.g., 'fetch', 'plot').")

class QueryAnalysisOutput(BaseModel):
    result: QueryFields
class StockAnalysisState(TypedDict):
    query: str
    parsed_output: QueryAnalysisOutput
    generated_code: Optional[str]
    execution_result: Optional[str]



def query_parser_node(state: StockAnalysisState):
    query = state["query"]
    prompt = """You are a Stock Data Analyst. Extract stock details from this user query: {query}. 
    
    """
    finalprompt=prompt.format(query=query)
    llm_with_struc=llm.with_structured_output(QueryAnalysisOutput)
    response = llm_with_struc.invoke(finalprompt)
    
    return {"parsed_output": response}

def code_writer_node(state: StockAnalysisState):
    parsed = state["parsed_output"]
    if isinstance(parsed, dict):
        raise NodeInterrupt("recieved wrong type")
    fprompt = """You are a Senior Python Developer. Generate code to {action} the stock data.
    Stock: {symbol}
    Timeframe: {timeframe}

    Use yfinance, pandas, and matplotlib libraries. Output should be a clean, executable .py Python script for stock visualization without explanations or AI-generated messages—just the direct script content. without ''' or any code blockers
    """
    action=parsed.result.action
    symbol=parsed.result.symbol
    time=parsed.result.timeframe
    ffprompt=fprompt.format(action=action,symbol=symbol,timeframe=time)
    code = llm.invoke(ffprompt)
    return {"generated_code": code}


def code_result(state: StockAnalysisState):
    
    generated_code = state["generated_code"]
    try:
        # Execute the generated code in a controlled environment
        exec_globals = {}
        exec(generated_code.content, exec_globals)
        return {"execution_result": "Code executed successfully"}
    except Exception as e:
        return {"execution_result": f"Execution failed: {str(e)}"}


graph = StateGraph(StockAnalysisState)

graph.add_node("QueryParser", query_parser_node)
graph.add_node("CodeWriter", code_writer_node)
graph.add_node("CodeExecutor", code_result)


graph.add_edge(START,"QueryParser")
graph.add_edge("QueryParser", "CodeWriter")
graph.add_edge("CodeWriter", "CodeExecutor")
graph.add_edge("CodeExecutor", END)


workflow = graph.compile()

#visual representation of our graph
#display(Image(workflow.get_graph(xray=1).draw_mermaid_png()))


# Function to be wrapped inside MCP tool
def run_financial_analysis(query):
    result = workflow.invoke({"query": query})
    
    return result["generated_code"].content

if __name__ == "__main__":
    res=run_financial_analysis("Plot YTD stock gain of Tesla")
    print(res)
