# Import required libraries for handling image conversion
import sys
import streamlit as st
import tempfile
import os
sys.path.append(os.getcwd())
from llama_index.llms.openai import OpenAI
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
import asyncio
import nest_asyncio
nest_asyncio.apply()
from llama_index.core.llms import LLM

from data_model import *
from Workflow import GuidelineRecommendationWorkflow

# Add import from the model of your choice. e.g.:
# from deepsseek import DeepSeekModel
# llm = DeepSeekModel.load("path/to/deepseek-model")
llm = None
async def execute_workflow(llama_inputs:dict, patient_info_path:str, llm:Optional[LLM] = None):

    index = LlamaCloudIndex(
        name=llama_inputs["name"],
        project_name=llama_inputs["project_name"],
        organization_id=llama_inputs["organization_id"],
        api_key=llama_inputs["api_key"]
    )

    retriever = index.as_retriever(similarity_top_k=3)

    llm = llm or OpenAI(model="gpt-4-turbo")  # "gpt-4o")

    workflow = GuidelineRecommendationWorkflow(
        guideline_retriever=retriever,
        llm=llm,
        verbose=True,
        timeout=None,  # don't worry about timeout to make sure it completes
    )

    handler = workflow.run(patient_json_path= patient_info_path)
    async for event in handler.stream_events():
        if isinstance(event, LogEvent):
            if event.delta:
                print(event.msg, end="")
            else:
                print(event.msg)
    response_dict = await handler
    st.write(str(response_dict["case_summary"].render()))


st.markdown("""
    <style>
    /* Change the background color of the main page */
    .reportview-container {
        background-color: #add8e6;  /* Light Blue background */
        opacity: 0.5;
    }

    /* Change the background color of the sidebar */
    .sidebar .sidebar-content {
        background-color: #e6f7ff;  /* Light Blue for the sidebar */
    }
    </style>
    """, unsafe_allow_html=True)

# Streamlit Interface
st.title("Patient Case Summary")
st.write("Tool to generate a patient case summary based on the patient's historical data and the latest medical guidelines.")
st.write("Follow the steps below to generate the patient case summary.")


st.header("Step 0 - OPENAI API KEY")
st.write("Please (in the sidebar) introduce your OpenAI API Key")
os.environ["OPENAI_API_KEY"] = st.sidebar.text_input(label="OpenAI API Key", type="password")


st.header("STEP 1 - Patient Information")
uploaded_file = st.file_uploader("Upload patient json file", type="json")

if uploaded_file is not None:
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        temp_file.write(uploaded_file.read())  # Save the uploaded file to temp location
        st.session_state["patient_info_path"] = temp_file.name  # Save the patient_info_path = temp_file.name  # Get the file path


st.header("Step2 - Guide Retrieval in LLamaIndex")
st.write("Fill this form to tell the tool where it should look for the guidelines inside LlamaIndex.")
if "llama_inputs" not in st.session_state:
    st.session_state.llama_inputs = {}
with st.expander("LlamaIndex Configuration", expanded=False):
    with st.form(key='llama_form'):
        name = st.text_input("Name", "")
        project_name = st.text_input("Project Name", "")
        organization_id = st.text_input("Organization ID", "")
        api_key = st.text_input("API Key", type="password")
        submit_button = st.form_submit_button("Save LlamaIndex Configuration")

        #Cuando se presiona el botón, guardar los valores en un diccionario
        if submit_button:
            st.session_state.llama_inputs = {
                "name": name,
                "project_name": project_name,
                "organization_id": organization_id,
                "api_key": api_key
            }
            st.success("LamaIndex configuration values saved!")
            llama_inputs_copy = st.session_state.llama_inputs.copy()
            llama_inputs_copy["api_key"] = "XXXXXX"
            st.json(llama_inputs_copy)

st.header("Step3 - Get your patient case summary!")
st.write("Just press the the buttom and wait for the output!")

get_summary_buttom = st.button("Generate Patient Case Summary", type="primary", key="get_summary")
if get_summary_buttom:
    with st.spinner("Wait for it...", show_time=True):
        asyncio.run(execute_workflow(st.session_state.llama_inputs, st.session_state["patient_info_path"], llm))
else:
    st.warning("Please press the button to generate the patient case summary")


