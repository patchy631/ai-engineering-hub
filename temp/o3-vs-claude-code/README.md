
# Compare Claud 3.7 Sonnet and OpenAI o3 using RAG over code (GitHub).

This project will also leverages [CometML Opik](https://github.com/comet-ml/opik) to build an e2e evaluation and observability pipeline for a RAG application.


## Installation and setup

**Get API Keys**:
   - [Opik API Key](https://www.comet.com/signup)  
   - [Open AI API Key](https://platform.openai.com/api-keys)
   - [Anthropic AI API Key](https://www.anthropic.com/api)

Add these to your .env file, refer ```.env.example```



**Install Dependencies**:
   Ensure you have Python 3.11 or later installed.
   ```bash
   pip install opik llama-index llama-index-agent-openai llama-index-llms-openai llama-index-llms-anthropic --upgrade --quiet
   ```

**Running the app**:

Run streamlit app using ``` streamlit run app.py```.

**Running Evaluation**:

You can run the code in notebook ```Opik for LLM evaluation.ipynb```.

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
