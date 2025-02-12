
# Agentic RAG using CrewAI

This project leverages CrewAI to build an Agentic RAG that can search through your docs and fallbacks to web search in case it doesn't find the answer in the docs, have option to use either of deep-seek-r1 or llama 3.2 that runs locally. More details un Running the app section below!

Before that, make sure you grab your FireCrawl API keys to search the web.

**Get API Keys**:
   - [FireCrawl](https://www.firecrawl.dev/i/api)

### Watch Demo on YouTube
[![Watch Demo on YouTube](https://github.com/patchy631/ai-engineering-hub/blob/main/agentic_rag/thumbnail/thumbnail.png)](https://youtu.be/O4yBW_GTRk0)


## Installation and setup

**Get API Keys**:
   - [FireCrawl](https://www.firecrawl.dev/i/api)


**Install Dependencies**:
   Ensure you have Python 3.11 or later installed.
   ```bash
   pip install crewai crewai-tools chonkie[semantic] markitdown qdrant-client fastembed
   ```

**Running the app**:

To use deep-seek-rq use command ``` streamlit run app_deep_seek.py ```, for llama 3.2 use command ``` streamlit run app_llama3.2.py ```

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
