import os
import streamlit as st
from news_flow import create_news_flow, AINewsGeneratorFlow
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Streamlit page config
st.set_page_config(
    page_title="AI News Generator with CrewAI Flows", 
    page_icon="📰", 
    layout="wide"
)

# Title and description
st.title("🤖 AI News Generator - Powered by CrewAI Flows")
st.markdown("""
Generate comprehensive blog posts about any topic using AI agents in a structured, event-driven workflow.
This implementation uses **CrewAI Flows** for better state management and agentic coordination.
""")

# Sidebar
with st.sidebar:
    st.header("Content Settings")
    
    # Make the text input take up more space
    topic = st.text_area(
        "Enter your topic",
        height=100,
        placeholder="Enter the topic you want to generate content about..."
    )
    
    # Add more sidebar controls
    st.markdown("### Advanced Settings")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, help="Higher values make output more creative")
    
    # Add some spacing
    st.markdown("---")
    
    # Make the generate button more prominent in the sidebar
    generate_button = st.button("Generate Content", type="primary", use_container_width=True)
    
    # Add some helpful information
    with st.expander("ℹ️ How CrewAI Flows Work"):
        st.markdown("""
        **CrewAI Flows** provide a structured approach to AI workflows:
        
        1. **Research Phase**: AI researcher gathers comprehensive information
        2. **Content Generation**: AI writer creates engaging blog post
        3. **State Management**: Flow tracks progress and results
        4. **Event-Driven**: Each phase triggers the next automatically
        
        **Benefits:**
        - Better error handling
        - State persistence
        - Modular design
        - Enhanced debugging
        """)
    
    with st.expander("🚀 Usage Instructions"):
        st.markdown("""
        1. Enter your desired topic in the text area above
        2. Adjust the temperature if needed (higher = more creative)
        3. Click 'Generate Content' to start the flow
        4. Monitor progress through the flow phases
        5. Download the result as a markdown file
        """)

# Main content area
if generate_button and topic:
    # Create columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📄 Generated Content")
        content_placeholder = st.empty()
    
    with col2:
        st.markdown("### 📊 Flow Progress")
        progress_placeholder = st.empty()
        
        st.markdown("### 📋 Flow State")
        state_placeholder = st.empty()
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        with st.spinner('🔄 Initializing AI News Generation Flow...'):
            status_text.text("🔄 Creating flow instance...")
            progress_bar.progress(10)
            
            # Create flow instance
            news_flow = create_news_flow(topic, temperature)
            
            status_text.text("🔍 Phase 1: Research in progress...")
            progress_bar.progress(25)
            
            # Update progress display
            with progress_placeholder.container():
                st.markdown("**Current Phase:** 🔍 Research")
                st.markdown("**Status:** Gathering information...")
                
            # Execute flow (this will run all phases)
            result = news_flow.kickoff()
            
            status_text.text("✅ Flow completed successfully!")
            progress_bar.progress(100)
            
            # Update progress display
            with progress_placeholder.container():
                st.success("**Flow Completed Successfully!** ✅")
                st.markdown(f"**Word Count:** {result.get('word_count', 'N/A')}")
                st.markdown(f"**Citations:** {result.get('citations_count', 'N/A')}")
                
            # Update state display
            with state_placeholder.container():
                st.json({
                    "topic": topic,
                    "temperature": temperature,
                    "has_research": news_flow.state.research_report is not None,
                    "has_blog_post": news_flow.state.final_blog_post is not None,
                    "word_count": result.get('word_count', 0),
                    "citations_count": result.get('citations_count', 0)
                })
            
            # Display generated content
            with content_placeholder.container():
                blog_content = result.get('blog_post', '')
                if blog_content:
                    st.markdown(blog_content)
                    
                    # Add download button
                    st.download_button(
                        label="📥 Download Content",
                        data=blog_content,
                        file_name=f"{topic.lower().replace(' ', '_')}_article.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                    
                    # Add research summary if available
                    if result.get('research_summary'):
                        with st.expander("📚 Research Summary"):
                            st.markdown(result['research_summary'])
                else:
                    st.error("No content was generated. Please try again.")
                    
    except Exception as e:
        st.error(f"❌ An error occurred during flow execution: {str(e)}")
        
        # Show debugging information
        with st.expander("🔍 Debug Information"):
            st.code(str(e))
            st.markdown("**Possible solutions:**")
            st.markdown("- Check your API keys (COHERE_API_KEY, SERPER_API_KEY)")
            st.markdown("- Ensure you have a stable internet connection")
            st.markdown("- Try a different topic or adjust temperature")
            
elif generate_button and not topic:
    st.warning("⚠️ Please enter a topic before generating content.")

# Add flow visualization section
st.markdown("---")
st.markdown("## 🔀 Flow Architecture")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Flow Steps:
    1. **🔍 Research Phase**
       - Senior Research Analyst agent
       - Web search and analysis
       - Source verification
       
    2. **✍️ Content Generation**
       - Content Writer agent  
       - Transform research to blog
       - Maintain accuracy & citations
       
    3. **🏁 Finalization**
       - Validate outputs
       - Calculate metrics
       - Prepare final results
    """)

with col2:
    if st.button("📊 Visualize Flow Structure"):
        st.info("Flow visualization would show the event-driven architecture with @start, @listen decorators connecting the phases.")
        
        # You could add flow.plot() here if implemented
        st.code("""
        @start()
        def conduct_research():
            # Research phase
            
        @listen(conduct_research)  
        def generate_content():
            # Writing phase
            
        @listen(generate_content)
        def finalize_output():
            # Finalization phase
        """)

# Footer
st.markdown("---")
st.markdown("""
**Built with CrewAI Flows, Streamlit and powered by Cohere's Command R**

🔗 **GitHub Issue #168**: *Replace the current implementation with CrewAI flows to create an agentic workflow*

This implementation demonstrates the power of CrewAI Flows for creating structured, event-driven AI workflows 
with better state management, error handling, and modularity compared to traditional crew-based approaches.
""")