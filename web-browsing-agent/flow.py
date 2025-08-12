from typing import Dict, Any
from dotenv import load_dotenv
from pydantic import BaseModel
from crewai import Agent, Task, Crew
from crewai import LLM
from crewai.tools import tool
from crewai.flow.flow import Flow, start, listen
from stagehand_tool import browser_automation


load_dotenv()

# Define our LLMs for providing to agents
planner_llm = LLM(model="ollama/gpt-oss")
automation_llm = LLM(model="openai/gpt-4")
response_llm = LLM(model="ollama/gpt-oss")


@tool("Stagehand Browser Tool")
def stagehand_browser_tool(task_description: str, website_url: str) -> str:
    """
    A tool that allows to interact with a web browser.
    The tool is used to perform browser automation tasks powered by Stagehand capabilities.

    Args:
        task_description (str): The task description for the agent to perform.
        website_url (str): The URL of the website to interact and navigate to.

    Returns:
        str: The result of the browser automation task.
    """
    return browser_automation(task_description, website_url)


class BrowserAutomationFlowState(BaseModel):
    query: str = ""
    result: str = ""


class AutomationPlan(BaseModel):
    task_description: str
    website_url: str


class BrowserAutomationFlow(Flow[BrowserAutomationFlowState]):
    """
    A CrewAI Flow to intelligently handle browser automation tasks
    through specialized agents using Stagehand tools.
    """

    @start()
    def start_flow(self) -> Dict[str, Any]:
        print(f"Flow started with query: {self.state.query}")
        return {"query": self.state.query}

    @listen(start_flow)
    def plan_task(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        print("--- Using Automation Planner to plan the task ---")

        planner_agent = Agent(
            role="Automation Planner Specialist",
            goal="Plan the automation task for the user's query.",
            backstory="You are a browser automation specialist that plans the automation task for the user's query.",
            llm=planner_llm,
        )

        plan_task = Task(
            description=f"Analyze the following user query and determine the website url and the task description: '{inputs['query']}'.",
            agent=planner_agent,
            output_pydantic=AutomationPlan,
            expected_output=(
                "A JSON object with the following format:\n"
                "{\n"
                '  "task_description": "<brief description of what needs to be done>",\n'
                '  "website_url": "<URL of the target website>"\n'
                "}"
            ),
        )

        crew = Crew(agents=[planner_agent], tasks=[plan_task], verbose=True)
        result = crew.kickoff()

        # Add a fallback check to ensure we always have a valid website URL
        website_url = result.pydantic.website_url
        if not website_url or website_url.lower() in ["", "none", "null", "n/a"]:
            result["website_url"] = "https://www.google.com"

        return {
            "task_description": result["task_description"],
            "website_url": website_url,
        }

    @listen(plan_task)
    def handle_browser_automation(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        print("--- Delegating to Browser Automation Specialist ---")

        automation_agent = Agent(
            role="Browser Automation Specialist",
            goal="Execute browser automation using the Stagehand tool",
            backstory="You specialize in executing user-defined automation tasks on websites using the Stagehand tool.",
            tools=[stagehand_browser_tool],
            llm=automation_llm,
        )

        automation_task = Task(
            description=(
                f"Perform the following browser automation task:\n\n"
                f"Website: {inputs['website_url']}\n"
                f"Task: {inputs['task_description']}\n\n"
                f"Use the Stagehand tool to complete this task accurately."
            ),
            agent=automation_agent,
            expected_output="A string containing the result of executing the browser automation task using Stagehand.",
            markdown=True,
        )

        crew = Crew(agents=[automation_agent], tasks=[automation_task], verbose=True)
        result = crew.kickoff()
        return {"result": str(result)}

    @listen(handle_browser_automation)
    def synthesize_result(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        print("--- Synthesizing Final Response ---")

        synthesis_agent = Agent(
            role="Response Synthesis Specialist",
            goal="Craft a clear, concise, and user-friendly response based on the tool calling output from the browser automation specialist.",
            backstory="An expert in communication and assistance.",
            llm=response_llm,
        )

        synthesis_task = Task(
            description=(
                f"Review the following browser automation specialist result and present it as a generalized, coherent response for the end user:\n\n"
                f"{inputs['result']}"
            ),
            expected_output="A concise, user-facing response of the browser automation result.",
            agent=synthesis_agent,
        )

        crew = Crew(agents=[synthesis_agent], tasks=[synthesis_task], verbose=True)
        final_result = crew.kickoff()
        return {"result": str(final_result)}


# Usage example
async def main():
    flow = BrowserAutomationFlow()
    flow.state.query = "Extract the top contributor's username from this GitHub repository: https://github.com/browserbase/stagehand"
    result = await flow.kickoff_async()

    print(f"\n{'='*50}")
    print(f"FINAL RESULT")
    print(f"{'='*50}")
    print(result["result"])


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
