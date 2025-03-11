import streamlit as st
import json
import workflow  # Ensure workflow.py exists with a 'process' function

st.title("🏥 Patient Case Summary Generator")

# File Upload
uploaded_file = st.file_uploader("almeta_buckridge.json", type=["json"])

if uploaded_file:
    try:
        # Load JSON safely
        patient_data = json.load(uploaded_file)

        # Ensure workflow module has the right function
        if hasattr(workflow, "process"):
            result = workflow.process(patient_data)  # ✅ Call the function only after defining patient_data
        else:
            raise AttributeError("The 'workflow' module is missing the 'process' function.")

        # Display the summary
        st.subheader("📝 Case Summary")
        
        if "case_summary" in result:
            st.text(result["case_summary"])  # No need for `.render()`
        else:
            st.warning("No 'case_summary' found in the processed data.")

    except json.JSONDecodeError:
        st.error("❌ Invalid JSON file. Please check the format.")
    except AttributeError as e:
        st.error(f"❌ Attribute Error: {e}")
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
