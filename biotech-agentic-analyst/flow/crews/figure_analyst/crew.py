from __future__ import annotations

import os
from typing import List

from crewai import Agent, Crew, LLM, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from models import FigureIntelligenceList

# Primary: multimodal, 400K context, ~12x cheaper than gpt-4o ($0.20/$1.25 per M tokens).
# Override with FIGURE_ANALYST_MODEL env var, e.g. openrouter/openai/gpt-oss-120b:free
_FIGURE_MODEL = os.getenv("FIGURE_ANALYST_MODEL", "openrouter/openai/gpt-5.4-nano")


@CrewBase
class FigureAnalystCrew:
    """Crew for extracting structured intelligence from scientific figures."""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def figure_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["figure_analyst"],  # type: ignore[index]
            llm=LLM(model=_FIGURE_MODEL),
            verbose=True,
            allow_delegation=False,
            multimodal=True,
        )

    @task
    def figure_analysis(self) -> Task:
        return Task(
            config=self.tasks_config["figure_analysis"],  # type: ignore[index]
            output_pydantic=FigureIntelligenceList,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
