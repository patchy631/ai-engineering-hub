import os
from typing import Dict, Any
from crewai.flow.flow import Flow, start, listen
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NewsGeneratorState(BaseModel):
    """Structured state for the news generation flow"""
    topic: str = ""
    research_results: str = ""
    final_content: str = ""
    temperature: float = 0.7

class NewsGeneratorFlow(Flow[NewsGeneratorState]):
    """
    CrewAI Flow for generating AI news content.
    
    This flow orchestrates a two-phase process:
    1. Research phase: Comprehensive topic research
    2. Content writing phase: Transform research into engaging blog post
    """

    def __init__(self, topic: str, temperature: float = 0.7):
        """Initialize the flow with topic and configuration"""
        super().__init__()
        
        # Store configuration as instance variables
        self.topic = topic
        self.temperature = temperature
        self.research_results = ""
        self.final_content = ""
        
        # Initialize LLM
        self.llm = LLM(
            model="command-r",
            temperature=temperature
        )
        
        # Initialize search tool
        self.search_tool = SerperDevTool(n_results=10)

    @start()
    def research_topic(self) -> str:
        """
        Phase 1: Research the given topic comprehensively
        
        Returns:
            str: Research results
        """
        print(f"🔍 Starting research phase for topic: {self.topic}")
        
        # Create Senior Research Analyst agent
        senior_research_analyst = Agent(
            role="Senior Research Analyst",
            goal=f"Research, analyze, and synthesize comprehensive information on {self.topic} from reliable web sources",
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

        # Research Task
        research_task = Task(
            description=(f"""
                1. Conduct comprehensive research on {self.topic} including:
                    - Recent developments and news
                    - Key industry trends and innovations
                    - Expert opinions and analyses
                    - Statistical data and market insights
                2. Evaluate source credibility and fact-check all information
                3. Organize findings into a structured research brief
                4. Include all relevant citations and sources
            """),
            expected_output="""A detailed research report containing:
                - Executive summary of key findings
                - Comprehensive analysis of current trends and developments
                - List of verified facts and statistics
                - All citations and links to original sources
                - Clear categorization of main themes and patterns
                Please format with clear sections and bullet points for easy reference.""",
            agent=senior_research_analyst
        )

        # Create and execute research crew
        research_crew = Crew(
            agents=[senior_research_analyst],
            tasks=[research_task],
            verbose=True
        )

        research_results = research_crew.kickoff(inputs={"topic": self.topic})
        
        # Store research results
        self.research_results = str(research_results)
        
        print("✅ Research phase completed")
        return self.research_results

    @listen(research_topic)
    def write_content(self, research_results: str) -> str:
        """
        Phase 2: Transform research into engaging blog content
        
        Args:
            research_results: Output from research_topic method
            
        Returns:
            str: Final blog content
        """
        print("✍️ Starting content writing phase")
        
        # Create Content Writer agent
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

        # Writing Task
        writing_task = Task(
            description=(f"""
                Using the research brief provided, create an engaging blog post about {self.topic} that:
                1. Transforms technical information into accessible content
                2. Maintains all factual accuracy and citations from the research
                3. Includes:
                    - Attention-grabbing introduction
                    - Well-structured body sections with clear headings
                    - Compelling conclusion
                4. Preserves all source citations in [Source: URL] format
                5. Includes a References section at the end
            """),
            expected_output="""A polished blog post in markdown format that:
                - Engages readers while maintaining accuracy
                - Contains properly structured sections
                - Includes inline citations hyperlinked to the original source url
                - Presents information in an accessible yet informative way
                - Follows proper markdown formatting, use H1 for the title and H3 for the sub-sections""",
            agent=content_writer,
            context=[research_results] if isinstance(research_results, str) else []
        )

        # Create and execute writing crew
        writing_crew = Crew(
            agents=[content_writer],
            tasks=[writing_task],
            verbose=True
        )

        final_content = writing_crew.kickoff(inputs={
            "topic": self.topic,
            "research_results": research_results
        })
        
        # Store final content
        self.final_content = str(final_content)
        
        print("✅ Content writing phase completed")
        return self.final_content

    def get_final_content(self) -> str:
        """Get the final generated content"""
        return self.final_content

    def get_research_results(self) -> str:
        """Get the research results"""
        return self.research_results

def generate_news_content(topic: str, temperature: float = 0.7) -> Dict[str, Any]:
    """
    Generate news content using CrewAI Flow
    
    Args:
        topic: The topic to research and write about
        temperature: LLM temperature setting
        
    Returns:
        Dict containing research results and final content
    """
    print(f"🚀 Starting NewsGeneratorFlow for topic: {topic}")
    
    # Create and execute flow
    flow = NewsGeneratorFlow(topic=topic, temperature=temperature)
    result = flow.kickoff()
    
    return {
        "topic": topic,
        "research_results": flow.get_research_results(),
        "final_content": flow.get_final_content(),
        "flow_result": str(result)
    }

if __name__ == "__main__":
    """Example usage of the NewsGeneratorFlow"""
    
    # Example topic
    topic = "Latest developments in Large Language Models and AI"
    
    print("=" * 60)
    print("AI News Generator - CrewAI Flow Implementation")
    print("=" * 60)
    
    try:
        # Generate content using the flow
        result = generate_news_content(topic, temperature=0.7)
        
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        
        print(f"\n📝 Topic: {result['topic']}")
        print(f"\n🔍 Research Results Preview: {result['research_results'][:200]}...")
        print(f"\n✍️ Final Content Preview: {result['final_content'][:200]}...")
        
        # Save results to files
        with open("research_results.md", "w") as f:
            f.write(result['research_results'])
        
        with open("final_article.md", "w") as f:
            f.write(result['final_content'])
            
        print("\n💾 Results saved to:")
        print("  - research_results.md")
        print("  - final_article.md")
        
    except Exception as e:
        print(f"❌ Error: {e}")