import os
import gc
import uuid
import tempfile
import base64
import json
import asyncio
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path
import re  # Add this for regex pattern matching

from llama_index.llms.openai import OpenAI
from workflow_code.workflow import GuidelineRecommendationWorkflow, LogEvent
from workflow_code.guideline_retrieval import setup_guideline_retriever
from workflow_code.data_models import CaseSummary

# Load environment variables
load_dotenv()

# Initialize session state
if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}
    st.session_state.case_summary = None
    st.session_state.processing = False
    st.session_state.patient_info = None
    st.session_state.workflow_logs = []  # Change to list to store structured logs
    st.session_state.current_log_text = ""  # For plain text display

session_id = st.session_state.id

# Create data directories if they don't exist
data_dir = Path("data")
if not data_dir.exists():
    data_dir.mkdir(parents=True)

output_dir = Path("data_out")
if not output_dir.exists():
    output_dir.mkdir(parents=True)

def reset_session():
    """Reset the session state."""
    st.session_state.case_summary = None
    st.session_state.processing = False
    st.session_state.patient_info = None
    st.session_state.workflow_logs = []
    st.session_state.current_log_text = ""
    gc.collect()

async def process_patient_data(file_path, progress_callback=None):
    """Process patient data and generate case summary."""
    try:
        # Check for required API keys
        openai_api_key = os.getenv("OPENAI_API_KEY")
        llamacloud_api_key = os.getenv("LLAMACLOUD_API_KEY")
        
        if not openai_api_key:
            st.error("OpenAI API key is missing. Please add it to your .env file.")
            return None
            
        if not llamacloud_api_key:
            st.error("LlamaCloud API key is missing. Please add it to your .env file.")
            return None
        
        # Setup guideline retriever
        retriever = setup_guideline_retriever(
            name=os.getenv("GUIDELINE_INDEX_NAME", "medical_guidelines_0"),
            project_name=os.getenv("GUIDELINE_PROJECT_NAME", "llamacloud_demo"),
            organization_id=os.getenv("GUIDELINE_ORG_ID", "cdcb3478-1348-492e-8aa0-25f47d1a3902"),
            api_key=llamacloud_api_key,
            similarity_top_k=3
        )
        
        # Initialize LLM with increased timeout
        llm = OpenAI(model="gpt-4o", api_key=openai_api_key, timeout=120)
        
        # Initialize workflow with increased timeout
        workflow = GuidelineRecommendationWorkflow(
            guideline_retriever=retriever,
            llm=llm,
            verbose=True,
            timeout=300,  # 5 minutes timeout for the entire workflow
            output_dir=str(output_dir)
        )
        
        # Run workflow
        handler = workflow.run(patient_json_path=file_path)
        
        # Process events
        progress_placeholder = st.empty()
        progress_text = ""
        progress_percentage = 0
        total_steps = 5  # Approximate number of major steps in the workflow
        current_step = 0
        
        # Store logs in a structured format
        logs = []
        
        async for event in handler.stream_events():
            if isinstance(event, LogEvent):
                # Process the log message
                if event.delta:
                    progress_text += event.msg
                else:
                    # Add to structured logs with type detection
                    log_entry = {"text": event.msg}
                    
                    # Detect if this contains JSON data
                    if ">> Patient Info:" in event.msg:
                        # Extract JSON part
                        json_match = re.search(r'>> Patient Info: ({.*})', event.msg)
                        if json_match:
                            try:
                                json_data = json.loads(json_match.group(1).replace("'", '"'))
                                log_entry = {
                                    "type": "json",
                                    "title": ">> Patient Info:",
                                    "data": json_data
                                }
                            except:
                                pass
                    elif ">> Guideline recommendation:" in event.msg:
                        # Extract JSON part
                        json_match = re.search(r'>> Guideline recommendation: ({.*})', event.msg)
                        if json_match:
                            try:
                                json_data = json.loads(json_match.group(1).replace("'", '"'))
                                log_entry = {
                                    "type": "json",
                                    "title": ">> Guideline recommendation:",
                                    "data": json_data
                                }
                            except:
                                pass
                    elif ">> Found guidelines:" in event.msg:
                        # Extract text content
                        log_entry = {
                            "type": "code",
                            "title": ">> Found guidelines:",
                            "data": event.msg.replace(">> Found guidelines: ", "")
                        }
                    
                    # Add to logs list
                    logs.append(log_entry)
                    progress_text += event.msg + "\n"
                    
                    # Update progress based on message content
                    if ">> Reading patient info" in event.msg or ">> Loading patient info" in event.msg:
                        current_step = 1
                    elif ">> Creating condition bundles" in event.msg or ">> Loading condition bundles" in event.msg:
                        current_step = 2
                    elif ">> Generating query" in event.msg:
                        current_step = 3
                    elif ">> Found guidelines" in event.msg:
                        current_step = 3
                    elif ">> Guideline recommendation" in event.msg:
                        current_step = 4
                    elif ">> Generating Case Summary" in event.msg:
                        current_step = 5
                
                progress_percentage = min(int((current_step / total_steps) * 100), 95)
                
                if progress_callback:
                    progress_callback(progress_text, progress_percentage, logs)
                else:
                    progress_placeholder.text(progress_text)
                
                st.session_state.current_log_text = progress_text
                st.session_state.workflow_logs = logs
        
        # Get results
        response_dict = await handler
        case_summary = response_dict.get("case_summary")
        
        if progress_callback:
            progress_callback(progress_text + "\nCompleted!", 100, logs)
        
        return case_summary
    
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        if progress_callback:
            progress_callback(error_msg, 0)
        st.error(error_msg)
        return None

# Streamlit UI
st.set_page_config(
    page_title="Patient Case Report Powered by OpenAI and LlamaCloud",
    page_icon="🏥",
    layout="wide"
)

col1, col2 = st.columns([6, 1])

with col1:
    st.markdown("""
    # Patient Case Summary Generator
    ## Powered by OpenAI and LlamaCloud
    """)

with col2:
    st.button("Reset ↺", on_click=reset_session)
  
# Sidebar for file upload
with st.sidebar:
    st.header("Upload Patient Data")
    
    uploaded_file = st.file_uploader("Choose a patient data file (FHIR format)", type=["json"])
    
    if uploaded_file:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                # Parse the file to display basic patient info
                try:
                    patient_data = json.load(uploaded_file)
                    patient_entries = [entry for entry in patient_data.get("entry", []) 
                                      if entry.get("resource", {}).get("resourceType") == "Patient"]
                    
                    if patient_entries:
                        patient_resource = patient_entries[0].get("resource", {})
                        name_entry = patient_resource.get("name", [{}])[0]
                        given_name = name_entry.get("given", [""])[0]
                        family_name = name_entry.get("family", "")
                        
                        st.session_state.patient_info = {
                            "name": f"{given_name} {family_name}",
                            "gender": patient_resource.get("gender", ""),
                            "birth_date": patient_resource.get("birthDate", "")
                        }
                except Exception as e:
                    st.warning(f"Could not parse patient data: {str(e)}")
                
                # Process button
                if st.button("Generate Case Summary"):
                    st.session_state.processing = True
                    
                    # Create placeholders for progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Define callback for progress updates
                    def update_progress(msg, percentage, logs=None):
                        status_text.text(msg)
                        progress_bar.progress(percentage)
                        if logs:
                            st.session_state.workflow_logs = logs
                            st.session_state.current_log_text = msg
                    
                    with st.spinner("Processing patient data..."):
                        # Run the processing asynchronously
                        case_summary = asyncio.run(process_patient_data(file_path, update_progress))
                        
                        if case_summary:
                            st.session_state.case_summary = case_summary
                            st.session_state.processing = False
                            st.success("Case summary generated successfully!")
                        else:
                            st.error("Failed to generate case summary.")
                            st.session_state.processing = False
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.stop()
    
    # Display workflow logs in an expander with better formatting
    if st.session_state.workflow_logs:
        with st.expander("Workflow Logs", expanded=False):
            # Add a toggle for view mode
            view_mode = st.radio("View mode:", ["Formatted", "Plain Text"], horizontal=True)
            
            if view_mode == "Formatted":
                for log in st.session_state.workflow_logs:
                    if isinstance(log, dict) and "type" in log:
                        if log["type"] == "json":
                            st.markdown(f"**{log.get('title', '')}**")
                            st.json(log["data"])
                        elif log["type"] == "code":
                            st.markdown(f"**{log.get('title', '')}**")
                            st.code(log["data"])
                        else:
                            st.text(log.get("text", ""))
                    else:
                        # Fallback for simple text logs
                        st.text(log.get("text", str(log)))
            else:
                # Plain text view
                st.text(st.session_state.current_log_text)

# Main content area
if st.session_state.patient_info:
    st.subheader("Patient Information")
    patient_info = st.session_state.patient_info
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Name", patient_info["name"])
    with col2:
        st.metric("Gender", patient_info["gender"].capitalize())
    with col3:
        # Calculate age
        if patient_info["birth_date"]:
            birth_date = datetime.strptime(patient_info["birth_date"], "%Y-%m-%d")
            today = datetime.now()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            st.metric("Age", f"{age} years")
        else:
            st.metric("Birth Date", patient_info["birth_date"])

# Display case summary if available
if st.session_state.case_summary:
    case_summary = st.session_state.case_summary
    
    st.header("Case Summary")
    
    # Overall assessment
    st.subheader("Overall Assessment")
    st.write(case_summary.overall_assessment)
    
    # Condition summaries
    if case_summary.condition_summaries:
        st.subheader("Condition Summaries")
        
        for condition in case_summary.condition_summaries:
            with st.expander(f"{condition.condition_display}", expanded=True):
                st.write(condition.summary)
    
    # Download option
    summary_text = case_summary.render()
    st.download_button(
        label="Download Case Summary",
        data=summary_text,
        file_name=f"case_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )

# Display processing message
if st.session_state.processing:
    st.info("Processing patient data... This may take a few minutes.") 