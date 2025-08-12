from collections.abc import AsyncGenerator
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import RunYield, RunYieldResume, Server
from smolagents import CodeAgent, LiteLLMModel, DuckDuckGoSearchTool
import warnings

warnings.filterwarnings("ignore")

server = Server()

model = LiteLLMModel(
    model_id="ollama_chat/qwen2.5:14b",
    api_base="http://localhost:11434",
    # api_key="your-api-key",
    num_ctx=8192
)

@server.agent()
async def research_verifier(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    """Agent that fact-checks and enhances a research summary using web search."""

    agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=model)

    prompt = input[0].parts[0].content
    response = agent.run(prompt)

    yield Message(parts=[MessagePart(content=str(response))])

if __name__ == "__main__":
    server.run(port=8001)