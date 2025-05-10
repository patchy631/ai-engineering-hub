import streamlit as st
import json
import pandas as pd
import os
import nest_asyncio
from prompts import *
from classes import *
from utils import *
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.google import GeminiEmbedding

nest_asyncio.apply()
from llama_index.llms.groq import Groq
from agent_workflow import GuidelineRecommendationWorkflow
import asyncio
from dotenv import load_dotenv

load_dotenv(override=True)

# File paths
OUTPUT_DIR = "data_out/workflow_output"
PATIENT_INFO_PATH = f"{OUTPUT_DIR}/patient_info.json"
CONDITION_BUNDLES_PATH = f"{OUTPUT_DIR}/condition_bundles.json"
GUIDELINE_RECOMMENDATIONS_PATH = f"{OUTPUT_DIR}/guideline_recommendations.jsonl"


st.set_page_config(page_title="Patient Case Summary", layout="wide")
st.title("📋 Patient Case Summary AI Agent")

# Loading indicator
st.sidebar.header("Upload Patient Documents")
persist_dir = "./stored_index"
embed_model = GeminiEmbedding(
    model_name="models/embedding-001", api_key=os.getenv("GEMINI_API_KEY")
)
Settings.embed_model = embed_model
if os.path.exists(persist_dir):
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    # Load the index from the storage context
    index = load_index_from_storage(storage_context)

else:
    warning = st.sidebar.warning("Embeddings not found. Computing now...")
    with st.spinner("Computing embeddings... This may take a minute."):
        # Load documents and build index
        documents = SimpleDirectoryReader("ref_pdf").load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=persist_dir)
    warning.empty()

    st.sidebar.success("Embeddings computed successfully!")


retriever = index.as_retriever(similarity_top_k=3)

st.sidebar.success("Indexing complete!")

# Sidebar for File Upload
st.sidebar.header("Upload Patient Documents")
uploaded_file = st.sidebar.file_uploader(
    "Upload patient-related document (JSON or JSONL)",
    type=["json", "jsonl"],
)
wait_text = st.warning("Please upload a file to continue...")

llm = Groq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
)


# Function to check if files exist after processing
def check_files():

    if (
        os.path.exists(PATIENT_INFO_PATH)
        and os.path.exists(CONDITION_BUNDLES_PATH)
        and os.path.exists(GUIDELINE_RECOMMENDATIONS_PATH)
    ):
        return True  # All files exist

    return False


def process_file(input_json):
    """Ensures the workflow runs inside an async event loop."""

    async def run_workflow():
        workflow = GuidelineRecommendationWorkflow(
            guideline_retriever=retriever,
            llm=llm,
            verbose=True,
            timeout=None,
        )
        await workflow.run(
            patient_json_path=input_json
        )  # Properly await async function

    try:
        asyncio.run(run_workflow())  # Ensures the function runs inside an event loop
    except RuntimeError as e:
        st.error(f"Error processing file: {e}")


# File processing and display logic
if uploaded_file:
    wait_text.empty()
    st.sidebar.info("Processing uploaded file...")

    # Read uploaded file content
    try:
        uploaded_data = json.load(uploaded_file)
        with open("uploaded_file.json", "w") as f:
            json.dump(uploaded_data, f)

        with st.spinner("Processing patient case..."):

            process_file("uploaded_file.json")

            if check_files():
                st.sidebar.success("Processing complete!")
            else:
                st.sidebar.error("Processing failed. Files not found.")

        # Load processed data from output files
        patient_info = load_json(PATIENT_INFO_PATH)
        condition_bundles = load_json(CONDITION_BUNDLES_PATH)
        guideline_recommendations = load_jsonl(GUIDELINE_RECOMMENDATIONS_PATH)

        # Display Patient Information
        if patient_info:
            st.subheader("🧑‍⚕️ Patient Information")
            st.write(
                f"**Name:** {patient_info.get('given_name', 'N/A')} {patient_info.get('family_name', 'N/A')}"
            )
            st.write(f"**Birth Date:** {patient_info.get('birth_date', 'N/A')}")
            st.write(f"**Gender:** {patient_info.get('gender', 'N/A')}")

            # Conditions
            if "conditions" in patient_info:
                st.subheader("🦠 Medical Conditions")
                conditions_df = pd.DataFrame(patient_info["conditions"])
                st.dataframe(conditions_df, use_container_width=True)

            # Recent Encounters
            if "recent_encounters" in patient_info:
                st.subheader("📅 Recent Encounters")
                encounters_df = pd.DataFrame(patient_info["recent_encounters"])
                st.dataframe(encounters_df, use_container_width=True)

            # Medications
            if "current_medications" in patient_info:
                st.subheader("💊 Current Medications")
                medications_df = pd.DataFrame(patient_info["current_medications"])
                st.dataframe(medications_df, use_container_width=True)

        # Display Condition Bundles
        if condition_bundles:
            st.subheader("🔗 Condition Bundles")
            for bundle in condition_bundles.get("bundles", []):
                st.write(
                    f"### {bundle['condition']['display']} ({bundle['condition']['clinical_status']})"
                )

                # Related Encounters
                if bundle.get("encounters"):
                    st.write("**Encounters Related:**")
                    encounters_df = pd.DataFrame(bundle["encounters"])
                    st.dataframe(encounters_df, use_container_width=True)

                # Medications for the Condition
                if bundle.get("medications"):
                    st.write("**Medications:**")
                    medications_df = pd.DataFrame(bundle["medications"])
                    st.dataframe(medications_df, use_container_width=True)

        # Display Guideline Recommendations
        if guideline_recommendations:
            st.subheader("📜 Guideline Recommendations")
            recommendations_df = pd.DataFrame(guideline_recommendations)
            st.dataframe(recommendations_df, use_container_width=True)

    except Exception as e:
        st.sidebar.error(f"Error processing file: {e}")

else:
    st.sidebar.info("Upload a JSON or JSONL file to analyze patient cases.")
