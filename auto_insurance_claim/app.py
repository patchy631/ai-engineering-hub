import streamlit as st
import nest_asyncio
import asyncio
import json
import tempfile
import os
from opik import track
from workflows import LogEvent, AutoInsuranceWorkflow
from api import policy_index, ollama_llm, get_opik_tracker

# Apply nest_asyncio to allow async operations in Streamlit
nest_asyncio.apply()
get_opik_tracker()

workflow = AutoInsuranceWorkflow(
    policy_retriever=policy_index(),
    llm=ollama_llm(),
    verbose=True,
    timeout=None,  # don't worry about timeout to make sure it completes
)


async def stream_workflow(workflow, **workflow_kwargs):
    handler = workflow.run(**workflow_kwargs)
    async for event in handler.stream_events():
        if isinstance(event, LogEvent):
            if event.delta:
                print(event.msg, end="")
            else:
                print(event.msg)

    return await handler


st.title("Auto Insurance Claim Processing")

# File upload section
st.subheader("Upload File")
# col1, col2 = st.columns(2)

# with col1:
#     declaration_file = st.file_uploader("Upload Policy Declaration File (.md)", type=['md'])
claim_file = st.file_uploader("Upload Claim File (.json)", type=['json'])


@track()
async def main():
    if  claim_file:
        # policy_content = declaration_file.read().decode()
        claim_data = json.loads(claim_file.read().decode())
        
        st.success("Files uploaded successfully!")
        # Display claim information
        st.subheader("Claim Information")
        with st.expander("View Claim Details"):
            st.json(claim_data)
            
        # Create a temporary file to store the claim data
        with tempfile.NamedTemporaryFile(suffix='.json', mode='w+', delete=False) as temp_file:
            json.dump(claim_data, temp_file)
            temp_path = temp_file.name
        
        try:
            # Process the claim using the temporary file path
            with st.spinner("Analyzing claim against policy..."):
                try: 
                    response = await stream_workflow(workflow, claim_json_path=temp_path)
                    st.write(response["decision"])
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    else:
        st.info("Please upload a policy declaration file to begin.")
        
if __name__ == "__main__":
    asyncio.run(main())
    