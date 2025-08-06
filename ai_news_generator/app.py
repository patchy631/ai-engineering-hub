import os
import streamlit as st
from crewai import Agent, Task, Crew, LLM
from crewai.flow.flow import Flow, start, listen
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

# Load environment variables
load_dotenv()

# Define the Flow State Model
class NewsGenerationState(BaseModel):
    topic: str = ""
    temperature: float = 0.7
    research_report: Optional[str] = None
    final_article: Optional[str] = None
    error: Optional[str] = None

# Define the News Generation Flow
class NewsGenerationFlow(Flow[NewsGenerationState]):
    
    @start()
    def conduct_research(self):
        """Conduct comprehensive research on the given topic"""
        llm = LLM(
            model="command-r",
            temperature=self.state.temperature
        )
        
        search_tool = SerperDevTool(n_results=10)
        
        # Senior Research Analyst Agent
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
            tools=[search_tool],
            llm=llm
        )
        
        # Research Task
        research_task = Task(
            description=(f"""
                1. Conduct comprehensive research on {self.state.topic} including:
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
        
        try:
            research_result = research_crew.kickoff(inputs={"topic": self.state.topic})
            self.state.research_report = research_result.raw
            return self.state.research_report
        except Exception as e:
            self.state.error = f"Research failed: {str(e)}"
            return None
    
    @listen(conduct_research)
    def generate_content(self, research_report):
        """Generate engaging blog content based on research findings"""
        if not research_report or self.state.error:
            return None
            
        llm = LLM(
            model="command-r",
            temperature=self.state.temperature
        )
        
        # Content Writer Agent
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
            llm=llm
        )
        
        # Writing Task
        writing_task = Task(
            description=(f"""
                Using the research brief provided, create an engaging blog post about {self.state.topic} that:
                1. Transforms technical information into accessible content
                2. Maintains all factual accuracy and citations from the research
                3. Includes:
                    - Attention-grabbing introduction
                    - Well-structured body sections with clear headings
                    - Compelling conclusion
                4. Preserves all source citations in [Source: URL] format
                5. Includes a References section at the end
                
                Research Report to use: {self.state.research_report}
            """),
            expected_output="""A polished blog post in markdown format that:
                - Engages readers while maintaining accuracy
                - Contains properly structured sections
                - Includes Inline citations hyperlinked to the original source url
                - Presents information in an accessible yet informative way
                - Follows proper markdown formatting, use H1 for the title and H3 for the sub-sections""",
            agent=content_writer
        )
        
        # Create and execute writing crew
        writing_crew = Crew(
            agents=[content_writer],
            tasks=[writing_task],
            verbose=True
        )
        
        try:
            writing_result = writing_crew.kickoff(inputs={
                "topic": self.state.topic,
                "research_report": self.state.research_report
            })
            self.state.final_article = writing_result.raw
            return self.state.final_article
        except Exception as e:
            self.state.error = f"Content generation failed: {str(e)}"
            return None

# Streamlit page config
st.set_page_config(page_title="AI News Generator", page_icon="📰", layout="wide")

# Title and description
st.title("🤖 AI News Generator - CrewAI Flows Edition")
st.markdown("Generate comprehensive blog posts about any topic using **CrewAI Flows** for enhanced agentic workflow orchestration.")
st.info("✨ **New!** Now powered by CrewAI Flows - Experience improved workflow management, better error handling, and enhanced agent coordination.")

# Sidebar
with st.sidebar:
    st.header("Content Settings")
    
    # Make the text input take up more space
    topic = st.text_area(
        "Enter your topic",
        height=100,
        placeholder="Enter the topic you want to generate content about..."
    )
    
    # Add more sidebar controls if needed
    st.markdown("### Advanced Settings")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    
    # Add some spacing
    st.markdown("---")
    
    # Make the generate button more prominent in the sidebar
    generate_button = st.button("Generate Content", type="primary", use_container_width=True)
    
    # Add some helpful information
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        1. Enter your desired topic in the text area above
        2. Adjust the temperature if needed (higher = more creative)
        3. Click 'Generate Content' to start
        4. Wait for the AI to generate your article
        5. Download the result as a markdown file
        """)

def generate_content_with_flow(topic, temperature=0.7):
    """Generate content using CrewAI Flow"""
    try:
        # Create flow instance with initial state
        flow = NewsGenerationFlow()
        flow.state.topic = topic
        flow.state.temperature = temperature
        
        # Execute the flow
        result = flow.kickoff()
        
        if flow.state.error:
            raise Exception(flow.state.error)
            
        return flow.state.final_article
    except Exception as e:
        raise Exception(f"Flow execution failed: {str(e)}")

# Main content area
if generate_button and topic.strip():
    with st.spinner('Generating content using CrewAI Flow... This may take a moment.'):
        try:
            # Generate content using the new flow-based approach
            result = generate_content_with_flow(topic, temperature)
            
            if result:
                st.markdown("### Generated Content")
                st.markdown(result)
                
                # Add download button
                st.download_button(
                    label="Download Content",
                    data=result,
                    file_name=f"{topic.lower().replace(' ', '_')}_article.md",
                    mime="text/markdown"
                )
                
                # Add flow visualization option
                with st.expander("🔍 View Flow Execution Details"):
                    st.info("This content was generated using CrewAI Flows with the following steps:")
                    st.markdown("""
                    1. **Research Phase**: Senior Research Analyst conducted comprehensive web research
                    2. **Content Generation Phase**: Content Writer transformed research into engaging article
                    3. **Flow Orchestration**: CrewAI Flow managed the sequential execution and state management
                    """)
            else:
                st.error("No content was generated. Please try again.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Please check your API keys (SERPER_API_KEY and COHERE_API_KEY) and try again.")

elif generate_button and not topic.strip():
    st.warning("Please enter a topic before generating content.")

# Footer
st.markdown("---")
st.markdown("Built with CrewAI **Flows**, Streamlit and powered by Cohere's Command R7B")
st.markdown("*Now using CrewAI Flows for enhanced agentic workflow orchestration*")