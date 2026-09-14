# Patient Case Summary Application

This application provides a Streamlit interface for analyzing patient case summaries using LlamaIndex and medical guidelines.

We'll use:
- @Synthea for generating synthetic patient data
- @OpenAI for condition mapping and summary generation
- @LlamaCloud for vector database storage of medical guidelines
- @LlamaIndex for orchestration and retrieval
- @Streamlit for the web interface

A demo is shown below:

[Video demo](demo.mp4)

## Setup and Installation Instructions

**Setup LlamaCloud**:

Get an API key from [LlamaCloud](https://cloud.llamaindex.ai/) and set it in the `.env` file as follows:

```bash
LLAMA_CLOUD_API_KEY=<YOUR_LLAMACLOUD_API_KEY> 
```

**Setup OpenAI**:

Get an API key from [OpenAI](https://openai.com/) and set it in the `.env` file as follows:

```bash
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY> 
```

**Install Dependencies**:
   Ensure you have Python 3.11 or later installed.
   ```bash
   pip install -r requirements.txt
   ```

**Run the app**:

   Run the app by running the following command:

   ```bash
   streamlit run app.py
   ```

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.