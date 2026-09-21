import streamlit as st
import json
import os
from insurance_claim_processor import process_claim, ClaimInfo

st.set_page_config(page_title="Auto Insurance Claim Processor", layout="wide")

st.title("Auto Insurance Claim Processor")

# Create tabs for different ways to input claims
tab1, tab2 = st.tabs(["Process File", "Manual Entry"])

with tab1:
    st.header("Process Claim from JSON File")
    
    # File uploader section with its own button
    st.subheader("Upload a claim file")
    uploaded_file = st.file_uploader("Upload a claim JSON file", type=["json"])
    process_uploaded = st.button("Process Uploaded File", key="process_uploaded", disabled=uploaded_file is None)
    
    # Add some space between sections
    st.markdown("---")
    
    # Sample files section with its own button
    st.subheader("Or use a sample file")
    sample_files = []
    
    # Check for sample files in the data directory
    if os.path.exists("data"):
        sample_files = [f for f in os.listdir("data") if f.endswith(".json")]
    
    if sample_files:
        selected_sample = st.selectbox("Select a sample claim", sample_files)
        use_sample = st.button("Process Selected Sample", key="use_sample")
    else:
        st.warning("No sample files found in 'data' directory.")
        use_sample = False
        selected_sample = None
    
    # Handle file processing for uploaded file
    if process_uploaded and uploaded_file is not None:
        # Save uploaded file temporarily
        with open("temp_claim.json", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        with st.spinner("Processing claim..."):
            decision, logs = process_claim(claim_json_path="temp_claim.json")
            
            # Display results
            st.success("Claim processed successfully!")
            
            # Create two columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Claim Decision")
                st.json(json.loads(decision.model_dump_json()))
            
            with col2:
                st.subheader("Processing Logs")
                for log in logs:
                    st.text(log)
            
            # Clean up temp file
            if os.path.exists("temp_claim.json"):
                os.remove("temp_claim.json")
    
    # Handle sample file processing
    elif use_sample and selected_sample:
        sample_path = os.path.join("data", selected_sample)
        
        with st.spinner("Processing sample claim..."):
            decision, logs = process_claim(claim_json_path=sample_path)
            
            # Display results
            st.success(f"Sample claim {selected_sample} processed successfully!")
            
            # Create two columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Claim Decision")
                st.json(json.loads(decision.model_dump_json()))
            
            with col2:
                st.subheader("Processing Logs")
                for log in logs:
                    st.text(log)

with tab2:
    st.header("Enter Claim Details Manually")
    
    # Form for manual entry
    with st.form("claim_form"):
        claim_number = st.text_input("Claim Number")
        policy_number = st.text_input("Policy Number")
        claimant_name = st.text_input("Claimant Name")
        date_of_loss = st.date_input("Date of Loss")
        loss_description = st.text_area("Loss Description")
        estimated_repair_cost = st.number_input("Estimated Repair Cost", min_value=0.0, format="%.2f")
        vehicle_details = st.text_input("Vehicle Details (Optional)")
        
        submit_form = st.form_submit_button("Submit Claim")
    
    if submit_form:
        # Create claim data dictionary
        claim_data = {
            "claim_number": claim_number,
            "policy_number": policy_number,
            "claimant_name": claimant_name,
            "date_of_loss": date_of_loss.strftime("%Y-%m-%d"),
            "loss_description": loss_description,
            "estimated_repair_cost": estimated_repair_cost
        }
        
        if vehicle_details:
            claim_data["vehicle_details"] = vehicle_details
        
        with st.spinner("Processing claim..."):
            decision, logs = process_claim(claim_data=claim_data)
            
            # Display results
            st.success("Claim processed successfully!")
            
            # Create two columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Claim Decision")
                st.json(json.loads(decision.model_dump_json()))
            
            with col2:
                st.subheader("Processing Logs")
                for log in logs:
                    st.text(log)

# Add footer with information
st.markdown("---")
st.markdown("Insurance Claim Processor | Powered by LlamaIndex and Gemini")