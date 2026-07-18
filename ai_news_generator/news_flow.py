#!/usr/bin/env python
import os
from typing import Optional
from pydantic import BaseModel, Field
from crewai.flow.flow import Flow, listen, start
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

load_dotenv()

class ResearchReport(BaseModel):
    """Model for research report output"""
    executive_summary: str = Field(description="Executive summary of key findings")
    analysis: str = Field(description="Comprehensive analysis of current trends and developments")
    facts_and_statistics: str = Field(description="List of verified facts and statistics")
    citations: list[str] = Field(description="All citations and links to original sources", default=[])
    main_themes: str = Field(description="Clear categorization of main themes and patterns")

class BlogPost(BaseModel):
    """Model for blog post output"""
    title: str = Field(description="Blog post title")
    content: str = Field(description="Full blog post content in markdown format")
    word_count: int = Field(description="Approximate word count", default=0)

class NewsFlowState(BaseModel):
    """State management for the AI News Generation Flow"""
    topic: str = Field(description="The topic to research and write about")
    temperature: float = Field(description="LLM temperature setting", default=0.7)
    research_report: Optional[ResearchReport] = None
    final_blog_post: Optional[BlogPost] = None
    
class AINewsGeneratorFlow(Flow[NewsFlowState]):
    """
    CrewAI Flow for AI News Generation using agentic workflow.
    
    This flow implements a structured, event-driven approach to:
    1. Research comprehensive information on a given topic
    2. Transform research findings into engaging blog posts
    3. Maintain state and provide better error handling
    """
    
    def __init__(self, state: Optional[NewsFlowState] = None):
        super().__init__(state)
        self._setup_llm()
        self._setup_tools()
    
    def _setup_llm(self):
        """Initialize the LLM with proper configuration"""
        self.llm = LLM(
            model="command-r",
            temperature=self.state.temperature if self.state else 0.7
        )
    
    def _setup_tools(self):
        """Initialize research tools"""
        self.search_tool = SerperDevTool(n_results=10)
    
    @start()
    def conduct_research(self):
        """
        Initial flow step: Conduct comprehensive research on the topic
        """
        print(f"🔍 Starting research phase for topic: {self.state.topic}")
        
        # Create Senior Research Analyst Agent
        senior_research_analyst = Agent(
            role="Senior Research Analyst",
            goal=f"Research, analyze, and synthesize comprehensive information on {self.state.topic} from reliable web sources",
            backstory="You're an expert research analyst with advanced web research skills. "
                    "You excel at finding, analyzing, and synthesizing information from "
                    "across the internet using search tools. You're skilled at "
                    "distinguishing reliable sources from unreliable ones, "
                    "fact-checking, cross-referencing information, and "
                    "identifying key patterns and insights. You provide "
                    "well-organized research briefs with proper citations "
                    "and source verification. Your analysis includes both "
                    "raw data and interpreted insights, making complex "
                    "information accessible and actionable.",
            allow_delegation=False,
            verbose=True,
            tools=[self.search_tool],
            llm=self.llm
        )
        
        # Create Research Task
        research_task = Task(
            description=f"""
                Conduct comprehensive research on {self.state.topic} including:
                1. Recent developments and news
                2. Key industry trends and innovations  
                3. Expert opinions and analyses
                4. Statistical data and market insights
                5. Evaluate source credibility and fact-check all information
                6. Organize findings into a structured research brief
                7. Include all relevant citations and sources
            """,
            expected_output="""A detailed research report containing:
                - Executive summary of key findings
                - Comprehensive analysis of current trends and developments
                - List of verified facts and statistics
                - All citations and links to original sources
                - Clear categorization of main themes and patterns
                Please format with clear sections and bullet points for easy reference.""",
            agent=senior_research_analyst,
            output_pydantic=ResearchReport
        )
        
        # Execute research task
        research_crew = Crew(
            agents=[senior_research_analyst],
            tasks=[research_task],
            verbose=True
        )
        
        result = research_crew.kickoff()
        
        # Store research results in state
        self.state.research_report = result.pydantic
        
        print(f"✅ Research phase completed for: {self.state.topic}")
        return result
    
    @listen(conduct_research)
    def generate_content(self, research_result):
        """
        Second flow step: Transform research into engaging blog post
        """
        print(f"✍️ Starting content generation phase for topic: {self.state.topic}")
        
        # Create Content Writer Agent
        content_writer = Agent(
            role="Content Writer",
            goal="Transform research findings into engaging blog posts while maintaining accuracy",
            backstory="You're a skilled content writer specialized in creating "
                    "engaging, accessible content from technical research. "
                    "You work closely with the Senior Research Analyst and excel at maintaining the perfect "
                    "balance between informative and entertaining writing, "
                    "while ensuring all facts and citations from the research "
                    "are properly incorporated. You have a talent for making "
                    "complex topics approachable without oversimplifying them.",
            allow_delegation=False,
            verbose=True,
            llm=self.llm
        )
        
        # Create Writing Task
        writing_task = Task(
            description=f"""
                Using the research brief provided, create an engaging blog post about {self.state.topic} that:
                1. Transforms technical information into accessible content
                2. Maintains all factual accuracy and citations from the research
                3. Includes:
                    - Attention-grabbing introduction
                    - Well-structured body sections with clear headings
                    - Compelling conclusion
                4. Preserves all source citations in [Source: URL] format
                5. Includes a References section at the end
                6. Uses proper markdown formatting
            """,
            expected_output="""A polished blog post in markdown format that:
                - Engages readers while maintaining accuracy
                - Contains properly structured sections
                - Includes inline citations hyperlinked to the original source URL
                - Presents information in an accessible yet informative way
                - Follows proper markdown formatting, use H1 for the title and H3 for the sub-sections
                - Has an approximate word count""",
            agent=content_writer,
            context=[research_result],
            output_pydantic=BlogPost
        )
        
        # Execute writing task
        writing_crew = Crew(
            agents=[content_writer],
            tasks=[writing_task],
            verbose=True
        )
        
        result = writing_crew.kickoff()
        
        # Store blog post results in state
        self.state.final_blog_post = result.pydantic
        
        print(f"✅ Content generation completed for: {self.state.topic}")
        return result
    
    @listen(generate_content)
    def finalize_output(self, content_result):
        """
        Final flow step: Prepare and validate final output
        """
        print(f"🏁 Finalizing output for topic: {self.state.topic}")
        
        # Validate that we have all required components
        if not self.state.research_report:
            raise ValueError("Research report not found in state")
        
        if not self.state.final_blog_post:
            raise ValueError("Final blog post not found in state")
        
        # Calculate word count if not already done
        if self.state.final_blog_post.word_count == 0:
            word_count = len(self.state.final_blog_post.content.split())
            self.state.final_blog_post.word_count = word_count
        
        print(f"✅ Flow completed successfully!")
        print(f"📊 Generated {self.state.final_blog_post.word_count} word blog post")
        print(f"📚 Research included {len(self.state.research_report.citations)} citations")
        
        return {
            "blog_post": self.state.final_blog_post.content,
            "research_summary": self.state.research_report.executive_summary,
            "word_count": self.state.final_blog_post.word_count,
            "citations_count": len(self.state.research_report.citations)
        }
    
    def get_blog_content(self) -> str:
        """
        Convenience method to get the final blog post content
        """
        if self.state.final_blog_post:
            return self.state.final_blog_post.content
        return ""
    
    def get_research_summary(self) -> str:
        """
        Convenience method to get research summary
        """
        if self.state.research_report:
            return self.state.research_report.executive_summary
        return ""


def create_news_flow(topic: str, temperature: float = 0.7) -> AINewsGeneratorFlow:
    """
    Factory function to create a new AI News Generator Flow
    
    Args:
        topic (str): The topic to research and write about
        temperature (float): LLM temperature setting
    
    Returns:
        AINewsGeneratorFlow: Configured flow instance
    """
    initial_state = NewsFlowState(
        topic=topic,
        temperature=temperature
    )
    
    return AINewsGeneratorFlow(state=initial_state)


def kickoff_news_flow(topic: str, temperature: float = 0.7) -> dict:
    """
    Convenience function to run the complete AI news generation flow
    
    Args:
        topic (str): The topic to research and write about  
        temperature (float): LLM temperature setting
    
    Returns:
        dict: Final results including blog post and metadata
    """
    flow = create_news_flow(topic, temperature)
    result = flow.kickoff()
    return result


if __name__ == "__main__":
    # Example usage
    result = kickoff_news_flow("Latest developments in AI and Machine Learning")
    print("\n" + "="*50)
    print("FINAL BLOG POST:")
    print("="*50)
    print(result["blog_post"])