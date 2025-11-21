import os
from crewai import Agent, Task, Crew, LLM
from crewai.project import CrewBase, agent, task, crew

from ai_news_flow.tools.custom_tools import ReadabilityAnalyzer
from ai_news_flow.models import EditedContent

@CrewBase
class EditingCrew:
    """Editing crew for polishing and finalizing content."""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self, llm=None, temperature=0.5):
        # Lower temperature for editing tasks to ensure consistency
        self.llm = llm or LLM(model="command-r", temperature=temperature)
        self.readability_tool = ReadabilityAnalyzer()

    @agent
    def copy_editor(self) -> Agent:
        return Agent(
            config=self.agents_config['copy_editor'],
            tools=[self.readability_tool],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    @agent  
    def technical_editor(self) -> Agent:
        return Agent(
            config=self.agents_config['technical_editor'],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def publishing_editor(self) -> Agent:
        return Agent(
            config=self.agents_config['publishing_editor'],
            tools=[self.readability_tool],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    @task
    def copy_editing_task(self) -> Task:
        return Task(
            config=self.tasks_config['copy_editing_task'],
            agent=self.copy_editor()
        )

    @task
    def technical_editing_task(self) -> Task:
        return Task(
            config=self.tasks_config['technical_editing_task'],
            agent=self.technical_editor(),
            context=[self.copy_editing_task()]
        )

    @task
    def final_editing_task(self) -> Task:
        return Task(
            config=self.tasks_config['final_editing_task'],
            agent=self.publishing_editor(),
            context=[self.copy_editing_task(), self.technical_editing_task()],
            output_pydantic=EditedContent
        )

    @crew
    def crew(self) -> Crew:
        """Create the editing crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process="sequential",
            verbose=True,
            memory=True,
            embedder={
                "provider": "cohere",
                "config": {
                    "model": "embed-english-v3.0"
                }
            }
        )