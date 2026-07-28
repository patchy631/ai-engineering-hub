import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import nest_asyncio
from dotenv import load_dotenv
import os
import asyncio

from llama_index.llms.openai import OpenAI
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex

from src.models import PatientInfo, ConditionBundles, GuidelineRecommendation, CaseSummary
from src.utils import parse_synthea_patient
from src.workflow import GuidelineRecommendationWorkflow
from src.conditions import create_condition_bundles

# Apply nest_asyncio to allow running async code in Streamlit
nest_asyncio.apply()

# Load environment variables
load_dotenv()

# Initialize OpenAI and LlamaCloud
llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
index = LlamaCloudIndex(
    name="medical_guidelines_0",
    project_name="Default",
    organization_id="58cc6b83-c155-4ed1-b4c0-c47abb8bb202",
    api_key=os.getenv("LLAMA_CLOUD_API_KEY")
)

# Set up the Streamlit interface
st.title("Patient Case Summary Analysis")
st.write("Upload a patient JSON file to analyze their case summary using medical guidelines.")

# File uploader
uploaded_file = st.file_uploader("Choose a patient JSON file", type="json")

async def process_patient_data(workflow, temp_path):
    # Create a status container
    status = st.empty()
    status.text("Processing patient data...")

    # Run the workflow
    handler = workflow.run(patient_json_path=str(temp_path))
    
    # Process events
    progress_bar = st.progress(0)
    progress_text = st.empty()

    async for event in handler.stream_events():
        if hasattr(event, 'msg'):
            progress_text.text(event.msg)
            # Update progress bar (simplified example)
            progress_bar.progress(0.99)

    # Get the final result
    response_dict = await handler
    case_summary = response_dict["case_summary"]

    return case_summary

if uploaded_file is not None:
    # Save the uploaded file temporarily
    temp_path = Path("temp_patient.json")
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    try:
        # Initialize the workflow
        workflow = GuidelineRecommendationWorkflow(
            guideline_retriever=index.as_retriever(similarity_top_k=3),
            llm=llm,
            verbose=True,
            timeout=None
        )

        # Call the async function
        case_summary = asyncio.run(process_patient_data(workflow, temp_path))

        # Display results
        st.success("Analysis complete!")
        
        # Display patient information
        st.header("Patient Summary")
        st.markdown(case_summary.render())

        # Download button for the report
        report_json = case_summary.model_dump_json(indent=2)
        st.download_button(
            label="Download Report (JSON)",
            data=report_json,
            file_name="case_summary_report.json",
            mime="application/json"
        )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_path.exists():
            temp_path.unlink()

else:
    st.info("Please upload a patient JSON file to begin analysis.")