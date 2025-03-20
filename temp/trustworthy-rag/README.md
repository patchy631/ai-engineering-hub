# Trustworthy RAG over complex documents using TLM and LlamaParse

The project uses a trustworthy language model from Cleanlab (TLM) that prvides a confidence score and reasoning on the generated output. It also uses [LlamaParse](https://docs.cloud.llamaindex.ai/llamacloud/getting_started/api_key) to parse complex documents into LLM ready clean markdown format.

Before you start, grab your API keys for LlamaParse and TLM

- [LlamaParse API Key](https://docs.cloud.llamaindex.ai/llamacloud/getting_started/api_key)
- [Cleanlab TLM API Key](https://tlm.cleanlab.ai/)

---
## Setup and installations

**Setup Environment**:
- Paste your API keys by creating a `.env`
- Refer `.env.example` file


**Install Dependencies**:
   Ensure you have Python 3.11 or later installed.
   ```bash
   pip install llama-index-llms-cleanlab llama-index llama-index-embeddings-huggingface
   ```
**Running the app**:
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
