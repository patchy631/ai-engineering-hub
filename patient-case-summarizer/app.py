import streamlit as st
import asyncio
import os
from patient_case_summary import GuidelineRecommendationWorkflow, retriever
from llama_index.llms.ollama import Ollama

# Set page configuration for a wider layout and custom title
st.set_page_config(page_title="Patient Case Summary Generator", layout="wide", page_icon="🏥")

# Custom CSS for styling
st.markdown("""
    <style>
    .main-title {
        font-size: 36px;
        font-weight: bold;
        color: white;
        text-align: center-left;
        margin-bottom: 20px;
    }
    .subheader {
        font-size: 24px;
        color: white;
        margin-top: 20px;
    }
    .summary-box {
        background-color: #1e1e1e;
        color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        font-family: 'Courier New', Courier, monospace;
        font-size: 16px;
        line-height: 1.6;
        white-space: pre-wrap;
        border: 1px solid #444;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        width: 95%;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2980b9;
    }
    
    .table-style {
        width: 100%;
        border-collapse: collapse;
        border-radius: 10px;
    }
    
            .table-style th, .table-style td {
        padding: 10px;
        border: 1px solid #444;
        text-align: left;
        font-size: 18px;
    }
    
    .table-style th {
        background-color: #2596be;
        color: white;
    }
    .description {
        font-size: 20px;
        margin-bottom: 20px;
        margin-right: 40px;
        color: white;
        opacity: 0.5;
            }
    </style>
""", unsafe_allow_html=True)

# App title with custom styling
st.markdown('<div class="main-title">🏥 Patient Case Summary Generator</div>', unsafe_allow_html=True)
# Sidebar for instructions and branding
with st.sidebar:
    # File upload with a nicer label
    st.markdown("#### Upload Patient Data")
    uploaded_file = st.file_uploader("Choose a patient JSON file", type=["json"], help="Upload a Synthea-generated FHIR JSON file.")

    # Save uploaded file temporarily if provided
    if uploaded_file:
        patient_json_path = "temp_patient.json"
        with open(patient_json_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File uploaded successfully: {uploaded_file.name}")
    else:
        patient_json_path = None

# Main content area
col1, col2 = st.columns([4, 1])  # Two-column layout

with col2:
    st.markdown("### How to Use")
    st.markdown("""
    1. Upload a patient JSON file.
    2. Click 'Generate Summary' to process the data.
    3. View the formatted patient summary.
    """)
    st.markdown("---")
    st.markdown("Powered by Ollama & LLamaCloud")

with col1:
    st.markdown('<div class="description">The Patient Case Summary Generator is a Streamlit app that lets healthcare professionals upload patient JSON data to create concise AI-generated summaries. It uses medical guidelines to detail conditions, encounters, and recommendations.</div>', unsafe_allow_html=True)
    # Button with progress feedback
    st.markdown("#### Generate")
    generate_btn = st.button("Generate Summary", key="generate_btn")
    if generate_btn:
        if not patient_json_path or not os.path.exists(patient_json_path):
            st.error("Please upload a valid patient JSON file first.", icon="🚨")
        else:
            with st.spinner("Processing patient data..."):
                # Initialize the workflow
                llm = Ollama(model="deepseek-r1:7b", base_url="http://localhost:11434")
                workflow = GuidelineRecommendationWorkflow(
                    guideline_retriever=retriever,
                    llm=llm,
                    verbose=True,
                    timeout=None
                )

                # Define async function to run the workflow
                async def run_workflow():
                    handler = workflow.run(patient_json_path=patient_json_path)
                    response_dict = await handler
                    return response_dict["case_summary"]

                # Run the workflow and display results
                try:
                    case_summary = asyncio.run(run_workflow())

                    name = getattr(case_summary, "patient_name", "Unknown")
                    age = getattr(case_summary, "patient_age", "Unknown")
                    condition_summary_raw = case_summary.render().strip()
                    condition_summary = condition_summary_raw.replace(name, "").replace(str(age), "").strip()

                    st.subheader("Patient Details")
                    st.markdown(
                        f"""
                        <table style="width: 95%; border-collapse: collapse; text-align: left;">
                            <tr>
                                <th style="border: 1px solid #ddd; padding: 8px; background-color: #333c3d;">Attribute</th>
                                <th style="border: 1px solid #ddd; padding: 8px; background-color: #333c3d;">Value</th>
                            </tr>
                            <tr>
                                <td style="border: 1px solid #ddd; padding: 8px;">Name</td>
                                <td style="border: 1px solid #ddd; padding: 8px;">{name}</td>
                            </tr>
                            <tr>
                                <td style="border: 1px solid #ddd; padding: 8px;">Age</td>
                                <td style="border: 1px solid #ddd; padding: 8px;">{age}</td>
                            </tr>
                        </table>
                        """,
                        unsafe_allow_html=True
                    )

                    st.subheader("Condition Summary")
                    st.markdown(
                        f"""
                        <div style="max-height: 300px; overflow-y: auto; padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #333c3d; width: 95%">
                            <pre>{condition_summary_raw}</pre>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")



# Clean up temporary file
if patient_json_path and os.path.exists(patient_json_path):
    os.remove(patient_json_path)