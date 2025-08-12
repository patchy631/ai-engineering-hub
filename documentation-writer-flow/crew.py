from crewai import Agent, Task, Crew
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    WebsiteSearchTool
)
# Import helper functions
from utils import load_llm, load_yaml_config, check_mermaid_syntax
from schemas.models import DocPlan

# Configuration paths
PLANNER_AGENTS_PATH = "config/planner_agents.yaml"
PLANNER_TASKS_PATH = "config/planner_tasks.yaml"
DOC_AGENTS_PATH = "config/documentation_agents.yaml"
DOC_TASKS_PATH = "config/documentation_tasks.yaml"

def initialize_planning_crew():
    # Load agent and task configurations from YAML files
    agents_config = load_yaml_config(PLANNER_AGENTS_PATH)
    tasks_config = load_yaml_config(PLANNER_TASKS_PATH)

    code_explorer = Agent(
        config=agents_config['code_explorer'],
        tools=[
            DirectoryReadTool(),
            FileReadTool()
        ],
        llm=load_llm()
    )

    documentation_planner = Agent(
        config=agents_config['documentation_planner'],
        tools=[
            DirectoryReadTool(),
            FileReadTool()
        ],
        llm=load_llm()
    )

    analyze_codebase = Task(
        config=tasks_config['analyze_codebase'],
        agent=code_explorer
    )

    create_documentation_plan = Task(
        config=tasks_config['create_documentation_plan'],
        agent=documentation_planner,
        output_pydantic=DocPlan
    )

    return Crew(
        agents=[code_explorer, documentation_planner],
        tasks=[analyze_codebase, create_documentation_plan],
        verbose=False
    )

def initialize_documentation_crew():
    # Load agent and task configurations from YAML files
    agents_config = load_yaml_config(DOC_AGENTS_PATH)
    tasks_config = load_yaml_config(DOC_TASKS_PATH)

    overview_writer = Agent(
        config=agents_config['overview_writer'], 
        tools=[
            DirectoryReadTool(),
            FileReadTool(),
            WebsiteSearchTool(
                website="https://mermaid.js.org/intro/",
                config=dict(
                    embedder=dict(
                        provider="ollama",
                        config=dict(
                            model="nomic-embed-text",
                        ),
                    )
                )
            )
        ],
        llm=load_llm()
    )

    documentation_reviewer = Agent(
        config=agents_config['documentation_reviewer'], 
        tools=[
            DirectoryReadTool(
                directory="docs/", 
                name="Check existing documentation folder"
            ),
            FileReadTool(),
        ],
        llm=load_llm()
    )

    draft_documentation = Task(
        config=tasks_config['draft_documentation'],
        agent=overview_writer
    )

    qa_review_documentation = Task(
        config=tasks_config['qa_review_documentation'],
        agent=documentation_reviewer,
        guardrail=check_mermaid_syntax,
        max_retries=5
    )

    return Crew(
        agents=[overview_writer, documentation_reviewer],
        tasks=[draft_documentation, qa_review_documentation],
        verbose=False
    )