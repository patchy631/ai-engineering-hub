# Patient Case Summarizer

This project includes building a summary of patient's case based on previous medical history and prescriptions.
Key components:
- LlamaIndex for doc indexing and creating workflow 
- Streamlit for the UI.

## Installation and setup

**Setup LLAMA INDEX**:

Get an API key from [LLAMA CLOUD](https://cloud.llamaindex.ai/login) and set it in the `.env` file as follows:

```bash
LLAMA_CLOUD_API_KEY=<YOUR_LLAMACLOUD_API_KEY> 
```

or alternatively you can set it in the streamlit app UI after running.

**Setup OPEN AI Key**:

Set the key to use openai models in the `.env` file as follows:

```bash
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY> 
```

or alternatively you can set it in the streamlit app UI after running.

**Install Dependencies**:
   Ensure you have Python 3.11 installed.
   
   ```bash
   pip install -r requirements.txt
   ```

**Run the app**:

   Run the app by running the following command:

   ```bash
   streamlit run streamlit_app.py
   ```

---


[Twitter Thread](https://typefully.com/t/mlSflab)