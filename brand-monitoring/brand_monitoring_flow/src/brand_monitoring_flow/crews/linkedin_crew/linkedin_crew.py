from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel, Field

class LinkedInWriterReport(BaseModel):
    post_title: str = Field(description="The title explaining how the brand was used in an individual post")
    post_link: str = Field(description="The link to the scraped content")
    content_lines: list[str] = Field(description="The bullet points within the scraped content that are relevant to the brand")

class LinkedInReport(BaseModel):   
    content: list[LinkedInWriterReport] = Field(description=("A list of extracted content with title, the post link, "
                                                              "and the bullet points within each unique post. "
                                                              "The size of the output list will be the same as the number of posts in the input data.")
                                                              )

llm = LLM(model="ollama/deepseek-r1")


@CrewBase
class LinkedInCrew:
    """LinkedIn Analysis Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def analysis_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["analysis_agent"],
            llm=llm,
        )
        
    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["analysis_task"],
        )
    
    @agent
    def writer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["writer_agent"],
            llm=llm,
        )

    @task
    def write_report_task(self) -> Task:
        return Task(
            config=self.tasks_config["write_report_task"],
            output_pydantic=LinkedInReport,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the LinkedIn Analysis Crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
