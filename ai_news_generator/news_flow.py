import os
from typing import Any, Dict
from pydantic import BaseModel
from crewai import Agent, Task, Crew, LLM
from crewai.flow.flow import Flow, listen, start
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

load_dotenv()


class ResearchState(BaseModel):
    """State model for research findings"""
    topic: str
    research_brief: str
    sources: list[str] = []
    key_findings: list[str] = []


class NewsGeneratorFlow(Flow[ResearchState]):
    """
    CrewAI Flow for generating AI news content.
    
    This flow orchestrates a two-phase process:
    1. Research Phase: Comprehensive research on the given topic
    2. Writing Phase: Transform research into engaging blog content
    """

    def __init__(self):
        super().__init__()
        self.llm = LLM(
            model="command-r",
            temperature=0.7
        )
        self.search_tool = SerperDevTool(n_results=10)

    def _create_research_agent(self) -> Agent:
        """Create the Senior Research Analyst agent"""
        return Agent(
            role="Senior Research Analyst",
            goal="Research, analyze, and synthesize comprehensive information from reliable web sources",
            backstory=(
                "You're an expert research analyst with advanced web research skills. "
                "You excel at finding, analyzing, and synthesizing information from "
                "across the internet using search tools. You're skilled at "
                "distinguishing reliable sources from unreliable ones, "
                "fact-checking, cross-referencing information, and "
                "identifying key patterns and insights. You provide "
                "well-organized research briefs with proper citations "
                "and source verification. Your analysis includes both "
                "raw data and interpreted insights, making complex "
                "information accessible and actionable."
            ),
            allow_delegation=False,
            verbose=True,
            tools=[self.search_tool],
            llm=self.llm
        )

    def _create_content_writer_agent(self) -> Agent:
        """Create the Content Writer agent"""
        return Agent(
            role="Content Writer",
            goal="Transform research findings into engaging blog posts while maintaining accuracy",
            backstory=(
                "You're a skilled content writer specialized in creating "
                "engaging, accessible content from technical research. "
                "You work closely with the Senior Research Analyst and excel at maintaining the perfect "
                "balance between informative and entertaining writing, "
                "while ensuring all facts and citations from the research "
                "are properly incorporated. You have a talent for making "
                "complex topics approachable without oversimplifying them."
            ),
            allow_delegation=False,
            verbose=True,
            llm=self.llm
        )

    @start()
    def research_phase(self) -> str:
        """
        Initial phase: Conduct comprehensive research on the topic
        """
        research_agent = self._create_research_agent()
        
        research_task = Task(
            description=f"""
                1. Conduct comprehensive research on {self.state.topic} including:
                    - Recent developments and news
                    - Key industry trends and innovations
                    - Expert opinions and analyses
                    - Statistical data and market insights
                2. Evaluate source credibility and fact-check all information
                3. Organize findings into a structured research brief
                4. Include all relevant citations and sources
            """,
            expected_output="""A detailed research report containing:
                - Executive summary of key findings
                - Comprehensive analysis of current trends and developments
                - List of verified facts and statistics
                - All citations and links to original sources
                - Clear categorization of main themes and patterns
                Please format with clear sections and bullet points for easy reference.""",
            agent=research_agent
        )

        # Create a single-agent crew for research
        research_crew = Crew(
            agents=[research_agent],
            tasks=[research_task],
            verbose=True
        )

        # Execute research and return results
        research_result = research_crew.kickoff(inputs={"topic": self.state.topic})
        
        # Update state with research findings
        self.state.research_brief = str(research_result)
        
        return str(research_result)

    @listen(research_phase)
    def writing_phase(self, research_results: str) -> str:
        """
        Second phase: Transform research into engaging blog content
        """
        content_writer = self._create_content_writer_agent()
        
        writing_task = Task(
            description=f"""
                Using the research brief provided: {research_results}
                
                Create an engaging blog post that:
                1. Transforms technical information into accessible content
                2. Maintains all factual accuracy and citations from the research
                3. Includes:
                    - Attention-grabbing introduction
                    - Well-structured body sections with clear headings
                    - Compelling conclusion
                4. Preserves all source citations in [Source: URL] format
                5. Includes a References section at the end
            """,
            expected_output="""A polished blog post in markdown format that:
                - Engages readers while maintaining accuracy
                - Contains properly structured sections
                - Includes Inline citations hyperlinked to the original source url
                - Presents information in an accessible yet informative way
                - Follows proper markdown formatting, use H1 for the title and H3 for the sub-sections""",
            agent=content_writer
        )

        # Create a single-agent crew for writing
        writing_crew = Crew(
            agents=[content_writer],
            tasks=[writing_task],
            verbose=True
        )

        # Execute writing phase
        writing_result = writing_crew.kickoff(inputs={
            "topic": self.state.topic,
            "research_results": research_results
        })

        return str(writing_result)

    def kickoff(self, inputs: Dict[str, Any]) -> Any:
        """
        Initialize and run the flow with the given topic
        """
        # Initialize state with the topic
        if not hasattr(self, 'state') or self.state is None:
            self.state = ResearchState(topic=inputs.get("topic", ""))
        else:
            self.state.topic = inputs.get("topic", "")
        
        # Start the flow execution
        return super().kickoff(inputs=inputs)


def generate_content_with_flow(topic: str) -> str:
    """
    Convenience function to generate content using the NewsGeneratorFlow
    
    Args:
        topic (str): The topic to research and write about
    
    Returns:
        str: The generated blog post content
    """
    flow = NewsGeneratorFlow()
    result = flow.kickoff(inputs={"topic": topic})
    return str(result)