# Patient Case Summary Generation Using RAG 

This project builds a case summary generator for patient data.

We use:
- Synthea for generating synthetic patient data
- OpenAI for condition mapping and summary generation
- LlamaCloud for vector database storage of medical guidelines
- LlamaIndex for orchestration and retrieval
- Streamlit for the web interface

## Installation and setup

**Setup OpenAI**:

Get an API from OpenAI and set it in the .env file as follows:
   ```bash
   OPENAI_API_KEY=<YOUR_API_KEY> 
   ```

**Setup LlamaCloud**:

1. Download sample medical guidelines (PDF files) from the `/data` directory
2. Create a vector index on LlamaCloud:
   - Sign up/login to [LlamaCloud](https://cloud.llamaindex.ai/)
   - Create a new project (or use existing)
   - Upload the medical guideline PDFs and create an index
3. Configure your environment variables in the `.env` file:
   ```bash
   LLAMACLOUD_API_KEY=your_llamacloud_api_key_here
   GUIDELINE_INDEX_NAME=medical_guidelines_0
   GUIDELINE_PROJECT_NAME=llamacloud_demo
   GUIDELINE_ORG_ID=your_organization_id_here
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

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
