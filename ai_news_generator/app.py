import os
import streamlit as st
from main import generate_news_content
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Streamlit page config
st.set_page_config(page_title="AI News Generator", page_icon="📰", layout="wide")

# Title and description
st.title("🤖 AI News Generator, powered by CrewAI Flows and Cohere's Command R7B")
st.markdown("Generate comprehensive blog posts about any topic using AI agents with CrewAI Flows for better workflow orchestration.")

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
        3. Click 'Generate Content' to start the CrewAI Flow
        4. The flow will execute in two phases:
           - 🔍 Research Phase: Comprehensive topic research
           - ✍️ Writing Phase: Transform research into blog content
        5. Download the result as a markdown file
        """)
        
    with st.expander("🔄 About CrewAI Flows"):
        st.markdown("""
        This application now uses **CrewAI Flows** for better workflow orchestration:
        - **Event-driven**: Each phase triggers the next automatically
        - **State management**: Seamlessly passes data between phases
        - **Modular**: Easy to extend with additional workflow steps
        - **Reliable**: Better error handling and workflow control
        """)

def generate_content(topic, temperature=0.7):
    """Generate content using the new CrewAI Flow implementation"""
    return generate_news_content(topic, temperature)

# Main content area
if generate_button:
    if not topic.strip():
        st.warning("Please enter a topic to generate content.")
    else:
        with st.spinner('🚀 Executing CrewAI Flow... This may take a moment.'):
            try:
                # Generate content using CrewAI Flow
                result = generate_content(topic, temperature)
                
                # Display results
                st.success("✅ Content generation completed!")
                
                # Show phase results in tabs
                tab1, tab2 = st.tabs(["📰 Final Article", "🔍 Research Results"])
                
                with tab1:
                    st.markdown("### Generated Article")
                    st.markdown(result['final_content'])
                    
                    # Download button for final content
                    st.download_button(
                        label="📥 Download Article",
                        data=result['final_content'],
                        file_name=f"{topic.lower().replace(' ', '_')}_article.md",
                        mime="text/markdown",
                        type="primary"
                    )
                
                with tab2:
                    st.markdown("### Research Results")
                    st.markdown(result['research_results'])
                    
                    # Download button for research results
                    st.download_button(
                        label="📥 Download Research",
                        data=result['research_results'],
                        file_name=f"{topic.lower().replace(' ', '_')}_research.md",
                        mime="text/markdown"
                    )
                    
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.info("Please check your API keys and internet connection.")

# Footer
st.markdown("---")
st.markdown("Built with CrewAI Flows, Streamlit and powered by Cohere's Command R7B")

# Add flow information
with st.expander("🔄 Flow Execution Details"):
    st.markdown("""
    **CrewAI Flow Phases:**
    1. **🔍 Research Phase** - Senior Research Analyst gathers comprehensive information
    2. **✍️ Content Writing Phase** - Content Writer transforms research into engaging blog post
    
    **Flow Benefits:**
    - Event-driven execution with @start and @listen decorators
    - State management for seamless data passing between phases
    - Modular architecture for easy extension
    - Better error handling and workflow control
    """)