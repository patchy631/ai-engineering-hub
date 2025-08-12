# rename .env.example to .env and add the following:
# SERPER_API_KEY=your_serper_api_key
# OPENAI_API_KEY=your_openai_api_key

from crewai import Crew, Agent, Task, LLM
import litserve as ls
from crewai_tools import SerperDevTool

# If you'd like, you can use a local LLM as well through Ollama. Do this:
# ollama pull qwen3 in the command line.

# Uncomment the following line and also the llm=llm line in the Agents definitions.
# llm = LLM(model="ollama/qwen3")

class AgenticRAGAPI(ls.LitAPI):
    def setup(self, device):
        researcher_agent = Agent(
            role="Researcher",
            goal="Research about the user's query and generate insights",
            backstory="You are a helpful assistant that can answer questions about the document.",
            verbose=True,
            tools=[SerperDevTool()],
            # llm=llm
        )

        writer_agent = Agent(
            role="Writer",
            goal="Use the available insights to write a concise and informative response to the user's query",
            backstory="You are a helpful assistant that can write a report about the user's query",
            verbose=True,
            # llm=llm
        )
        
        researcher_task = Task(
            description="Research about the user's query and generate insights: {query}",
            expected_output="A concise and informative report about the user's query",
            agent=researcher_agent,
        )

        writer_task = Task(
            description="Use the available insights to write a concise and informative response to the user's query: {query}",
            expected_output="A concise and informative response to the user's query",
            agent=writer_agent,
        )
        
        self.crew = Crew(
            agents=[researcher_agent, writer_agent],
            tasks=[researcher_task, writer_task],
            verbose=True,
        )

    def decode_request(self, request):
        return request["query"]

    def predict(self, query):
        return self.crew.kickoff(inputs={"query": query})

    def encode_response(self, output):
        return {"output": output}

if __name__ == "__main__":
    api = AgenticRAGAPI()
    server = ls.LitServer(api)
    server.run(port=8000)