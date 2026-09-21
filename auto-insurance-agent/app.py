import streamlit as st
import os
import json
import asyncio
import nest_asyncio
# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Import required libraries
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
# Import local modules
from src.workflow.workflow import AutoInsuranceWorkflow
from src.ui.components import StreamlitEventHandler
from src.utils.helpers import (
    get_declarations_docs, get_local_declaration_file,
    generate_workflow_visualization
)
from src.workflow.events import LogEvent

# Set page configuration
st.set_page_config(
    page_title="Auto Insurance Claim Processor",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Streamlit app starts here
    st.title("🚗 Auto Insurance Claim Processor")
    
    # Create tabs for different sections of the app
    tab1, tab2, tab3, tab4 = st.tabs(["Process Claims", "Policy Viewer", "Workflow Visualization", "About"])
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")

    # API Key inputs
    with st.sidebar.expander("API Keys", expanded=False):
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        llama_cloud_api_key = st.text_input("LlamaCloud API Key", type="password")

    # Index configuration
    with st.sidebar.expander("Index Configuration", expanded=False):
        claim_index_name = st.text_input("LlamaCloud Claims Index Name", value="auto-insurance-claims")
        declarations_index_name = st.text_input("LlamaCloud Declarations Index Name", value="auto-insurance-declarations")
        llama_cloud_org_id = st.text_input("Organization ID", type="password")
    
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        if llama_cloud_api_key:
            os.environ["LLAMA_CLOUD_API_KEY"] = llama_cloud_api_key
        if llama_cloud_org_id:
            os.environ["LLAMA_CLOUD_ORG_ID"] = llama_cloud_org_id

    with tab1:
        st.markdown("""
        This app processes auto insurance claims by:
        1. Analyzing claim information
        2. Retrieving relevant policy sections
        3. Evaluating coverage and deductibles
        4. Producing a final claim decision with recommended payout
        """)

        # Model selection
        model_option = st.sidebar.selectbox(
            "Select LLM Model",
            ["gpt-4o", "gpt-4"]
        )

        # Claim input method
        input_method = st.sidebar.radio("Claim Input Method", ["Upload JSON", "Sample Data", "Manual Entry"])

        # Main content area
        claim_data = None

        if input_method == "Upload JSON":
            uploaded_file = st.file_uploader("Upload claim JSON file", type=["json"])
            if uploaded_file is not None:
                try:
                    claim_data = json.load(uploaded_file)
                    st.success("File uploaded successfully!")
                except Exception as e:
                    st.error(f"Error parsing JSON: {e}")

        elif input_method == "Sample Data":
            sample_option = st.selectbox("Select sample claim", ["John's Rear-End Collision", "Alice's Parking Lot Damage"])
            
            if sample_option == "John's Rear-End Collision":
                claim_data = {
                    "claim_number": "CLAIM-12345",
                    "policy_number": "POLICY-ABC123",
                    "claimant_name": "John Smith",
                    "date_of_loss": "2023-05-15",
                    "loss_description": "Rear-ended at stoplight by another vehicle",
                    "estimated_repair_cost": 4500.00,
                    "vehicle_details": "2020 Toyota Camry"
                }
            else:
                claim_data = {
                    "claim_number": "CLAIM-67890",
                    "policy_number": "POLICY-DEF456",
                    "claimant_name": "Alice Johnson",
                    "date_of_loss": "2023-06-20",
                    "loss_description": "Vehicle damaged in parking lot by shopping cart",
                    "estimated_repair_cost": 1200.00,
                    "vehicle_details": "2019 Honda Civic"
                }

        elif input_method == "Manual Entry":
            with st.form("claim_form"):
                col1, col2 = st.columns(2)
                with col1:
                    claim_number = st.text_input("Claim Number", value="CLAIM-")
                    policy_number = st.text_input("Policy Number", value="POLICY-")
                    claimant_name = st.text_input("Claimant Name")
                    date_of_loss = st.date_input("Date of Loss")
                
                with col2:
                    vehicle_details = st.text_input("Vehicle Details (Year, Make, Model)")
                    estimated_repair_cost = st.number_input("Estimated Repair Cost ($)", min_value=0.0, step=100.0)
                    
                loss_description = st.text_area("Loss Description")
                
                submit_button = st.form_submit_button("Submit Claim")
                
                if submit_button:
                    claim_data = {
                        "claim_number": claim_number,
                        "policy_number": policy_number,
                        "claimant_name": claimant_name,
                        "date_of_loss": str(date_of_loss),
                        "loss_description": loss_description,
                        "estimated_repair_cost": float(estimated_repair_cost),
                        "vehicle_details": vehicle_details
                    }

        # Display claim data if available
        if claim_data:
            st.subheader("Claim Information")
            
            # Format the display in columns
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Claim Number:** {claim_data['claim_number']}")
                st.write(f"**Policy Number:** {claim_data['policy_number']}")
                st.write(f"**Claimant:** {claim_data['claimant_name']}")
                st.write(f"**Date of Loss:** {claim_data['date_of_loss']}")
            
            with col2:
                st.write(f"**Vehicle:** {claim_data.get('vehicle_details', 'N/A')}")
                st.write(f"**Estimated Repair Cost:** ${claim_data['estimated_repair_cost']:.2f}")
            
            st.write("**Loss Description:**")
            st.write(claim_data['loss_description'])
            
            # Process button
            if st.button("Process Claim"):
                if not openai_api_key:
                    st.error("Please provide an OpenAI API key in the sidebar.")
                elif not llama_cloud_api_key:
                    st.error("Please provide a LlamaCloud API key in the sidebar.")
                else:
                    with st.spinner("Processing claim..."):
                        try:
                            # Initialize LLM based on selection
                            if "gpt" in model_option:
                                llm = OpenAI(model=model_option)
                            else:
                                llm = Anthropic(model=model_option)
                            
                            # Initialize index with better error handling
                            try:
                                # Import here to ensure it's in the right scope
                                import requests.exceptions
                                
                                try:
                                    index = LlamaCloudIndex(
                                        name=claim_index_name,
                                        project_name="Default",
                                        organization_id=llama_cloud_org_id,
                                        api_key=llama_cloud_api_key
                                    )
                                    
                                    retriever = index.as_retriever(rerank_top_n=3)
                                    
                                    # Initialize declarations index with better error handling
                                    declarations_index = None
                                    try:
                                        declarations_index = LlamaCloudIndex(
                                            name=declarations_index_name,
                                            project_name="Default",
                                            organization_id=llama_cloud_org_id,
                                            api_key=llama_cloud_api_key
                                        )
                                    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                                        st.warning(f"Connection timeout when initializing declarations index: {e}. Proceeding without declarations.")
                                    except Exception as e:
                                        st.warning(f"Could not initialize declarations index: {e}. Proceeding without declarations.")
                                    
                                    # Create containers for progress and details
                                    progress_container = st.empty()
                                    st.markdown("### Processing Details")
                                    details_container = st.empty()
                                    
                                    # Initialize workflow
                                    workflow = AutoInsuranceWorkflow(
                                        policy_retriever=retriever,
                                        declarations_index=declarations_index,
                                        llm=llm,
                                        verbose=True,
                                        timeout=None
                                    )
                                    
                                    # Create a temporary JSON file
                                    temp_file_path = "temp_claim.json"
                                    with open(temp_file_path, "w") as f:
                                        json.dump(claim_data, f)
                                    
                                    # Run the workflow with enhanced progress tracking
                                    async def run_workflow():
                                        handler = workflow.run(claim_json_path=temp_file_path)
                                        streamlit_handler = StreamlitEventHandler(progress_container, details_container)
                                        
                                        async for event in handler.stream_events():
                                            if isinstance(event, LogEvent):
                                                await streamlit_handler.handle_event(event)
                                        
                                        return await handler
                                    
                                    # Execute the workflow
                                    result = asyncio.run(run_workflow())
                                    
                                    # Clean up temp file
                                    if os.path.exists(temp_file_path):
                                        os.remove(temp_file_path)
                                    
                                    # Display results
                                    st.subheader("Claim Decision")
                                    decision = result["decision"]
                                    
                                    # Create a styled box for the decision
                                    decision_status = "✅ APPROVED" if decision.covered else "❌ DENIED"
                                    status_color = "green" if decision.covered else "red"
                                    
                                    st.markdown(f"""
                                    <div style="padding: 20px; border-radius: 10px; background-color: #f0f2f6;">
                                        <h3 style="color: {status_color};">{decision_status}</h3>
                                        <p><strong>Claim Number:</strong> {decision.claim_number}</p>
                                        <p><strong>Deductible:</strong> ${decision.deductible:.2f}</p>
                                        <p><strong>Recommended Payout:</strong> ${decision.recommended_payout:.2f}</p>
                                        <p><strong>Notes:</strong> {decision.notes}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                                    st.error(f"Connection timeout when initializing LlamaCloud index: {str(e)}")
                                    st.info("""
                                    The server took too long to respond. This might be due to:
                                    - Network connectivity issues
                                    - High server load
                                    - Temporary service disruption
                                    
                                    Please try again later or check your connection.
                                    """)
                            except Exception as e:
                                st.error(f"Error initializing LlamaCloud index: {str(e)}")
                                
                                # Add more detailed troubleshooting information
                                with st.expander("Troubleshooting Connection Issues"):
                                    st.markdown("""
                                    ### Connection Troubleshooting
                                    
                                    The error "Server disconnected without sending a response" typically indicates:
                                    
                                    1. **Server Overload**: The LlamaCloud server might be experiencing high traffic
                                    2. **Network Issues**: There might be connectivity problems between your application and LlamaCloud
                                    3. **Timeout**: The request might be taking too long and timing out
                                    
                                    #### Possible Solutions:
                                    
                                    - Try again later when server load might be lower
                                    - Check your internet connection
                                    - Verify your API key and organization ID are correct
                                    - Contact LlamaCloud support if the issue persists
                                    """)
                        except Exception as e:
                            st.error(f"Error processing claim: {str(e)}")
        else:
            st.info("Please provide claim information using one of the input methods in the sidebar.")
    
    with tab2:
        st.header("Policy Document Viewer")
        st.markdown("""
        View insurance policy documents and declarations pages. The system will attempt to retrieve 
        documents from LlamaCloud, with sample documents as fallback.
        """)
        
        # Get API key from sidebar or environment
        llama_cloud_api_key = os.environ.get("LLAMA_CLOUD_API_KEY", "")
        if not llama_cloud_api_key and 'llama_cloud_api_key' in st.session_state:
            llama_cloud_api_key = st.session_state['llama_cloud_api_key']
        
        # Document type selection
        doc_type = st.radio("Select Document Type", ["Insurance Policy", "Declarations Page"])
        
        if doc_type == "Insurance Policy":
            st.subheader("Auto Insurance Policy")
            
            # Add a search box
            search_term = st.text_input("Search in policy document (optional):")
            
            # Define sample policy sections for fallback
            policy_sections = [
                {
                    "title": "SECTION I - LIABILITY COVERAGE",
                    "content": """
### A. Insuring Agreement

We will pay damages for bodily injury or property damage for which any insured becomes legally responsible because of an auto accident. Damages include prejudgment interest awarded against the insured. We will settle or defend, as we consider appropriate, any claim or suit asking for these damages. In addition to our limit of liability, we will pay all defense costs we incur.

### B. Exclusions

We do not provide Liability Coverage for any insured:

1. Who intentionally causes bodily injury or property damage.
2. For property damage to property owned or being transported by that insured.
3. For property damage to property rented to, used by, or in the care of that insured.
                    """
                },
                {
                    "title": "SECTION II - COLLISION COVERAGE",
                    "content": """
### A. Insuring Agreement

We will pay for direct and accidental loss to your covered auto or any non-owned auto, including their equipment, minus any applicable deductible shown in the Declarations. If loss to more than one covered auto or non-owned auto results from the same collision, only the highest applicable deductible will apply.

### B. Deductible

The deductible amount shown in the Declarations Page will be subtracted from the amount of each covered loss. A separate deductible applies to each covered auto. If a single event results in loss to more than one covered auto, the deductible will apply separately to each.
                    """
                },
                {
                    "title": "SECTION III - COMPREHENSIVE COVERAGE",
                    "content": """
### A. Insuring Agreement

We will pay for direct and accidental loss to your covered auto or any non-owned auto, including their equipment, minus any applicable deductible shown in the Declarations. We will pay for loss to your covered auto caused by:

1. Other than collision, only if the Declarations indicate that Comprehensive Coverage is provided for that auto.
2. Missiles or falling objects; fire; theft or larceny; explosion or earthquake; windstorm; hail, water or flood; malicious mischief or vandalism; riot or civil commotion; contact with bird or animal; or breakage of glass.
                    """
                },
                {
                    "title": "SECTION IV - GENERAL PROVISIONS",
                    "content": """
### A. Policy Period and Territory

This policy applies only to accidents and losses which occur:
1. During the policy period as shown in the Declarations; and
2. Within the policy territory.

### B. Changes

This policy contains all the agreements between you and us. Its terms may not be changed or waived except by endorsement issued by us.
                    """
                },
                {
                    "title": "SECTION V - DEFINITIONS",
                    "content": """
### A. "Bodily injury" 
Means bodily harm, sickness or disease, including death that results.

### B. "Business" 
Includes trade, profession or occupation.

### C. "Covered auto" 
Means:
1. Any vehicle shown in the Declarations.
2. Any of the following types of vehicles on the date you become the owner:
   a. a private passenger auto; or
   b. a pickup, panel truck, van or similar type vehicle with a Gross Vehicle Weight Rating of 10,000 lbs. or less, not used for business purposes.

### D. "Property damage" 
Means physical injury to, destruction of or loss of use of tangible property.
                    """
                }
            ]
            
            # Attempt to retrieve policy from LlamaCloud if API key is provided
            policy_text = ""
            retrieval_success = False
            
            if llama_cloud_api_key:
                try:
                    with st.spinner("Retrieving policy document from LlamaCloud..."):
                        # Get index configuration from sidebar or session state
                        index_name = claim_index_name
                        org_id = llama_cloud_org_id
                        
                        try:
                            index = LlamaCloudIndex(
                                name=index_name,
                                project_name="Default",
                                organization_id=org_id,
                                api_key=llama_cloud_api_key
                            )
                            
                            # Create retriever
                            retriever = index.as_retriever(similarity_top_k=5)
                            
                            # Try multiple queries to get better results
                            queries = [
                                "full auto insurance policy document",
                                "complete auto insurance policy text",
                                "auto insurance policy terms and conditions"
                            ]
                            
                            all_docs = []
                            for query in queries:
                                try:
                                    docs = retriever.retrieve(query)
                                    if docs:
                                        all_docs.extend(docs)
                                        st.success(f"✅ Retrieved policy sections using query: '{query}'")
                                except Exception as e:
                                    st.warning(f"⚠️ Query '{query}' failed: {str(e)}")
                            
                            # Remove duplicates by ID
                            unique_docs = {}
                            for doc in all_docs:
                                unique_docs[doc.id_] = doc
                            
                            if unique_docs:
                                policy_text = "\n\n".join([doc.get_content() for doc in unique_docs.values()])
                                retrieval_success = True
                                st.success(f"✅ Successfully retrieved policy document with {len(unique_docs)} sections")
                            else:
                                st.warning("⚠️ No policy documents found in the index. Using sample policy instead.")
                        except Exception as e:
                            st.error(f"❌ Error initializing LlamaCloud index: {str(e)}")
                            st.info("ℹ️ Using sample policy document instead.")
                except Exception as e:
                    st.error(f"❌ Error retrieving policy document: {str(e)}")
                    st.info("ℹ️ Using sample policy document instead.")
            else:
                st.warning("⚠️ No LlamaCloud API key provided. Using sample documents instead. To view actual policy documents, please provide your API key in the sidebar.")
            
            # If retrieval failed or no API key, use sample policy
            if not retrieval_success:
                st.info("ℹ️ Displaying sample policy document. This is not your actual policy.")
                
                # Display sections based on search
                if search_term:
                    st.write(f"Showing sections containing: '{search_term}'")
                    found_match = False
                    
                    for section in policy_sections:
                        if search_term.lower() in section["title"].lower() or search_term.lower() in section["content"].lower():
                            found_match = True
                            with st.expander(f"{section['title']} (Match Found)", expanded=True):
                                st.markdown(section["content"])
                    
                    if not found_match:
                        st.warning(f"No matches found for '{search_term}'")
                else:
                    # No search term, display all sections
                    for i, section in enumerate(policy_sections):
                        with st.expander(section["title"], expanded=i == 0):  # Only first section expanded by default
                            st.markdown(section["content"])
            else:
                # Display the retrieved policy text
                if search_term:
                    st.write(f"Showing sections containing: '{search_term}'")
                    
                    # Split the policy text into sections and search
                    sections = policy_text.split("\n\n")
                    found_match = False
                    
                    for i, section in enumerate(sections):
                        if section.strip() and search_term.lower() in section.lower():
                            found_match = True
                            with st.expander(f"Section {i+1} (Match Found)", expanded=True):
                                # Highlight the search term
                                highlighted_text = section
                                search_term_lower = search_term.lower()
                                
                                # Find all occurrences of the search term (case insensitive)
                                for word in section.split():
                                    if search_term_lower in word.lower():
                                        highlighted_text = highlighted_text.replace(word, f"**{word}**")
                                
                                st.markdown(highlighted_text)
                    
                    if not found_match:
                        st.warning(f"No matches found for '{search_term}'")
                else:
                    # No search term, display all sections
                    sections = policy_text.split("\n\n")
                    for i, section in enumerate(sections):
                        if section.strip():
                            with st.expander(f"Section {i+1}", expanded=i < 3):  # First 3 sections expanded by default
                                st.markdown(section)
            
            # Add troubleshooting tips if using API but retrieval failed
            if llama_cloud_api_key and not retrieval_success:
                with st.expander("Troubleshooting Tips"):
                    st.markdown("""
                    ### Troubleshooting Tips for Policy Retrieval
                    
                    1. **Check API Key**: Ensure your LlamaCloud API key is correct
                    2. **Verify Index Name**: Make sure the index name matches your LlamaCloud index
                    3. **Organization ID**: Verify your organization ID is correct
                    4. **Index Content**: Ensure your index contains policy documents
                    5. **Network Connection**: Check your internet connection
                    
                    If problems persist, try restarting the application or checking the LlamaCloud dashboard.
                    """)
        
        else:  # Declarations Page
            st.subheader("Insurance Declarations Page")
            
            # Get policy number
            policy_number = st.text_input("Enter Policy Number", value="POLICY-")
            
            # Attempt to retrieve declarations from LlamaCloud if API key is provided
            declarations_text = ""
            retrieval_success = False
            
            # Always attempt to retrieve from LlamaCloud first if we have a policy number and API key
            if policy_number and llama_cloud_api_key:
                try:
                    with st.spinner("Retrieving declarations page from LlamaCloud..."):
                        # Get index configuration from sidebar or session state
                        index_name = declarations_index_name
                        org_id = llama_cloud_org_id
                        
                        try:
                            # Set a timeout for the connection attempt
                            declarations_index = LlamaCloudIndex(
                                name=index_name,
                                project_name="Default",
                                organization_id=org_id,
                                api_key=llama_cloud_api_key
                            )
                            
                            # Retrieve declarations with timeout handling
                            try:
                                # Try to get all documents in the index to see what's available
                                st.info("Searching for declaration files in LlamaCloud...")
                                
                                # First try to get the specific declaration file
                                docs = get_declarations_docs(policy_number, declarations_index=declarations_index)
                                
                                if docs:
                                    declarations_text = docs[0].get_content()
                                    retrieval_success = True
                                    st.success(f"✅ Successfully retrieved declarations page for {policy_number} from LlamaCloud")
                                    st.markdown(declarations_text)
                                else:
                                    # If specific retrieval failed, try to list all available documents
                                    try:
                                        retriever = declarations_index.as_retriever(similarity_top_k=10)
                                        all_docs = retriever.retrieve("declarations page")
                                        
                                        if all_docs:
                                            st.warning(f"⚠️ No exact match for {policy_number}, but found {len(all_docs)} declaration documents in LlamaCloud")
                                            
                                            # Display a list of available documents
                                            with st.expander("Available Declaration Documents"):
                                                st.markdown("### Available Declaration Documents in LlamaCloud:")
                                                for i, doc in enumerate(all_docs):
                                                    doc_id = getattr(doc, 'id_', f"Document {i+1}")
                                                    doc_content_preview = doc.get_content()[:100] + "..." if len(doc.get_content()) > 100 else doc.get_content()
                                                    st.markdown(f"**Document {i+1}:** {doc_id}")
                                                    st.markdown(f"**Preview:** {doc_content_preview}")
                                                    if st.button(f"View Document {i+1}"):
                                                        declarations_text = doc.get_content()
                                                        retrieval_success = True
                                                        st.success(f"✅ Displaying document {i+1}")
                                                        st.markdown(declarations_text)
                                        else:
                                            st.warning(f"⚠️ No declaration documents found in LlamaCloud for policy number: {policy_number}")
                                    except Exception as list_e:
                                        st.error(f"❌ Error listing available documents: {str(list_e)}")
                            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                                st.error(f"❌ Connection timeout when retrieving declarations: {str(e)}")
                                st.info("The server took too long to respond. Checking for local declaration files...")
                            except Exception as e:
                                st.error(f"❌ Error retrieving declarations: {str(e)}")
                                st.info("Checking for local declaration files...")
                        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                            st.error(f"❌ Connection timeout when initializing declarations index: {str(e)}")
                            st.info("The server took too long to respond. Checking for local declaration files...")
                        except Exception as e:
                            st.error(f"❌ Error initializing declarations index: {str(e)}")
                            st.info("Checking for local declaration files...")
                except Exception as e:
                    st.error(f"❌ Error retrieving declarations page: {str(e)}")
                    st.info("Checking for local declaration files...")
            elif not llama_cloud_api_key:
                st.warning("⚠️ No LlamaCloud API key provided. Checking for local declaration files...")
            
            # If LlamaCloud retrieval failed, try to get local declaration file
            if not retrieval_success:
                # Try to get local declaration file
                local_declaration = get_local_declaration_file(policy_number)
                if local_declaration:
                    st.success(f"✅ Found local declaration file for {policy_number}")
                    st.markdown(local_declaration)
                    retrieval_success = True
                else:
                    st.warning(f"No local declaration file found for {policy_number}")
            
            # Only fall back to sample declarations if both LlamaCloud and local file retrieval failed
            if not retrieval_success:
                # Show sample declarations for common policy numbers
                if policy_number == "POLICY-ABC123":
                    st.info("Showing sample declarations page as fallback for John Smith (POLICY-ABC123)")
                    st.markdown("""
                    # AUTO INSURANCE DECLARATIONS PAGE
                    
                    **Policy Number:** POLICY-ABC123  
                    **Policy Period:** January 10, 2023 to January 10, 2024  
                    **Named Insured:** John Smith  
                    **Address:** 123 Main Street, Anytown, CA 90210  
                    
                    ## Vehicle Information
                    
                    **Vehicle:** 2020 Toyota Camry  
                    **VIN:** 4T1BF1FK5CU123456  
                    **Usage:** Commute (15 miles one-way)  
                    **Garaging Address:** Same as above  
                    
                    ## Coverage Summary
                    
                    | Coverage Type | Limits | Premium |
                    |--------------|--------|---------|
                    | Bodily Injury Liability | $100,000/$300,000 | $420 |
                    | Property Damage Liability | $50,000 | $180 |
                    | Medical Payments | $5,000 | $60 |
                    | Uninsured Motorist | $100,000/$300,000 | $90 |
                    | **Collision** | **$500 deductible** | **$360** |
                    | Comprehensive | $500 deductible | $240 |
                    
                    **Total Semi-Annual Premium:** $1,350
                    
                    ## Discounts Applied
                    
                    - Multi-policy discount
                    - Safe driver discount
                    - Anti-theft device discount
                    
                    ## Special Endorsements
                    
                    None
                    
                    ## Important Notes
                    
                    This policy is subject to all terms, conditions and exclusions contained in the policy contract. In the event of a loss, please report claims promptly by calling our 24-hour claims service at 1-800-555-CLAIM.
                    """)
                elif policy_number == "POLICY-DEF456":
                    st.info("Showing sample declarations page as fallback for Alice Johnson (POLICY-DEF456)")
                    st.markdown("""
                    # AUTO INSURANCE DECLARATIONS PAGE
                    
                    **Policy Number:** POLICY-DEF456  
                    **Policy Period:** March 15, 2023 to March 15, 2024  
                    **Named Insured:** Alice Johnson  
                    **Address:** 456 Oak Avenue, Somewhere, CA 94123  
                    
                    ## Vehicle Information
                    
                    **Vehicle:** 2019 Honda Civic  
                    **VIN:** 19XFC2F59KE123789  
                    **Usage:** Personal (7,500 miles annually)  
                    **Garaging Address:** Same as above  
                    
                    ## Coverage Summary
                    
                    | Coverage Type | Limits | Premium |
                    |--------------|--------|---------|
                    | Bodily Injury Liability | $100,000/$300,000 | $380 |
                    | Property Damage Liability | $50,000 | $160 |
                    | Medical Payments | $5,000 | $50 |
                    | Uninsured Motorist | $100,000/$300,000 | $80 |
                    | **Collision** | **$250 deductible** | **$420** |
                    | Comprehensive | $250 deductible | $280 |
                    
                    **Total Semi-Annual Premium:** $970
                    
                    ## Discounts Applied
                    
                    - Good student discount
                    - Defensive driving course discount
                    - Paperless billing discount
                    
                    ## Special Endorsements
                    
                    None
                    
                    ## Important Notes
                    
                    This policy is subject to all terms, conditions and exclusions contained in the policy contract. In the event of a loss, please report claims promptly by calling our 24-hour claims service at 1-800-555-CLAIM.
                    """)
                elif policy_number:
                    st.warning(f"No declarations page found for policy number: {policy_number}")
                    st.info("Try entering a valid policy number or use 'POLICY-ABC123' or 'POLICY-DEF456' to see sample declarations.")
                else:
                    st.info("Please enter a policy number to view declarations.")
            
            # Add sample policy buttons for convenience
            st.markdown("### Sample Policy Numbers")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("John Smith (POLICY-ABC123)"):
                    st.session_state['policy_number'] = "POLICY-ABC123"
                    st.rerun()
            with col2:
                if st.button("Alice Johnson (POLICY-DEF456)"):
                    st.session_state['policy_number'] = "POLICY-DEF456"
                    st.rerun()
                    
            # Add a section to explore LlamaCloud index
            with st.expander("Explore LlamaCloud Index"):
                st.markdown("""
                ### Explore LlamaCloud Index
                
                If you're having trouble finding specific declaration files, you can explore the LlamaCloud index directly.
                """)
                
                explore_query = st.text_input("Search query:", value="declarations")
                
                if st.button("Search LlamaCloud"):
                    if llama_cloud_api_key:
                        try:
                            with st.spinner("Searching LlamaCloud..."):
                                declarations_index = LlamaCloudIndex(
                                    name=declarations_index_name,
                                    project_name="Default",
                                    organization_id=llama_cloud_org_id,
                                    api_key=llama_cloud_api_key
                                )
                                
                                # Create retriever with higher limit
                                retriever = declarations_index.as_retriever(similarity_top_k=20)
                                
                                # Retrieve documents
                                docs = retriever.retrieve(explore_query)
                                
                                if docs:
                                    st.success(f"Found {len(docs)} documents matching '{explore_query}'")
                                    
                                    for i, doc in enumerate(docs):
                                        doc_id = getattr(doc, 'id_', f"Document {i+1}")
                                        doc_content_preview = doc.get_content()[:150] + "..." if len(doc.get_content()) > 150 else doc.get_content()
                                        
                                        with st.expander(f"Document {i+1}: {doc_id}"):
                                            st.markdown(f"**Preview:** {doc_content_preview}")
                                            if st.button(f"View Full Document {i+1}"):
                                                st.markdown("### Full Document Content:")
                                                st.markdown(doc.get_content())
                                else:
                                    st.warning(f"No documents found matching '{explore_query}'")
                        except Exception as e:
                            st.error(f"Error searching LlamaCloud: {str(e)}")
                    else:
                        st.error("Please provide a LlamaCloud API key in the sidebar to search the index.")
    
    with tab3:
        st.header("Workflow Visualization")
        st.markdown("""
        This visualization shows the complete workflow of the auto insurance claim processing system.
        It illustrates how claims move through different stages from initial parsing to final decision.
        """)
        
        # Generate workflow visualization button
        if st.button("Generate Workflow Visualization"):
            with st.spinner("Generating workflow visualization..."):
                try:
                    # Generate the workflow visualization
                    html_content = generate_workflow_visualization()
                    
                    # Display the HTML content
                    st.components.v1.html(html_content, height=600, scrolling=True)
                    
                    # Provide download link
                    st.download_button(
                        label="Download Workflow HTML",
                        data=html_content,
                        file_name="auto_insurance_workflow.html",
                        mime="text/html"
                    )
                except Exception as e:
                    st.error(f"Error generating workflow visualization: {str(e)}")
    
    with tab4:
        st.header("About This Application")
        st.markdown("""
        ### Auto Insurance Claim Processor
        
        This application demonstrates an AI-powered workflow for processing auto insurance claims. It uses:
        
        - **LLMs (Large Language Models)** for understanding claim details and policy conditions
        - **Vector search** to retrieve relevant policy sections based on the claim
        - **Structured workflows** to ensure consistent processing of claims
        
        ### How It Works
        
        1. **Claim Parsing**: The system extracts key information from the claim document
        2. **Policy Retrieval**: Relevant sections of the insurance policy are retrieved
        3. **Coverage Analysis**: The system determines if the claim is covered under the policy
        4. **Decision Generation**: A structured recommendation is produced with payout details
        
        ### Technologies Used
        
        - **LlamaIndex**: For document indexing and retrieval
        - **OpenAI/Anthropic**: For language understanding and reasoning
        - **Streamlit**: For the web interface
        
        ### Data Privacy
        
        This application processes data locally and only sends necessary information to the LLM API.
        No claim data is stored permanently unless you explicitly save it.
        """)
        
        # Display sample policy and declaration information
        with st.expander("Sample Policy Information"):
            st.markdown("""
            ### Sample Policy Structure
            
            The system works with standard auto insurance policies that typically include:
            
            - **Liability Coverage**: Bodily injury and property damage
            - **Collision Coverage**: Damage to your vehicle from accidents
            - **Comprehensive Coverage**: Non-collision damage (theft, weather, etc.)
            - **Medical Payments**: Coverage for medical expenses
            - **Uninsured/Underinsured Motorist**: Protection when other drivers lack coverage
            
            ### Sample Declarations Page
            
            The declarations page contains policy-specific information like:
            
            - Policy number and period
            - Named insured and vehicle details
            - Coverage limits and deductibles
            - Premium amounts
            - Special endorsements
            """)

    # Footer
    st.markdown("---")
    st.markdown("Auto Insurance Claim Processor - Powered by LlamaIndex and OpenAI")

if __name__ == "__main__":
    main() 
