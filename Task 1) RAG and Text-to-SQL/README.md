# Advanced RAG: Combining RAG and Text-to-SQL

This project demonstrates an advanced Retrieval-Augmented Generation (RAG) system that combines semantic search through RAG and structured database queries through Text-to-SQL in a single interface. The application uses a custom agent workflow that intelligently routes user queries to the appropriate engine based on the nature of the question.

## Project Overview

The application is built with the following key features:

- **Dual Query Engines**: Combines text-to-SQL capabilities for structured data queries and RAG for semantic information retrieval
- **Intelligent Query Routing**: Automatically determines whether to use SQL database or LlamaCloud for each query
- **Custom Workflow**: Uses LlamaIndex's workflow system to create an agent that can properly manage tools and responses
- **Streamlit Interface**: Provides a user-friendly chat interface to interact with the system

## Setup Instructions

### Prerequisites

- Python 3.8+
- A valid [OpenAI](https://platform.openai.com/api-keys) API key
- A LlamaCloud account and API key

### Installation

1. Clone the repository or download the code
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root directory with the following variables:

```
OPENAI_API_KEY = <your_openai_api_key>
LLAMA_CLOUD_API_KEY = <your_llama_cloud_api_key>
LLAMA_CLOUD_INDEX_NAME = <your_index_name>
LLAMA_CLOUD_PROJECT_NAME = <your_project_name>
LLAMA_CLOUD_ORG_ID = <your_organization_id>
```

### Creating Your LlamaCloud Index

1. Sign up for a [LlamaCloud](https://cloud.llamaindex.ai/) account if you don't have one
2. Create a new index in LlamaCloud
3. Download Wikipedia pages for the following cities as PDFs:
- [New York City](https://en.wikipedia.org/wiki/New_York_City)
- [Los Angeles](https://en.wikipedia.org/wiki/Los_Angeles)
- [Chicago](https://en.wikipedia.org/wiki/Chicago)
- [Houston](https://en.wikipedia.org/wiki/Houston)
- [Miami](https://en.wikipedia.org/wiki/Miami)
- [Seattle](https://en.wikipedia.org/wiki/Seattle)
4. Upload these PDFs to your LlamaCloud index

### Running the Streamlit App

Run the app by running the following command:

```bash
streamlit run app.py
```
## 📬 Stay Updated with Our Newsletter!
Get a FREE Data Science eBook 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. Subscribe now!
[![Join Our Newsletter](assets/join_ddods.png)](https://join.dailydoseofds.com/)

## Contribution
Contributions are welcome! Please fork the repository and submit a pull request with your improvements.