from collections.abc import AsyncGenerator
from acp_sdk.models import Message, MessagePart 
from acp_sdk.server import RunYield, RunYieldResume, Server
from crewai import Crew, Task, Agent, LLM

server = Server()

llm = LLM(
    model="ollama_chat/qwen2.5:14b", 
    base_url="http://localhost:11434", 
    max_tokens=8192
)

@server.agent()
async def research_drafter(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    """Agent that creates a general research summary on a given topic."""

    agent = Agent(
        role="Research summarizer",
        goal="Draft an informative and structured research summary based on the topic",
        backstory="You are a researcher who summarizes complex topics for general readers.",
        llm=llm
    )
    
    task = Task(
        description=f"Write a brief, clear summary on: {input[0].parts[0].content}",
        expected_output="A concise paragraph summarizing the topic",
        agent=agent
    )
    
    crew = Crew(agents=[agent], tasks=[task])
    task_output = await crew.kickoff_async()
    yield Message(parts=[MessagePart(content=str(task_output))])

if __name__ == "__main__":
    server.run(port=8000)