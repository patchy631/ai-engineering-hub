import streamlit as st
import os
import json
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.workflows import ResearchAssistantFlow

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .source-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .citation-item {
        background: #ffffff;
        border-left: 4px solid #3b82f6;
        padding: 0.8rem;
        margin: 0.3rem 0;
        border-radius: 0 4px 4px 0;
    }
    
    .status-success {
        color: #059669;
        font-weight: bold;
    }
    
    .status-error {
        color: #dc2626;
        font-weight: bold;
    }
    
    .status-warning {
        color: #d97706;
        font-weight: bold;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if 'assistant' not in st.session_state:
        st.session_state.assistant = None
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'document_processed' not in st.session_state:
        st.session_state.document_processed = False
    
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = {}
    
    if 'current_document' not in st.session_state:
        st.session_state.current_document = None
    
    if 'last_response' not in st.session_state:
        st.session_state.last_response = None

def check_api_keys() -> Dict[str, bool]:
    api_keys = {
        'OPENAI_API_KEY': bool(os.getenv('OPENAI_API_KEY')),
        'FIRECRAWL_API_KEY': bool(os.getenv('FIRECRAWL_API_KEY')),
        'ZEP_API_KEY': bool(os.getenv('ZEP_API_KEY')),
        'VOYAGE_API_KEY': bool(os.getenv('VOYAGE_API_KEY')),
        'TENSORLAKE_API_KEY': bool(os.getenv('TENSORLAKE_API_KEY'))
    }
    return api_keys


class StreamlitResearchAssistant:
    def __init__(self, user_id: str = "streamlit_user", thread_id: str = "streamlit_session"):
        self.user_id = user_id
        self.thread_id = thread_id
        self.flow = None
        self.initialized = False
    
    def initialize(self) -> bool:
        try:
            # Initialize the flow
            self.flow = ResearchAssistantFlow(
                tensorlake_api_key=os.getenv("TENSORLAKE_API_KEY"),
                voyage_api_key=os.getenv("VOYAGE_API_KEY"),
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                zep_api_key=os.getenv("ZEP_API_KEY"),
                firecrawl_api_key=os.getenv("FIRECRAWL_API_KEY"),
                milvus_db_path="milvus_lite.db"
            )
            
            self.initialized = True
            return True
        except Exception as e:
            st.error(f"Failed to initialize Research Assistant: {str(e)}")
            return False
    
    def query(self, user_query: str) -> Dict[str, Any]:
        if not self.initialized:
            return {"error": "Research Assistant not initialized"}
        
        try:
            # Execute the flow
            result = self.flow.kickoff(inputs={
                "query": user_query,
                "user_id": self.user_id,
                "thread_id": self.thread_id
            })
            return result
            
        except Exception as e:
            error_msg = f"Error processing query: {e}"
            return {"error": error_msg}

def create_research_assistant() -> Optional[StreamlitResearchAssistant]:
    try:
        assistant = StreamlitResearchAssistant()
        if assistant.initialize():
            return assistant
        return None
    except Exception as e:
        st.error(f"Failed to create Research Assistant: {str(e)}")
        return None

def process_uploaded_document(uploaded_file, assistant: StreamlitResearchAssistant) -> bool:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file.flush()
            os.fsync(tmp_file.fileno())
            tmp_file_path = tmp_file.name
        
        st.session_state.processing_status = {
            'stage': 'uploading',
            'message': 'Uploading document...',
            'progress': 0.1
        }
        
        # Process document
        progress_bar = st.progress(0.1)
        status_text = st.empty()
        
        status_text.text("📄 Uploading document...")
        time.sleep(0.5)
        
        progress_bar.progress(0.3)
        status_text.text("🔍 Parsing document content...")
        time.sleep(1)
        
        progress_bar.progress(0.6)
        status_text.text("🧠 Generating embeddings...")
        time.sleep(1)
        
        progress_bar.progress(0.8)
        status_text.text("💾 Storing in vector database...")
        
        if assistant.initialized:
            try:
                results = assistant.flow.process_documents([tmp_file_path])
                st.session_state.current_document = uploaded_file.name
                st.session_state.document_processed = True
                
                progress_bar.progress(1.0)
                status_text.text("✅ Document processed successfully!")
                
                os.unlink(tmp_file_path)
                
            except Exception as e:
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                
                error_msg = str(e)
                if "TensorLake" in error_msg:
                    raise Exception(f"Document parsing failed: {error_msg}")
                elif "Embedding" in error_msg:
                    raise Exception(f"Embedding generation failed: {error_msg}")
                elif "API" in error_msg or "key" in error_msg.lower():
                    raise Exception(f"API authentication failed: {error_msg}")
                else:
                    raise Exception(f"Document processing failed: {error_msg}")
        else:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
            raise Exception("Research Assistant not initialized")
    
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        st.session_state.processing_status = {
            'stage': 'completed',
            'message': f'Document "{uploaded_file.name}" processed successfully',
            'progress': 1.0
        }
        
        return True
        
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        st.session_state.processing_status = {
            'stage': 'error',
            'message': f'Error: {str(e)}',
            'progress': 0.0
        }
        return False


def display_citations_dropdown(response: Dict[str, Any], key: str):
    if 'context_sources' not in response:
        return
    
    context_sources = response['context_sources']
    evaluation_result = response.get('evaluation_result', {})
    
    try:
        relevant_source_keys = evaluation_result.get('relevant_sources', [])
        title = "📚 **View Sources & Citations**"
            
        with st.expander(title, expanded=False):
            if 'relevant_sources' in evaluation_result:
                st.markdown("#### 🎯 Source Relevance Summary")
                
                relevant_sources = evaluation_result['relevant_sources']
                relevance_scores = evaluation_result.get('relevance_scores', {})
                reasoning = evaluation_result.get('reasoning', 'No reasoning provided')
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown("**Relevant Sources:**")
                    for source in relevant_sources:
                        score = relevance_scores.get(source, 'N/A')
                        if isinstance(score, (int, float)):
                            st.markdown(f"• **{source}**: {score:.2f}")
                        else:
                            st.markdown(f"• **{source}**: {score}")
                
                with col2:
                    st.markdown("**Reasoning:**")
                    st.markdown(f"*{reasoning}*")
                
                st.markdown("---")
            
            # Only display sources that are marked as relevant by the evaluator
            all_sources = [
                ('RAG (Documents)', context_sources.get('rag_result', {}), '📄', 'RAG'),
                ('Memory (History)', context_sources.get('memory_result', {}), '🧠', 'Memory'), 
                ('Web Search', context_sources.get('web_result', {}), '🌐', 'Web'),
                ('ArXiv Papers', context_sources.get('tool_result', {}), '📚', 'ArXiv')
            ]
            # Filter sources based on evaluation result
            relevant_source_keys = evaluation_result.get('relevant_sources', [])
            # If no evaluation result available, show all sources
            if not relevant_source_keys:
                sources = [(name, data, icon) for name, data, icon, key in all_sources if data]
            else:
                # Only show sources that were marked as relevant
                sources = []
                for name, data, icon, key in all_sources:
                    if data and key in relevant_source_keys:
                        sources.append((name, data, icon))
            
            if not sources:
                st.markdown("*No relevant sources found for this query.*")
                return
            
            for source_name, source_data, icon in sources:
                if not source_data:
                    continue
                
                if source_name == 'Memory (History)':
                    status = 'OK'
                elif source_name == 'Web Search':
                    has_search_results = source_data.get('search_results')
                    has_explicit_status = source_data.get('status') == 'OK'
                    has_answer = source_data.get('answer')
                    has_relevance = source_data.get('relevance_assessment')
                    
                    if has_search_results or has_explicit_status or (has_answer and has_relevance):
                        status = 'OK'
                    elif source_data.get('status') == 'ERROR':
                        status = 'ERROR'
                    elif source_data.get('status') == 'INSUFFICIENT_CONTEXT':
                        status = 'INSUFFICIENT_CONTEXT'
                    else:
                        status = 'UNKNOWN'
                elif source_name == 'ArXiv Papers':
                    status = source_data.get('status', 'UNKNOWN')
                else:  # RAG
                    status = source_data.get('status', 'UNKNOWN')
                
                # Create expandable section for each source
                with st.expander(f"{icon} **{source_name}** ({status})", expanded=False):
                    
                    if status == 'OK':
                        if source_name == 'Memory (History)':
                            context = source_data.get('context', [])
                            if context:
                                st.markdown("**Memory Context:**")
                                
                                if isinstance(context, (list, tuple)):
                                    items_to_show = context[:6]
                                    for i, item in enumerate(items_to_show):
                                        item_str = str(item) if item is not None else ""
                                        if len(item_str) > 200:
                                            truncated_item = item_str[:200] + "..."
                                        else:
                                            truncated_item = item_str
                                        st.markdown(f"• {truncated_item}")
                                    
                                    if len(context) > 6:
                                        st.markdown(f"*...and {len(context) - 6} more items*")
                                else:
                                    st.markdown(f"• {str(context)[:500]}...")
                            
                            relevance = source_data.get('relevance_assessment', {})
                            if relevance:
                                citations = relevance.get('citations', [])
                                if citations:
                                    st.markdown("**Citations:**")
                                    for citation in citations:
                                        label = citation.get('label', 'Citation')
                                        locator = citation.get('locator', 'N/A')
                                        st.markdown(f"• **{label}** ({locator})")
                                
                                confidence = relevance.get('confidence', 'N/A')
                                if confidence != 'N/A':
                                    st.markdown(f"**Confidence:** {confidence}")
                        
                        elif source_name == 'Web Search':
                            search_results = source_data.get('search_results', [])
                            answer = source_data.get('answer', '')
                            
                            if search_results:
                                st.markdown("**Web Search Results:**")
                                if isinstance(search_results, (list, tuple)):
                                    results_to_show = search_results[:3]
                                    for i, result in enumerate(results_to_show):
                                        if isinstance(result, dict):
                                            title = result.get('title', 'No title')
                                            url = result.get('url', '#')
                                            content = str(result.get('content', 'No content'))[:150]
                                            st.markdown(f"**{i+1}. [{title}]({url})**")
                                            st.markdown(f"*{content}...*")
                                            st.markdown("---")
                                        else:
                                            st.markdown(f"**{i+1}.** {str(result)[:200]}...")
                                    
                                    if len(search_results) > 3:
                                        st.markdown(f"*...and {len(search_results) - 3} more results*")
                                else:
                                    st.markdown(f"• {str(search_results)[:500]}...")
                            
                            elif answer and answer.strip():
                                st.markdown("**Web Search Content:**")
                                if answer.startswith('**') or '**' in answer:
                                    st.markdown(answer[:1000] + ('...' if len(answer) > 1000 else ''))
                                else:
                                    st.markdown(f"```\n{answer[:500]}{'...' if len(answer) > 500 else ''}\n```")
                            
                            relevance = source_data.get('relevance_assessment', {})
                            if relevance:
                                confidence = relevance.get('confidence', 'N/A')
                                if confidence != 'N/A':
                                    st.markdown(f"**Confidence:** {confidence}")
                            
                            citations = source_data.get('citations', [])
                            if citations:
                                st.markdown("**Citations:**")
                                for citation in citations:
                                    if isinstance(citation, dict):
                                        label = citation.get('label', 'Web Citation')
                                        locator = citation.get('locator', '#')
                                        if locator.startswith('http'):
                                            st.markdown(f"• [{label}]({locator})")
                                        else:
                                            st.markdown(f"• **{label}** ({locator})")
                                    else:
                                        st.markdown(f"• {str(citation)}")
                        
                        elif source_name == 'ArXiv Papers':
                            answer = source_data.get('answer', '')
                            papers = []
                            if answer:
                                try:
                                    import json
                                    parsed_answer = json.loads(answer)
                                    papers = parsed_answer.get('papers', [])
                                except json.JSONDecodeError:
                                    st.markdown("**ArXiv Response:**")
                                    st.markdown(f"```\n{answer[:300]}...\n```")
                            
                            if papers:
                                st.markdown("**Academic Papers:**")
                                if isinstance(papers, (list, tuple)):
                                    papers_to_show = papers[:3]
                                    for i, paper in enumerate(papers_to_show):
                                        if isinstance(paper, dict):
                                            title = paper.get('title', 'No title')
                                            authors = paper.get('authors', [])
                                            url = paper.get('url', '#')
                                            abstract = str(paper.get('abstract', 'No abstract'))[:200]
                                            
                                            st.markdown(f"**{i+1}. [{title}]({url})**")
                                            if authors and isinstance(authors, (list, tuple)):
                                                authors_to_show = authors[:3] if len(authors) > 3 else authors
                                                authors_str = ', '.join(str(author) for author in authors_to_show)
                                                if len(authors) > 3:
                                                    authors_str += f" and {len(authors) - 3} others"
                                                st.markdown(f"*Authors: {authors_str}*")
                                            st.markdown(f"*{abstract}...*")
                                            st.markdown("---")
                                        else:
                                            st.markdown(f"**{i+1}.** {str(paper)[:200]}...")
                                    
                                    if len(papers) > 3:
                                        st.markdown(f"*...and {len(papers) - 3} more papers*")
                                else:
                                    st.markdown(f"• {str(papers)[:500]}...")
                        
                        else:  # RAG or other sources
                            st.markdown("**Content:**")
                            try:
                                answer = source_data.get('answer', 'No answer available')
                                if answer is None:
                                    st.markdown("```\nNo content available\n```")
                                elif isinstance(answer, (str)):
                                    preview = answer[:300] if len(answer) > 300 else answer
                                    ellipsis = '...' if len(answer) > 300 else ''
                                    st.markdown(f"```\n{preview}{ellipsis}\n```")
                                elif isinstance(answer, (dict, list)):
                                    try:
                                        import json
                                        json_str = json.dumps(answer, indent=2)
                                        preview = json_str[:300] if len(json_str) > 300 else json_str
                                        ellipsis = '...' if len(json_str) > 300 else ''
                                        st.markdown(f"```json\n{preview}{ellipsis}\n```")
                                    except Exception:
                                        st.markdown(f"```\n{str(answer)[:300]}...\n```")
                                else:
                                    answer_str = str(answer)
                                    preview = answer_str[:300] if len(answer_str) > 300 else answer_str
                                    ellipsis = '...' if len(answer_str) > 300 else ''
                                    st.markdown(f"```\n{preview}{ellipsis}\n```")
                                    
                            except Exception as answer_error:
                                st.error(f"Error displaying answer: {str(answer_error)}")
                                st.markdown("```\nError loading content\n```")
                            
                            # Show citations with enhanced metadata
                            citations = source_data.get('citations', [])
                            if citations and isinstance(citations, (list, tuple)):
                                st.markdown("**Citations:**")
                                for i, citation in enumerate(citations):
                                    try:
                                        if not isinstance(citation, dict):
                                            st.markdown(f"• Citation {i+1}: {str(citation)}")
                                            continue
                                            
                                        label = citation.get('label', f'Citation {i+1}')
                                        locator = citation.get('locator', 'No location')
                                        label = str(label) if label is not None else f'Citation {i+1}'
                                        locator = str(locator) if locator is not None else 'No location'
                                        
                                        page_number = citation.get('page_number')
                                        chunk_index = citation.get('chunk_index')
                                        score = citation.get('score')
                                        chunk_content = citation.get('content', '')
                                        
                                        if locator.startswith('http'):
                                            st.markdown(f"• [{label}]({locator})")
                                        elif page_number is not None and chunk_index is not None:
                                            score_text = f" (Score: {score:.3f})" if isinstance(score, (int, float)) else ""
                                            st.markdown(f"**📄 Page {page_number}, Chunk {chunk_index}**{score_text}")
                                            
                                            if chunk_content:
                                                content_preview = chunk_content[:300] if len(chunk_content) > 300 else chunk_content
                                                ellipsis = '...' if len(chunk_content) > 300 else ''
                                                st.markdown(f"```\n{content_preview}{ellipsis}\n```")
                                            else:
                                                st.markdown("*No content preview available*")
                                        elif 'chunk_' in locator:
                                            st.markdown(f"• **{label}** (Document chunk)")
                                        else:
                                            st.markdown(f"• **{label}**")
                                    except Exception as citation_error:
                                        st.markdown(f"• Citation {i+1}: Error displaying citation ({str(citation_error)})")
                            elif citations:
                                st.markdown("**Citations:**")
                                st.markdown(f"• Raw citation data: {str(citations)[:200]}...")
                            
                            # Show additional metadata
                            if 'retrieval_metadata' in source_data:
                                metadata = source_data['retrieval_metadata']
                                if 'retrieved_chunks' in metadata:
                                    st.markdown(f"**Retrieved Chunks:** {metadata['retrieved_chunks']}")
                                if 'document_count' in metadata:
                                    st.markdown(f"**Documents Searched:** {metadata['document_count']}")
                        
                        confidence = source_data.get('confidence', 'N/A')
                        if confidence != 'N/A':
                            if isinstance(confidence, (int, float)):
                                st.markdown(f"**Confidence:** {confidence:.2f}")
                            else:
                                st.markdown(f"**Confidence:** {confidence}")
                    
                    elif status == 'INSUFFICIENT_CONTEXT':
                        st.warning(f"{source_data.get('answer', 'No relevant information found')}")
                    
                    else:
                        error_msg = source_data.get('error', source_data.get('message', source_data.get('answer', 'Unknown error')))
                        st.error(f"{error_msg}")
    
    except Exception as e:
        st.error(f"❌ Error displaying citations: {str(e)}")
        st.caption(f"Debug info: Error type: {type(e).__name__}")
        
        # Show raw data for debugging
        with st.expander("🔍 Debug Information", expanded=False):
            st.json({
                "context_sources_keys": list(context_sources.keys()) if isinstance(context_sources, dict) else str(type(context_sources)),
                "evaluation_result_keys": list(evaluation_result.keys()) if isinstance(evaluation_result, dict) else str(type(evaluation_result)),
                "error_details": str(e)
            })


def display_sidebar_document_processing():
    with st.sidebar:
        st.markdown("## 📄 Document Processing")
        if not st.session_state.assistant:
            if st.button("🚀 Initialize Research Assistant", type="primary"):
                with st.spinner("Initializing..."):
                    assistant = create_research_assistant()
                    if assistant:
                        st.session_state.assistant = assistant
                        st.success("✅ Assistant initialized!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to initialize!")
            st.markdown("---")
            return
        
        # Document upload
        uploaded_file = st.file_uploader(
            "Upload PDF Document",
            type=['pdf'],
            help="Upload a PDF document to analyze"
        )
        
        if uploaded_file is not None:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"📄 **{uploaded_file.name}**")
                st.caption(f"Size: {uploaded_file.size:,} bytes")
            
            with col2:
                if st.button("Process", type="primary", key="process_doc"):
                    with st.spinner("Processing..."):
                        success = process_uploaded_document(uploaded_file, st.session_state.assistant)
                        if success:
                            st.session_state.document_processed = True
                            st.session_state.current_document = uploaded_file.name
                            st.success("✅ Processed!")
                            st.rerun()
                        else:
                            st.error("❌ Failed!")
        
        if st.session_state.document_processed:
            st.success("✅ Document Ready")
            if st.session_state.current_document:
                st.caption(f"Current: {st.session_state.current_document}")
        else:
            st.info("📋 No document processed")
    
        st.markdown("---")
    
        if st.session_state.assistant and st.session_state.assistant.initialized:
            st.success("🤖 Assistant: Online")
        else:
            st.error("🤖 Assistant: Offline")

def display_main_chat_interface():
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown("## 💬 Research Chat")
    with col2:
        if st.button("🔄 Reset Chat", type="secondary", key="reset_chat"):
            st.session_state.chat_history = []
            st.session_state.last_response = None
            st.success("Chat reset!")
            st.rerun()
    
    if not st.session_state.document_processed:
        st.warning("⚠️ Please process a document first using the sidebar.")
        return
    
    # Display chat history
    for i, (query, response) in enumerate(st.session_state.chat_history):
        with st.container():
            # User message
            st.markdown(f"**🧑 You:** {query}")
            # Assistant response
            if isinstance(response, dict) and 'final_response' in response:
                st.markdown(f"**🤖 Assistant:** {response['final_response']}")
                # Add citations dropdown
                display_citations_dropdown(response, f"citations_{i}")
            else:
                st.markdown(f"**🤖 Assistant:** {response}")
            
            st.markdown("---")

    query = st.chat_input("Ask me anything about your document...")
    
    if query:
        # Add user message to history
        with st.spinner("🔍 Researching your question..."):
            try:
                # Show progress steps
                progress_container = st.container()
                with progress_container:
                    st.info("📄 **Step 1/4:** Analyzing document...")
                    time.sleep(0.5)
                    st.info("🧠 **Step 2/4:** Retrieving memories...")
                    time.sleep(0.5)
                    st.info("🌐 **Step 3/4:** Searching web...")
                    time.sleep(0.5)
                    st.info("📚 **Step 4/4:** Searching academic papers...")
                    time.sleep(0.5)
                
                result = st.session_state.assistant.query(query)

                progress_container.empty()
                # Add to chat history
                st.session_state.chat_history.append((query, result))
                st.session_state.last_response = result
                st.rerun()
                
            except Exception as e:
                st.error(f"Error processing query: {str(e)}")

def display_initialization_message():
    st.info("⚠️ Please initialize the Research Assistant using the sidebar to begin.")

def main():
    initialize_session_state()
    
    st.markdown('''
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style='color: #ffffff; font-size: 3rem; font-weight: bold; margin-bottom: 10px;'>
                🔬 AI Research Assistant
            </h1>
            <div style="display: flex; justify-content: center; align-items: center; gap: 8px; margin-bottom: 20px;">
                <span style='color: #64748b; font-size: 16px; font-weight: 500;'>Powered by</span>
                <div style="display: flex; align-items: center; gap: 25px; margin-left: 15px;">
                    <a href="https://www.tensorlake.ai/" style="display: inline-block; vertical-align: middle;">
                        <img src="https://i.ibb.co/PZD1qrPg/tensorlake-logo.png" 
                             alt="Tensorlake" style="height: 36px;">
                    </a>
                    <a href="https://www.getzep.com/" style="display: inline-block; vertical-align: middle;">
                        <img src="https://i.ibb.co/DgtgNLVQ/zep-logo.png" 
                             alt="Zep" style="height: 32px;">
                    </a>
                    <a href="https://www.firecrawl.dev/" style="display: inline-block; vertical-align: middle;">
                        <img src="https://i.ibb.co/67jyMHfy/firecrawl-light-wordmark.png" 
                             alt="Firecrawl" style="height: 28px;">
                    </a>
                    <a href="https://www.crewai.com/" style="display: inline-block; vertical-align: middle;">
                        <img src="https://i.ibb.co/JwmNZhCx/crewai-logo.png" 
                             alt="CrewAI" style="height: 28px;">
                    </a>
                    <a href="https://milvus.io/" style="display: inline-block; vertical-align: middle;">
                        <img src="https://milvus.io/images/layout/milvus-logo.svg" 
                             alt="Milvus" style="height: 28px;">
                    </a>
                </div>
            </div>
            <p style='color: #64748b; font-size: 14px; margin-top: 10px;'>
                <b>Context Engineering Workflow</b> with RAG, Web Search, Memory & Academic Research
            </p>
        </div>
    ''', unsafe_allow_html=True)
    
    display_sidebar_document_processing()
    
    if st.session_state.assistant and st.session_state.assistant.initialized:
        display_main_chat_interface()
    else:
        display_initialization_message()

if __name__ == "__main__":
    main()
