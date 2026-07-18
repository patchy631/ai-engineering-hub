<h1 align="center">ClaimSonic: Auto Claim Agent 🚗</h1>
  <p align="center">
    ClaimSonic is an intelligent auto insurance claim processing application designed to streamline claim assessments. Leveraging advanced technologies such as LlamaIndex, OpenAI GPT-4o, and Streamlit, this project automates the extraction of claim details, retrieval of relevant policy documents, and generation of claim recommendations. The goal is to support claim adjusters by providing accurate, data-driven decision insights quickly. 
 <br>
     <br />
    <a href="https://github.com/vamshi694/"><strong>Explore the repo »</strong></a>
    <br />
    <br />
    <a href="https://www.youtube.com/watch?v=oKSzV4b5e1g">View Demo</a> 
    ·
    <a href="https://typefully.com/t/sjcCzxz">View Tweet</a>
  </p>

--- 

## Architecture Diagram

Below is an overview of the project architecture:

![Architecture Diagram](https://raw.githubusercontent.com/vamshi694/ai-engineering-hub/main/Vamshi_ClaimSonic_Auto_Insurance_Claims_Agent/flow_diagrams/ClaimSonic_whole_arch.png "Project Architecture")

Below is an holistic user->company journey in dealing with claims:

![Architecture Diagram](https://raw.githubusercontent.com/vamshi694/ai-engineering-hub/main/Vamshi_ClaimSonic_Auto_Insurance_Claims_Agent/flow_diagrams/claims_whole_flow.png "Project Architecture")


---

## Project Structure

- 📦 Prompts - Markdown prompt files for guiding LLM responses
- 🚀 main.py - Main application script for running the workflow in streamlit
- 🧾 flow_diagrams - Has the user -> company adjuster flow + AI workflow
- 🧪 notebooks - Jupyter notebooks with running code, development and vector db creater code snippets
- 🔍 pyproject.toml - Project configuration and dependency management
- 🧾 uv.lock - Lock file for virtual environment (using uv)

---

### Built With

* **LlamaIndex**: Workflows for orchestration & indexing the sample [California Personal Automobile Policy](https://nationalgeneral.com/forms_catalog/CAIP400_03012006_CA.pdf) against which claims are validated. This also indexes the per-user declaration documents. Make sure to download the document and upload it to [LlamaCloud](https://cloud.llamaindex.ai/).
* **OpenAI GPT-4o**: Provides advanced natural language understanding and structured output to assess claims and generate recommendations.
* **Streamlit**: Builds an interactive user interface for claim input and real-time workflow monitoring.
* **uv**: Manages the virtual environment and dependencies, ensuring reproducible builds.
* **Vercel**: Used Vercel to build and host a mock auto insurance company portal for customers and claims adjusters to evaluate users claims

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Installation and setup

Get an API key from [llamaindex](https://cloud.llamaindex.ai/), LLM api key and set it in the `.env` file as follows:
 
```bash
OPENAI_API_KEY = 
LLAMA_ORG_ID = 
LLAMA_CLOUD_API_KEY= 
```
---

**Install Dependencies**:
   Ensure you have Python 3.12 or later installed. First install [uv](https://github.com/your-repo/uv) for virtual environment through pip and then use it along with the pyproject.toml to install dependencies
   
   ```python

   pip install uv

   ```
   
   ```bash
   uv venv --python 3.12 [Make sure to use this virtual env before sync with the uv.lock file]
   uv init
   uv sync
   ```
---
**Run the app**:

   Run the app by running the following command:

   ```bash
   streamlit run main.py
   ```
---


## Contribution

This is part of a challenge round for [Daily Dose of Data Science Newsletter](https://join.dailydoseofds.com)
