# RAG + Text-to-SQL for City Knowledge

## Overview

This project enables you to create a custom agent that can query either your LlamaCloud index for retrieval-augmented generation (RAG)-based retrieval or a separate SQL query engine as a tool. In this example, we'll use PDFs of Wikipedia pages of US cities and a SQL database containing city populations and states as documents.

A **Streamlit-based application** (`app.py`) provides a user-friendly interface with:

- A **form in the left-hand pane** to set up environment variables (API keys, index details, and database connections).
- A **chat interface in the right-hand pane** to interact with the RAG pipeline, allowing users to retrieve knowledge from both structured (SQL) and unstructured (LlamaCloud) sources.

### Why This Matters

By integrating OpenAI's powerful language models with LlamaIndex's structured retrieval capabilities, you can build a highly efficient knowledge retrieval system. This approach allows you to:

- Leverage both unstructured text documents and structured SQL data to provide more accurate and contextual responses.
- Use OpenAI's API for intelligent query interpretation and summarization.
- Seamlessly index and retrieve data using LlamaIndex, making document and database queries more accessible.
- Offer an **interactive interface** for real-time querying via Streamlit.

---

## Prerequisites

This project requires API access to OpenAI and LlamaIndex Cloud. Follow the steps below to sign up, generate API keys, and build an index with relevant documents.

---

## Step 1: Set Up a Virtual Environment

Navigate to the project directory:

```sh
cd ai-engineering-hub/rag-with-txt2sql
```

To keep dependencies isolated, it is recommended to use a virtual environment. Follow these steps:

### Create and Activate a Virtual Environment

On **Windows**:

```sh
python -m venv venv
venv\Scripts\activate
```

On **Mac/Linux**:

```sh
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

After activating the virtual environment, ensure you are in the project directory:

```sh
cd ai-engineering-hub/rag-with-txt2sql
```

Then, install the required dependencies using the `requirements.txt` file:

```sh
pip install -r requirements.txt
```

To deactivate the virtual environment when done:

```sh
deactivate
```

---

## Step 2: Sign Up for OpenAI API Access

1. Navigate to [OpenAI API](https://openai.com/)
2. Sign up for an account if you do not already have one.
3. Once logged in, go to the [API keys](https://platform.openai.com/account/api-keys) section.
4. Click **Create new secret key** and store the generated key securely.

---

## Step 3: Sign Up for LlamaIndex Cloud

1. Visit [LlamaIndex Cloud](https://cloud.llamaindex.ai/)
2. Sign up for an account.
3. Once logged in, go to the **API Keys** section.
4. Generate a new API key and save it securely.

---

## Step 4: Prepare and Upload Documents to LlamaIndex Cloud

### Download Wikipedia Pages as PDFs

Download the following Wikipedia pages as PDFs:

- [New York City](https://en.wikipedia.org/wiki/New_York_City)
- [Los Angeles](https://en.wikipedia.org/wiki/Los_Angeles)
- [Chicago](https://en.wikipedia.org/wiki/Chicago)
- [Houston](https://en.wikipedia.org/wiki/Houston)
- [Miami](https://en.wikipedia.org/wiki/Miami)
- [Seattle](https://en.wikipedia.org/wiki/Seattle)

#### Instructions for Saving as PDF

1. Open each Wikipedia page in a browser.
2. Press **Ctrl-P (Windows/Linux)** or **Cmd-P (Mac)** to open the print dialog.
3. Change the destination to **Save as PDF**.
4. Click **Save** and store the file on your local machine.

### Upload PDFs to LlamaCloud

1. Log in to your [LlamaIndex Cloud](https://cloud.llamaindex.ai/) account.
2. Create a **new index**.
3. Upload the downloaded PDFs into your newly created index.

---

## Step 5: Use the API Keys and Index Parameters in Your Project

Once you have generated your OpenAI and LlamaIndex API keys, you can configure your project to use them by setting them as environment variables:

```sh
export OPENAI_API_KEY="your-openai-api-key"
export LLAMA_INDEX_API_KEY="your-llamaindex-api-key"
export LLAMA_INDEX_NAME="your index name"
export LLAMA_INDEX_PROJECT_NAME="Default"
export LLAMA_INDEX_ORGANIZATION_ID="your org id"
```


## Running the Streamlit App

Once the environment variables are set, you can run the Streamlit app to interact with the RAG pipeline:

```sh
streamlit run app.py
```

This will open a web-based UI with:

- **Left pane**: A form to enter API keys and environment variables.
- **Right pane**: A chat interface to interact with the RAG pipeline.

---

## Happy Exploring!

