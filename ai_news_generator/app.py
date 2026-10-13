import os
import streamlit as st
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool
from crewai.flow.flow import Flow, listen, start
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Streamlit page config
st.set_page_config(page_title="AI News Generator", page_icon="📰", layout="wide")

# Title and description
st.title("🤖 AI News Generator, powered by CrewAI and Cohere's Command R7B")
st.markdown("Generate comprehensive blog posts about any topic using AI agents.")

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

class NewsGeneratorFlow(Flow):
    def __init__(self, topic):
        super().__init__()
        self.topic = topic
        self.llm = LLM(
            model="command-r",
            temperature=0.7
        )
        self.search_tool = SerperDevTool(n_results=10)

    @start()
    def research_phase(self):
        """Phase 1: Research and analyze information on the given topic"""
        # Senior Research Analyst Agent
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

        research_result = research_crew.kickoff(inputs={"topic": self.topic})
        return research_result

    @listen(research_phase)
    def writing_phase(self, research_output):
        """Phase 2: Transform research into engaging blog post"""
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
            llm=self.llm
        )

        # Writing Task
        writing_task = Task(
            description=(f"""
                Using the research brief provided about {self.topic}, create an engaging blog post that:
                1. Transforms technical information into accessible content
                2. Maintains all factual accuracy and citations from the research
                3. Includes:
                    - Attention-grabbing introduction
                    - Well-structured body sections with clear headings
                    - Compelling conclusion
                4. Preserves all source citations in [Source: URL] format
                5. Includes a References section at the end
                
                Research Brief: {research_output}
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

        writing_result = writing_crew.kickoff(inputs={
            "topic": self.topic,
            "research_output": research_output
        })
        return writing_result

def generate_content(topic):
    """Generate content using CrewAI Flow"""
    flow = NewsGeneratorFlow(topic)
    return flow.kickoff()

# Main content area
if generate_button:
    with st.spinner('Generating content... This may take a moment.'):
        try:
            result = generate_content(topic)
            st.markdown("### Generated Content")
            st.markdown(result)
            
            # Add download button
            st.download_button(
                label="Download Content",
                data=result.raw,
                file_name=f"{topic.lower().replace(' ', '_')}_article.md",
                mime="text/markdown"
            )
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Built with CrewAI, Streamlit and powered by Cohere's Command R7B")