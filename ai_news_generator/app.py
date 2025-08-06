import os
import streamlit as st
from crewai import Agent, Task, Crew, LLM
from crewai.flow.flow import Flow, listen, start
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional

# Load environment variables
load_dotenv()

# Streamlit page config
st.set_page_config(page_title="AI News Generator", page_icon="📰", layout="wide")

# Title and description
st.title("🤖 AI News Generator with CrewAI Flows")
st.markdown("Generate comprehensive blog posts using **CrewAI Flows** - an event-driven, agentic workflow powered by Cohere's Command R7B")

# Add Flow benefits section
st.markdown("### 🌊 Flow Benefits")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**🔄 Event-Driven**\nTasks execute based on previous results")
with col2:
    st.markdown("**🎯 State Management**\nStructured data flow between agents")
with col3:
    st.markdown("**⚡ Optimized**\nBetter control and orchestration")

st.markdown("---")

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
    
    # Add Flow visualization
    st.markdown("### Flow Visualization")
    st.info("This application uses CrewAI Flows for structured, event-driven content generation:\n1. **Research Phase**: AI agent researches the topic\n2. **Writing Phase**: AI agent transforms research into engaging content")
    
    # Add some helpful information
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        1. Enter your desired topic in the text area above
        2. Adjust the temperature if needed (higher = more creative)
        3. Click 'Generate Content' to start
        4. Wait for the AI to generate your article
        5. Download the result as a markdown file
        """)

class NewsGenerationState(BaseModel):
    topic: str = ""
    research_report: str = ""
    final_article: str = ""
    temperature: float = 0.7

class AINewsGeneratorFlow(Flow[NewsGenerationState]):
    
    @start()
    def research_phase(self):
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
            description=("""
                1. Conduct comprehensive research on {topic} including:
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
        
        # Create Research Crew
        research_crew = Crew(
            agents=[senior_research_analyst],
            tasks=[research_task],
            verbose=True
        )
        
        # Execute research and store result
        research_result = research_crew.kickoff(inputs={"topic": self.state.topic})
        self.state.research_report = research_result.raw
        
        return research_result.raw
    
    @listen(research_phase)
    def content_writing_phase(self, research_report: str):
        """Transform research findings into engaging blog content"""
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
            description=("""
                Using the research brief provided, create an engaging blog post that:
                1. Transforms technical information into accessible content
                2. Maintains all factual accuracy and citations from the research
                3. Includes:
                    - Attention-grabbing introduction
                    - Well-structured body sections with clear headings
                    - Compelling conclusion
                4. Preserves all source citations in [Source: URL] format
                5. Includes a References section at the end
                
                Research Brief: {research_report}
            """),
            expected_output="""A polished blog post in markdown format that:
                - Engages readers while maintaining accuracy
                - Contains properly structured sections
                - Includes Inline citations hyperlinked to the original source url
                - Presents information in an accessible yet informative way
                - Follows proper markdown formatting, use H1 for the title and H3 for the sub-sections""",
            agent=content_writer
        )
        
        # Create Writing Crew
        writing_crew = Crew(
            agents=[content_writer],
            tasks=[writing_task],
            verbose=True
        )
        
        # Execute writing and store result
        writing_result = writing_crew.kickoff(inputs={
            "research_report": research_report,
            "topic": self.state.topic
        })
        self.state.final_article = writing_result.raw
        
        return writing_result.raw

def generate_content(topic, temperature=0.7):
    """Generate content using the AI News Generator Flow"""
    flow = AINewsGeneratorFlow()
    flow.state.topic = topic
    flow.state.temperature = temperature
    
    result = flow.kickoff()
    return result

# Main content area
if generate_button and topic:
    with st.spinner('Generating content using CrewAI Flows... This may take a moment.'):
        try:
            result = generate_content(topic, temperature)
            st.markdown("### Generated Content")
            st.markdown(result)
            
            # Add download button
            st.download_button(
                label="Download Content",
                data=result,
                file_name=f"{topic.lower().replace(' ', '_')}_article.md",
                mime="text/markdown"
            )
            
            # Show flow execution info
            with st.expander("Flow Execution Details"):
                st.success("✅ Research Phase: Completed")
                st.success("✅ Content Writing Phase: Completed")
                st.info("Flow executed successfully using CrewAI Flows with structured state management and event-driven task chaining.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
elif generate_button and not topic:
    st.warning("Please enter a topic before generating content.")

# Footer
st.markdown("---")
st.markdown("Built with **CrewAI Flows**, Streamlit and powered by Cohere's Command R7B")