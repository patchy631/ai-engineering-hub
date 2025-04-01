import asyncio
import streamlit as st
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# Import required modules from our package
from src.indices import retriever
from src.workflow import AutoInsuranceWorkflow, LogEvent

st.set_page_config(
    page_title="ClaimSonic: Smart Claim Assistant",
    layout="wide",
    initial_sidebar_state="auto"
)

# Inject custom CSS for styling
st.markdown("""
<style>
.app-container {
    background: #F0F4F8;
    font-family: Verdana, sans-serif;
    padding: 2rem;
    border-radius: 8px;
    margin: 1rem;
}
.log-message {
    padding: 6px;
    margin-bottom: 8px;
    background-color: #1976D2;
    color: white;
    border-radius: 4px;
    font-size: 0.9rem;
}
.workflow-output {
    background-color: #ffffff;
    border: 2px solid #1976D2;
    border-radius: 8px;
    padding: 1.5rem;
    margin-top: 2rem;
}
.workflow-output h4 {
    color: #1976D2;
    margin-bottom: 1rem;
    font-size: 1.4rem;
}
.workflow-output p {
    margin: 0.5rem 0;
    font-size: 1rem;
}
.workflow-output .highlight {
    color: #D32F2F;
    font-weight: bold;
}
.simulated-box {
    border: 2px dashed #1976D2;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    color: #1976D2;
    font-size: 1.2rem;
    margin-bottom: 1rem;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# Create the main container for the app
with st.container():
    st.markdown("<div class='app-container'>", unsafe_allow_html=True)
    st.title("Auto Claim Assistant")
    st.write("Your intelligent assistant to process auto insurance claims seamlessly.")

    st.info("Click the button below to simulate loading a PDF file with claim data.")

    # Initialize session state to store the claim JSON if not already present.
    if "claim_json_input" not in st.session_state:
        st.session_state["claim_json_input"] = ""

    # Simulated PDF upload box
    st.markdown("""
    <div class='simulated-box'>
        Click the button below to simulate PDF upload
    </div>
    """, unsafe_allow_html=True)

    # Simulated 'PDF Upload' button
    if st.button("Simulate PDF Upload"):
        st.session_state["claim_json_input"] = """{
  "claim_number": "CLM12345",
  "policy_number": "POL67890",
  "claimant_name": "Jane Doe",
  "date_of_loss": "2025-04-12",
  "loss_description": "Rear-end collision causing bumper damage",
  "estimated_repair_cost": 1200.50,
  "vehicle_details": "2019 Honda Accord"
}"""
        st.success("Simulated PDF loaded and claim data extracted!")

    # Display the (read-only) extracted claim JSON
    st.text_area("Extracted Claim JSON", value=st.session_state["claim_json_input"], height=220)

    # Instantiate the workflow (verbose mode enabled)
    workflow = AutoInsuranceWorkflow(policy_retriever=retriever, verbose=True, timeout=None)

    # Helper function to display log messages
    def display_log(message: str):
        st.markdown(f"<div class='log-message'>{message}</div>", unsafe_allow_html=True)

    # Function to run the workflow asynchronously
    async def run_workflow(claim_json_text: str):
        st.write("Starting claim workflow execution...")
        handler = workflow.run(claim_json_text=claim_json_text)
        async for event in handler.stream_events():
            if isinstance(event, LogEvent):
                display_log(event.msg)
        return await handler

    # Execute workflow button
    if st.button("Execute Claim Workflow"):
        if st.session_state["claim_json_input"].strip() == "":
            st.error("Please simulate a PDF upload first.")
        else:
            with st.spinner("Processing claim..."):
                result = asyncio.run(run_workflow(st.session_state["claim_json_input"]))
                decision = result["decision"]
                st.markdown(f"""
                <div class='workflow-output'>
                    <h4>Claim Decision</h4>
                    <p><strong>Claim Number:</strong> <span class="highlight">{decision.claim_number}</span></p>
                    <p><strong>Covered:</strong> <span class="highlight">{'Yes' if decision.covered else 'No'}</span></p>
                    <p><strong>Deductible:</strong> <span class="highlight">${decision.deductible:.2f}</span></p>
                    <p><strong>Recommended Payout:</strong> <span class="highlight">${decision.recommended_payout:.2f}</span></p>
                    <p><strong>Notes:</strong> {decision.notes}</p>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)