# Patient Case Summary Workflow

This project builds an AI-powered medical case summarization app that extracts key patient conditions, matches them with clinical guidelines, and generates a structured case summary for clinicians.

We use:
- Synthea to generate synthetic patient data.
- LlamaIndex to retrieve relevant medical guidelines.
- LlamaCloud (or a local VectorStoreIndex) for guideline matching.
- Streamlit to build an interactive UI.

  ## Installation and Setup
  **Set Up LlamaCloud** (Optional)

  If using LlamaCloud, get an API key from LlamaCloud and set it in the .env file:

  `LLAMA_CLOUD_API_KEY=<YOUR_LLAMA_CLOUD_API_KEY>`

  **Install Dependencies**

  Ensure you have Python 3.11+ installed, then run:

  `pip install streamlit llama-index llama-index-indices-managed-llama-cloud llama-cloud pydantic`

  **Run the app**

  Start the Streamlit UI with:

  `streamlit run app.py`

  Link to X thread: https://x.com/marziabil/status/1900598708682846514 

  

  
