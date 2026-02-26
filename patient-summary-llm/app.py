import streamlit as st
import json
import time

def main():
    st.set_page_config(page_title="MediSummarize", page_icon="📋")
    
    # App header
    st.title("MediSummarize")
    st.subheader("AI-Powered Medical Record Summarization")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("Configuration")
        uploaded_file = st.file_uploader("Upload Patient JSON File", type=["json"])
        api_key = st.text_input("Enter API Key", type="password")
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("MediSummarize uses advanced AI to provide concise summaries of patient medical records, helping healthcare professionals save time and focus on patient care.")
    
    # Main content area
    if uploaded_file is not None:
        try:
            # Load and display the patient data
            patient_data = json.load(uploaded_file)
            
            st.header("Patient Information")
            
            # Create columns for patient info
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Name:** {patient_data.get('name', 'Not provided')}")
                st.markdown(f"**Age:** {patient_data.get('age', 'Not provided')}")
                st.markdown(f"**Gender:** {patient_data.get('gender', 'Not provided')}")
            
            with col2:
                st.markdown(f"**ID:** {patient_data.get('id', 'Not provided')}")
                st.markdown(f"**Date Admitted:** {patient_data.get('date_admitted', 'Not provided')}")
            
            # Display raw data in expandable section
            with st.expander("View Raw Patient Data"):
                st.json(patient_data)
            
            # Summarize button
            if st.button("Summarize Medical Record", type="primary"):
                if not api_key:
                    st.error("Please enter an API key to generate summary.")
                else:
                    # Show processing animation
                    with st.spinner("Generating summary..."):
                        # Simulate API call time
                        time.sleep(2)
                    
                    st.success("Summary generated successfully!")
                    
                    # Display the summary
                    st.header("Patient Summary")
                    
                    summary = """
                    **Patient Summary for Almeta56  **
                    
                    Patient Name: Almeta56 Buckridge80

                    Age: 13 years

                    Overall Assessment:
                    Almeta56 Buckridge80 is a 13-year-old female with active childhood asthma and atopic dermatitis. Her asthma is currently managed with fluticasone propionate and albuterol, aligning with guidelines for children with recurrent wheezing. Atopic dermatitis is managed with loratadine, though current guidelines suggest other treatments for moderate to severe cases. Regular follow-ups for asthma and potential adjustments in dermatitis management are recommended.

                    Condition Summaries:
                    - Childhood asthma (disorder):
                    Almeta's asthma is actively managed with fluticasone propionate and albuterol, which are appropriate for her age and condition. She had a follow-up encounter on October 5, 2024, indicating ongoing management. The current treatment aligns with guidelines recommending inhaled corticosteroids and short-acting beta-agonists for children with recurrent wheezing.
                    - Atopic dermatitis (disorder):
                    Almeta's atopic dermatitis isx   currently managed with loratadine, taken as needed. While this provides symptomatic relief, current guidelines for moderate to severe cases recommend considering other treatments such as dupilumab or phototherapy. No recent encounters suggest a need for reassessment of her treatment plan.
                                        """
                    
                    st.markdown(summary)
                    
                    # Download option
                    st.download_button(
                        label="Download Summary",
                        data=summary,
                        file_name="patient_summary.txt",
                        mime="text/plain"
                    )
                    
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    else:
        # Display placeholder when no file is uploaded
        st.info("👈 Please upload a patient JSON file from the sidebar to begin.")
        st.markdown("### How It Works")
        st.markdown("""
        1. Upload your patient JSON file
        2. Enter your API key
        3. Click 'Summarize Medical Record'
        4. Review the AI-generated summary
        5. Download the summary if needed
        """)

if __name__ == "__main__":
    main()