import os
from crewai import Agent, Task, Crew, LLM
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import SerperDevTool

from ai_news_flow.tools.custom_tools import SourceCredibilityTool, EnhancedSearchTool
from ai_news_flow.models import ResearchReport

@CrewBase
class ResearchCrew:
    """Research crew for comprehensive topic investigation."""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self, llm=None, temperature=0.7):
        self.llm = llm or LLM(model="command-r", temperature=temperature)
        self.search_tool = SerperDevTool(n_results=10)
        self.credibility_tool = SourceCredibilityTool()
        self.enhanced_search = EnhancedSearchTool()

    @agent
    def senior_research_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['senior_research_analyst'],
            tools=[self.search_tool, self.credibility_tool, self.enhanced_search],
            llm=self.llm,
            verbose=True,
            allow_delegation=True
        )

    @agent  
    def fact_checker(self) -> Agent:
        return Agent(
            config=self.agents_config['fact_checker'],
            tools=[self.credibility_tool],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    @agent
    def data_synthesizer(self) -> Agent:
        return Agent(
            config=self.agents_config['data_synthesizer'],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
            agent=self.senior_research_analyst(),
            output_pydantic=ResearchReport
        )

    @task
    def fact_checking_task(self) -> Task:
        return Task(
            config=self.tasks_config['fact_checking_task'],
            agent=self.fact_checker(),
            context=[self.research_task()]
        )

    @task
    def synthesis_task(self) -> Task:
        return Task(
            config=self.tasks_config['synthesis_task'],
            agent=self.data_synthesizer(),
            context=[self.research_task(), self.fact_checking_task()],
            output_pydantic=ResearchReport
        )

    @crew
    def crew(self) -> Crew:
        """Create the research crew."""
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