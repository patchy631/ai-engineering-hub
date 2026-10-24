import os
import sys
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from ai_news_flow.main import NewsGeneratorFlow
except ImportError as e:
    st.error(f"Failed to import NewsGeneratorFlow: {e}")
    st.stop()

# Load environment variables
load_dotenv()

# Streamlit page config
st.set_page_config(
    page_title="AI News Generator with CrewAI Flow", 
    page_icon="📰", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("🤖 AI News Generator")
st.markdown("**Powered by CrewAI Flows, Cohere's Command R7B, and Multi-Agent Workflow**")
st.markdown("Generate comprehensive, well-researched blog posts using our advanced multi-phase AI workflow.")

# Sidebar
with st.sidebar:
    st.header("🎛️ Content Settings")
    
    # Topic input
    topic = st.text_area(
        "📝 Enter your topic",
        height=120,
        placeholder="e.g., 'Latest developments in artificial intelligence', 'Climate change impacts in 2025', 'Cryptocurrency market trends'...",
        help="Be specific about what you want to research and write about"
    )
    
    # Advanced Settings
    st.markdown("### ⚙️ Advanced Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        temperature = st.slider(
            "🌡️ Temperature", 
            0.0, 1.0, 0.7,
            help="Higher values make output more creative, lower values more focused"
        )
    with col2:
        max_sources = st.slider(
            "📚 Max Sources", 
            5, 20, 10,
            help="Maximum number of sources to research"
        )
    
    # Generation button
    st.markdown("---")
    generate_button = st.button(
        "🚀 Generate Article", 
        type="primary", 
        use_container_width=True,
        disabled=not topic.strip()
    )
    
    # Workflow information
    with st.expander("🔄 CrewAI Workflow Phases"):
        st.markdown("""
        **Phase 1: Research** 🔍
        - Senior Research Analyst finds sources
        - Fact Checker verifies information
        - Data Synthesizer organizes findings
        
        **Phase 2: Content Creation** ✍️
        - Content Strategist plans structure
        - Content Writer creates engaging copy
        - SEO Specialist optimizes for search
        
        **Phase 3: Editing** 📝
        - Copy Editor improves clarity
        - Technical Editor verifies accuracy
        - Publishing Editor finalizes format
        
        **Phase 4: Finalization** 🎯
        - Creates structured article
        - Calculates metrics
        - Prepares for delivery
        """)
    
    # Usage guide
    with st.expander("💡 Usage Tips"):
        st.markdown("""
        **Best Topics:**
        - Current events and trends
        - Technology developments
        - Industry analysis
        - Scientific discoveries
        - Market insights
        
        **Tips for Better Results:**
        - Be specific in your topic
        - Use recent/trending keywords
        - Include context or timeframes
        - Consider your target audience
        """)
    
    # API Keys status
    st.markdown("---")
    st.markdown("### 🔑 API Status")
    
    serper_key = os.getenv("SERPER_API_KEY")
    cohere_key = os.getenv("COHERE_API_KEY") or os.getenv("CO_API_KEY")
    
    if serper_key:
        st.success("✅ Serper API connected")
    else:
        st.error("❌ Serper API key missing")
        
    if cohere_key:
        st.success("✅ Cohere API connected") 
    else:
        st.error("❌ Cohere API key missing")

# Initialize session state for workflow tracking
if 'workflow_state' not in st.session_state:
    st.session_state.workflow_state = None
if 'generation_complete' not in st.session_state:
    st.session_state.generation_complete = False

def generate_content_with_flow(topic: str, temperature: float = 0.7, max_sources: int = 10):
    """Generate content using the CrewAI flow workflow."""
    try:
        # Create and run the flow
        flow = NewsGeneratorFlow(
            topic=topic, 
            temperature=temperature, 
            max_sources=max_sources
        )
        
        # Store flow in session state for tracking
        st.session_state.workflow_state = flow
        
        # Run the flow
        result = flow.kickoff()
        
        return flow
    
    except Exception as e:
        st.error(f"Error during content generation: {str(e)}")
        return None

def display_workflow_progress():
    """Display real-time workflow progress."""
    if st.session_state.workflow_state:
        flow = st.session_state.workflow_state
        
        # Progress indicators
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if flow.state.research_completed:
                st.success("✅ Research")
            else:
                st.info("🔍 Research")
                
        with col2:
            if flow.state.content_completed:
                st.success("✅ Content")
            else:
                st.info("✍️ Content")
                
        with col3:
            if flow.state.editing_completed:
                st.success("✅ Editing")
            else:
                st.info("📝 Editing")
                
        with col4:
            if flow.state.generation_completed:
                st.success("✅ Complete")
            else:
                st.info("🎯 Finalizing")

# Main content area
if not topic.strip():
    # Welcome message when no topic is entered
    st.markdown("### 👋 Welcome to AI News Generator!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Ready to create comprehensive, well-researched articles in minutes?**
        
        Our advanced AI workflow uses multiple specialized agents working together:
        
        🔍 **Research Team** - Finds and verifies information from reliable sources
        ✍️ **Content Team** - Creates engaging, well-structured articles  
        📝 **Editing Team** - Polishes and perfects the final output
        
        Simply enter your topic in the sidebar and click "Generate Article" to begin!
        """)
    
    with col2:
        st.image("https://via.placeholder.com/300x200?text=AI+News+Generator", 
                caption="Multi-Agent AI Workflow")

elif generate_button:
    # Check API keys before proceeding
    serper_key = os.getenv("SERPER_API_KEY")
    cohere_key = os.getenv("COHERE_API_KEY") or os.getenv("CO_API_KEY")
    
    if not serper_key or not cohere_key:
        st.error("🔑 Please set up your API keys (SERPER_API_KEY and COHERE_API_KEY) to use the generator.")
        st.stop()
    
    # Main generation process
    st.markdown(f"### 🚀 Generating Article: *{topic}*")
    
    # Progress section
    progress_container = st.container()
    
    with st.spinner('🤖 AI agents are working on your article...'):
        try:
            # Generate content using the flow
            flow_result = generate_content_with_flow(topic, temperature, max_sources)
            
            if flow_result and flow_result.state.generation_completed:
                st.session_state.generation_complete = True
                
                # Display success metrics
                with progress_container:
                    display_workflow_progress()
                    
                    # Show processing summary
                    summary = flow_result.get_processing_summary()
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📊 Research Sources", summary.get('research_sources', 0))
                    with col2:
                        st.metric("📝 Word Count", summary.get('word_count', 0))
                    with col3:
                        st.metric("⏱️ Processing Time", f"{summary.get('processing_time', 0):.1f}s")
                    with col4:
                        st.metric("📖 Readability Score", f"{summary.get('readability_score', 0):.1f}")
                
                # Display the generated content
                st.markdown("---")
                st.markdown("### 📰 Generated Article")
                
                final_content = flow_result.get_final_content()
                st.markdown(final_content)
                
                # Download options
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Download as Markdown
                    st.download_button(
                        label="📥 Download as Markdown",
                        data=final_content,
                        file_name=f"{topic.lower().replace(' ', '_')}_article.md",
                        mime="text/markdown",
                        type="primary"
                    )
                
                with col2:
                    # Download processing summary
                    import json
                    summary_json = json.dumps(summary, indent=2)
                    st.download_button(
                        label="📊 Download Summary",
                        data=summary_json,
                        file_name=f"{topic.lower().replace(' ', '_')}_summary.json",
                        mime="application/json"
                    )
                
                # Reset for new generation
                if st.button("🔄 Generate Another Article", type="secondary"):
                    st.session_state.workflow_state = None
                    st.session_state.generation_complete = False
                    st.rerun()
                
            else:
                st.error("❌ Content generation failed. Please try again.")
                
        except Exception as e:
            st.error(f"❌ An error occurred during generation: {str(e)}")
            st.error("Please check your API keys and internet connection, then try again.")

else:
    # Show sample or previous result
    if st.session_state.generation_complete and st.session_state.workflow_state:
        st.markdown("### 📰 Previous Article")
        st.markdown("*(Click 'Generate Article' in the sidebar to create a new one)*")
        
        display_workflow_progress()
        final_content = st.session_state.workflow_state.get_final_content()
        st.markdown(final_content)
    else:
        # Show examples or tips
        st.markdown("### 💡 Example Topics")
        
        examples = [
            "Latest developments in quantum computing",
            "Climate change impact on agriculture in 2025", 
            "Artificial intelligence in healthcare innovations",
            "Cryptocurrency market trends and regulations",
            "Space exploration missions planned for 2025"
        ]
        
        for i, example in enumerate(examples, 1):
            st.markdown(f"**{i}.** {example}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>🤖 <strong>AI News Generator v2.0</strong></p>
    <p>Built with CrewAI Flows, Streamlit, and powered by Cohere's Command R7B</p>
    <p><em>Advanced Multi-Agent Workflow for Professional Content Creation</em></p>
</div>
""", unsafe_allow_html=True)