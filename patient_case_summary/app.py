import streamlit as st
import os
import asyncio
from patient_case_summary import parse_synthea_patient, create_condition_bundles, generate_case_summary

# Set up LlamaCloud API key
os.environ["LLAMA_CLOUD_API_KEY"] = "your-llx-api-key"

# Streamlit UI
st.title("🩺 AI-Powered Medical Case Summarizer")

uploaded_file = st.file_uploader("Upload a patient JSON file", type=["json"])

async def process_patient(file_path):
    """Handles async patient data processing."""
    patient_info = parse_synthea_patient(file_path)
    condition_bundles = await create_condition_bundles(patient_info)  # Await properly
    return generate_case_summary(condition_bundles)

if uploaded_file is not None:
    with open("temp_patient.json", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write("✅ File uploaded successfully!")

    # Run async function in a separate event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.run_coroutine_threadsafe(process_patient("temp_patient.json"), loop)
    case_summary = future.result()  # Get the result safely

    st.subheader("📄 Patient Case Summary")
    st.write(case_summary)
