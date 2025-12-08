import os
from crewai import Agent, Task, Crew, LLM
from crewai.project import CrewBase, agent, task, crew

from ai_news_flow.models import ContentDraft

@CrewBase
class ContentCrew:
    """Content creation crew for transforming research into engaging articles."""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self, llm=None, temperature=0.7):
        self.llm = llm or LLM(model="command-r", temperature=temperature)

    @agent
    def content_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['content_strategist'],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    @agent  
    def content_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['content_writer'],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def seo_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['seo_specialist'],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    @task
    def content_strategy_task(self) -> Task:
        return Task(
            config=self.tasks_config['content_strategy_task'],
            agent=self.content_strategist()
        )

    @task
    def content_creation_task(self) -> Task:
        return Task(
            config=self.tasks_config['content_creation_task'],
            agent=self.content_writer(),
            context=[self.content_strategy_task()],
            output_pydantic=ContentDraft
        )

    @task
    def seo_optimization_task(self) -> Task:
        return Task(
            config=self.tasks_config['seo_optimization_task'],
            agent=self.seo_specialist(),
            context=[self.content_creation_task()],
            output_pydantic=ContentDraft
        )

    @crew
    def crew(self) -> Crew:
        """Create the content creation crew."""
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