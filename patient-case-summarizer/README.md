# Patient Case Summarizer

The Patient Case Summary Generator is a Streamlit app that lets healthcare professionals upload patient JSON data to create concise AI-generated summaries. It uses medical guidelines to detail conditions, encounters, and recommendations.

We use:
- LLamaCloudIndex for medical guideline retrieval
- OpenAI for processing patient data and generating case summary
- Streamlit to build the UI.

A demo is shown here:
[Video demo](demo.mov)

## Installation and setup

**Setup LlamaCloud**:

1. SignUp to LLamaCloud
2. Upload sample medical guidelines
3. Create an index
4. Get an API key from [LLamaCloud](https://cloud.llamaindex.ai/) and set it in the `.env` file as follows:

```bash
LLAMA_CLOUD_API_KEY=<YOUR_API_KEY> 
```

**Setup OpenAI key**:

Set it in the `.env` file as follows:

```bash
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY> 
```

**Install Dependencies**:

Ensure you have Python 3.11 or later installed
   ```bash
   pip install streamlit llama_index pydantic
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
