import streamlit as st
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.response_synthesizers import TreeSummarize
from llama_index.core.prompts import PromptTemplate
from llama_index.core.tools import FunctionTool, QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

st.set_page_config(
    page_title="Patient Case Summary Workflow",
    page_icon="\U0001F3E5",
    layout="wide"
)

st.title("\U0001F3E5 Patient Case Summary Workflow")

# Initialize LLM
@st.cache_resource
def get_llm():
    return Ollama(model="gemma3:1b", request_timeout=120.0)

llm = get_llm()

# Use local embeddings instead of OpenAI
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# File uploader
uploaded_file = st.file_uploader("Upload patient medical records (txt format)", type="txt")

if uploaded_file:
    # Save uploaded file temporarily
    with open("temp_patient_case.txt", "w") as f:
        f.write(uploaded_file.getvalue().decode())
    
    # Load document
    documents = SimpleDirectoryReader(
        input_files=["temp_patient_case.txt"]
    ).load_data()
    
    # Display document preview
    with st.expander("Document Preview"):
        st.write(documents[0].text[:500] + "...")
    
    # Create summary module
    summary_template = PromptTemplate(
        """
        You are a medical professional assistant. Create a comprehensive summary 
        of the following patient case. Include:
        
        1. Patient demographics
        2. Medical history
        3. Current medications
        4. Allergies
        5. Present illness
        6. Assessment and plan
        
        Patient case:
        {context_str}
        
        Summary:
        """
    )
    
    summarize_module = TreeSummarize(
        summary_template=summary_template,
        llm=llm
    )
    
    # Create vector index for Q&A using local embeddings
    vector_index = VectorStoreIndex.from_documents(
        documents, 
        embed_model=embed_model,  # Use local embedding model
        llm=llm
    )
    
    # Set up retriever with similarity search
    retriever = VectorIndexRetriever(
        index=vector_index,
        similarity_top_k=3
    )
    
    # Create query engine
    qa_engine = RetrieverQueryEngine(
        retriever=retriever,
        node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)]
    )
    
    # Create the patient summary tool
    summary_tool = FunctionTool.from_defaults(
        fn=lambda x: summarize_module.get_response(documents),
        name="patient_summary",
        description="Generate a comprehensive summary of the patient case"
    )
    
    # Create the Q&A tool
    qa_tool = QueryEngineTool(
        query_engine=qa_engine,
        metadata=ToolMetadata(
            name="patient_qa",
            description="Answer specific questions about the patient case"
        )
    )
    
    # Create the combined query engine
    query_engine = SubQuestionQueryEngine.from_defaults(
        query_engine_tools=[summary_tool, qa_tool],
        llm=llm
    )
    
    # Create tabs for different functionalities
    tab1, tab2 = st.tabs(["Patient Summary", "Ask Questions"])
    
    with tab1:
        if st.button("Generate Patient Summary"):
            with st.spinner("Generating comprehensive patient summary..."):
                summary = summarize_module.get_response(documents)
                st.markdown("## Patient Summary")
                st.markdown(summary.response)
    
    with tab2:
        st.markdown("## Ask Questions About the Patient")
        question = st.text_input("Enter your question about the patient")
        
        if question and st.button("Get Answer"):
            with st.spinner("Finding answer..."):
                response = qa_engine.query(question)
                st.markdown("### Answer")
                st.markdown(response.response)
    
    # Clean up temporary file
    if os.path.exists("temp_patient_case.txt"):
        os.remove("temp_patient_case.txt")

else:
    st.info("Please upload a patient medical record to begin")
    
    # Sample questions to guide users
    st.markdown("### Sample questions you can ask:")
    st.markdown("- What medications is the patient currently taking?")
    st.markdown("- Does the patient have any allergies?")
    st.markdown("- What is the patient's medical history?")
    st.markdown("- What is the treatment plan for this patient?")
