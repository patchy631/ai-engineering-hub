# World-class Document Processing Pipeline with Ground X

This application demonstrates how to build a Document Processing Pipeline that processes complex documents with tables, figures, and dense text using GroundX's state-of-the-art parsing technology. Users can upload documents and receive comprehensive insights including extracted text, semantic analysis, key insights, and interactive AI-powered document queries.

We use:

- Ground X for SOTA document processing and X-Ray analysis
- Streamlit for the UI
- Ollama for serving LLM locally

---

## Setup and Installation

Ensure you have Python 3.8.1 or later installed on your system.

Install dependencies:

```bash
uv sync
```

Copy `.env.example` to `.env` and configure the following environment variables:

```
GROUNDX_API_KEY=your_groundx_api_key_here
```

```bash
# Install Ollama from https://ollama.ai/
# Pull the required model
ollama pull phi3:mini
# Start Ollama service
ollama serve
```

Run the Streamlit app:

```bash
streamlit run app.py
```

## Project Structure

```
groundX-doc-pipeline/
├── app.py                          # Main Streamlit application (uses groundx_utils.py)
├── groundx_utils.py                # Utility functions for Ground X operations
├── .env                            # Environment variables (create from .env.example)
├── file/                           # Folder containing files for running evaluation
└── README.md                       # This file

📁 Evaluation Tools:
├── evaluation_geval.py             # GEval framework evaluation
└── run_evaluation_cli.py           # CLI evaluation runner
```

## Usage

1. Upload a document using the sidebar (supports PDF, PNG, JPG, JPEG, DOCX)
2. Wait for the document to be processed by Ground X
3. Explore the X-Ray analysis results in different tabs:
   - JSON Output: Raw analysis data
   - Narrative Summary: Extracted narratives
   - File Summary: Document overview
   - Suggested Text: AI-suggested content
   - Extracted Text: Raw text extraction
   - Keywords: Document keywords
4. Use the chat interface to ask questions about your document

## Features

The app implements a world-class document processing workflow:

- **Ground X Bucket Management**: Automatic bucket creation and document organization
- **Document Ingestion**: Support for PDF, Word docs, images, and more
- **X-Ray Analysis**: Rich structured data with summaries, page chunks, keywords, and metadata
- **Context Engineering**: Intelligent context preparation for LLM queries
- **AI Chat Interface**: Interactive Q&A powered by local LLM

---

## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
