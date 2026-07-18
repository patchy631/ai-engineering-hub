from pathlib import Path
from typing import Any, Dict, Optional
import json
from crewai import Agent, LLM
from crewai.flow.flow import Flow, and_, listen, start
from crewai_tools import ScrapeWebsiteTool
from pydantic import BaseModel, Field, field_validator

from agent_tools import job_automation, read_docx_file
from models import JobDescription, OptimizedResume, ParsedResume, ResumeAnalysis
from util import load_yaml_config

# Tool mapping for YAML references
TOOLS_MAP = {
    "scrape_website_tool": ScrapeWebsiteTool(),
    "resume_reader_tool": read_docx_file,  # Using @tool decorator from resume_reader.py
    "job_automation_tool": job_automation,
}


# Define Flow State
class ResumeOptimizerState(BaseModel):
    """State model for the resume optimizer flow."""

    resume_path: str = ""
    job_url: str = ""
    output_dir: str = "output"
    output_path: str = ""
    tone: str = "neutral"
    must_keep_sections: list = Field(default_factory=list)

    # Intermediate results - using structured types
    parsed_resume_data: Optional[ParsedResume] = None
    job_description_data: Optional[JobDescription] = None
    analysis_data: Optional[ResumeAnalysis] = None
    optimized_resume_data: Optional[OptimizedResume] = None
    formatted_resume_text: Optional[str] = None
    submission_result: Optional[str] = None

    @field_validator("resume_path")
    @classmethod
    def validate_resume_path(cls, v: str) -> str:
        """Validate that resume file exists if path is provided."""
        if v and not Path(v).exists():
            raise ValueError(f"Resume file not found: {v}")
        return v


def create_agent_from_config(agent_name: str, agents_config: Dict[str, Any]) -> Agent:
    """Create an Agent instance from YAML configuration."""
    agent_config = agents_config[agent_name]
    tools = [
        TOOLS_MAP[tool_name]
        for tool_name in agent_config.get("tools", [])
        if tool_name in TOOLS_MAP
    ]

    # Handle LLM configuration from YAML
    agent_kwargs = {
        "role": agent_config["role"],
        "goal": agent_config["goal"],
        "backstory": agent_config["backstory"],
        "verbose": agent_config.get("verbose", True),
        "allow_delegation": agent_config.get("allow_delegation", False),
        "tools": tools or None,
    }

    # Add LLM if specified in YAML config
    if "llm" in agent_config:
        agent_kwargs["llm"] = LLM(model=agent_config["llm"])

    return Agent(**agent_kwargs)


def get_task_description(task_name: str, tasks_config: Dict[str, Any], **kwargs) -> str:
    """Get task description from YAML and format with variables."""
    description = tasks_config[task_name]["description"]
    return description.format(**kwargs) if kwargs else description


# Define Flow Class
class ResumeOptimizerFlow(Flow[ResumeOptimizerState]):
    """Flow for optimizing resumes for ATS compatibility."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.agents_config = load_yaml_config("config/agents.yaml")
        self.tasks_config = load_yaml_config("config/tasks.yaml")

        # Initialize agents from YAML
        agent_mapping = {
            "resume_parser": "parser_agent",
            "job_fetcher": "fetcher_agent",
            "resume_analyzer": "analyzer_agent",
            "resume_optimizer": "optimizer_agent",
            "resume_generator": "generator_agent",
            "job_submitter": "submitter_agent",
        }
        for yaml_name, attr_name in agent_mapping.items():
            setattr(
                self,
                attr_name,
                create_agent_from_config(yaml_name, self.agents_config),
            )

    def _run_agent_task(
        self,
        agent: Agent,
        task_name: str,
        state_key: str,
        response_format: Optional[type[BaseModel]] = None,
        **task_kwargs,
    ) -> Any:
        """Common pattern for running agent tasks and storing results with optional structured output."""
        try:
            task_description = get_task_description(
                task_name, self.tasks_config, **task_kwargs
            )

            # Use async kickoff with optional structured output
            if response_format:
                result = agent.kickoff(
                    task_description, response_format=response_format
                )
                # Store structured data
                if hasattr(result, "pydantic") and result.pydantic is not None:
                    if isinstance(result.pydantic, response_format):
                        setattr(self.state, state_key, result.pydantic)
                        return result.pydantic
                    else:
                        raise ValueError(
                            f"Expected {response_format.__name__}, got {type(result.pydantic).__name__}"
                        )
                else:
                    # Fallback to raw if structured output not available
                    error_msg = (
                        f"Structured output failed for task '{task_name}'. "
                        f"Expected {response_format.__name__} but got raw output."
                    )
                    print(f"⚠️ {error_msg}")
                    raise RuntimeError(error_msg)
            else:
                # For non-structured outputs (like formatted text)
                result = agent.kickoff(task_description)
                result_data = result.raw if hasattr(result, "raw") else str(result)
                setattr(self.state, state_key, result_data)
                return result_data
        except Exception as e:
            error_msg = f"Error executing task '{task_name}': {str(e)}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg) from e

    @start()
    def parse_resume(self) -> None:
        """Parse the DOCX resume file and extract structured data."""
        print(f"Parsing resume: {self.state.resume_path}")
        self._run_agent_task(
            self.parser_agent,
            "parse_resume_task",
            "parsed_resume_data",
            response_format=ParsedResume,
            resume_path=self.state.resume_path,
        )
        with open("parsed_resume.json", "w") as f:
            json.dump(self.state.parsed_resume_data.model_dump(), f, indent=4)

    @start()
    def fetch_job_description(self) -> None:
        """Fetch and extract job description from URL."""
        print(f"Fetching job description: {self.state.job_url}")
        self._run_agent_task(
            self.fetcher_agent,
            "fetch_job_description_task",
            "job_description_data",
            response_format=JobDescription,
            job_url=self.state.job_url,
        )

    @listen(and_(parse_resume, fetch_job_description))
    def analyze_resume(self) -> None:
        """Analyze resume against job description."""
        print("Analyzing resume against job description...")
        # Convert structured data to dict for task description formatting
        resume_data_str = (
            self.state.parsed_resume_data.model_dump_json()
            if self.state.parsed_resume_data
            and isinstance(self.state.parsed_resume_data, BaseModel)
            else "{}"
        )
        job_data_str = (
            self.state.job_description_data.model_dump_json()
            if self.state.job_description_data
            and isinstance(self.state.job_description_data, BaseModel)
            else "{}"
        )

        self._run_agent_task(
            self.analyzer_agent,
            "analyze_resume_task",
            "analysis_data",
            response_format=ResumeAnalysis,
            resume_data=resume_data_str,
            job_data=job_data_str,
        )

    @listen(analyze_resume)
    def optimize_resume(self) -> None:
        """Optimize resume content for ATS."""
        print("Optimizing resume for ATS...")
        # Convert structured data to dict for task description formatting
        # Check if analysis_data is a Pydantic model before calling model_dump_json
        if not isinstance(self.state.analysis_data, BaseModel):
            raise ValueError(
                f"analysis_data is not a valid ResumeAnalysis model. "
                f"Got type: {type(self.state.analysis_data)}, value: {self.state.analysis_data}"
            )

        analysis_str = (
            self.state.analysis_data.model_dump_json()
            if self.state.analysis_data
            else "{}"
        )
        resume_data_str = (
            self.state.parsed_resume_data.model_dump_json()
            if self.state.parsed_resume_data
            and isinstance(self.state.parsed_resume_data, BaseModel)
            else "{}"
        )
        job_data_str = (
            self.state.job_description_data.model_dump_json()
            if self.state.job_description_data
            and isinstance(self.state.job_description_data, BaseModel)
            else "{}"
        )

        self._run_agent_task(
            self.optimizer_agent,
            "optimize_resume_task",
            "optimized_resume_data",
            response_format=OptimizedResume,
            analysis=analysis_str,
            resume_data=resume_data_str,
            job_data=job_data_str,
            tone=self.state.tone,
            must_keep_sections=self.state.must_keep_sections,
        )

    @listen(optimize_resume)
    def generate_text_resume(self) -> None:
        """Generate the optimized resume as a text file."""
        print("Generating formatted resume text...")
        # Convert optimized data to JSON string for task description
        optimized_data_str = (
            self.state.optimized_resume_data.model_dump_json()
            if self.state.optimized_resume_data
            and isinstance(self.state.optimized_resume_data, BaseModel)
            else "{}"
        )

        formatted_text = self._run_agent_task(
            self.generator_agent,
            "generate_text_resume_task",
            "formatted_resume_text",
            response_format=None,  # This task returns plain text, not structured
            optimized_data=optimized_data_str,
        )

        # Save to file - ensure output directory exists
        output_path = Path(self.state.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(formatted_text, encoding="utf-8")
        print(f"\n✓ Optimized resume saved to: {self.state.output_path}")

    @listen(generate_text_resume)
    def submit_job_application(self) -> None:
        print(f"Submitting job application to {self.state.job_url}")
        # Get the formatted resume text
        resume_text = (
            self.state.formatted_resume_text if self.state.formatted_resume_text else ""
        )

        if not resume_text:
            print(
                f"⚠️ No resume text available. Skipping job application submission to {self.state.job_url}"
            )
            return

        self._run_agent_task(
            self.submitter_agent,
            "submit_job_application_task",
            "submission_result",
            response_format=None,  # This task returns a status message, not structured
            application_url=self.state.job_url,
            profile=self.state.parsed_resume_data.model_dump_json(),
            resume_text=resume_text,
        )
