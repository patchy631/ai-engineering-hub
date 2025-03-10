# RAG and Text-to-SQL Query in Single Interface
This project builds a RAG and Text-to-SQL query app in a single interface. We use:
- OpenAI to power the LLM capabilities
- LlamaIndex for orchestrating the RAG app
- SQL Database for storing the data from CSV files
- Streamlit to build the UI

A demo is shown below:

[Video demo](demo.mp4)

Twitter Thread Draft:

[X Thread](https://typefully.com/t/dJMjlT7)

## Installation and setup

**Setup OpenAI**:
Get an API key from [OpenAI](https://openai.com/) and set it in the `.env` file as follows:
```bash
OPENAI_API_KEY="your-openai-api-key"
```

**Setup Llama Cloud**:
Get an API key from [Llama Cloud](https://llamacloud.ai/) and set it in the `.env` file as follows:
```bash
name="your-llama-cloud-index-name"
project_name="your-llama-cloud-project-name"
organization_id="your-llama-cloud-organization-id"
api_key="your-llama-cloud-api-key"
```
Note: The app uses an in-memory SQLite database that's recreated for each session.

**Install Dependencies**:
Ensure you have Python 3.7+ installed.
```bash
pip install streamlit llama-index openai sqlalchemy python-dotenv nest-asyncio
```

**Run the app**:
Run the app by running the following command:
```bash
streamlit run app.py
```

---
## How to Use

1. Upload a CSV file using the sidebar uploader
2. Ask questions in natural language in the text input field, such as:
   - "What is the population of the largest city in the dataset?"
   - "Tell me about the history of New York City"
   - "Which states have cities with populations over 1 million?"
3. The application will automatically determine whether to use SQL or RAG to answer your question and display the results.

The system intelligently routes queries between:
- A Text-to-SQL tool that translates natural language to SQL queries for data analysis
- A Llama Cloud RAG tool that retrieves information from a knowledge base for contextual answers

---
## Customization
You can customize the application by:
- Modifying the LLM model in `main.py` (currently using "gpt-3.5-turbo")
- Updating the Llama Cloud index configuration to use your own knowledge base
- Extending the workflow with additional tools for more capabilities

---
## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)
[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)
---

## Contribution
Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
