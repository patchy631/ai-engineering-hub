# Patient Case Summary Workflow

A Streamlit application that generates comprehensive summaries and enables Q&A on patient medical records using LlamaIndex and local LLMs.

## Features

- Upload patient medical records (text format)
- Generate structured patient summaries 
- Answer specific questions about patient cases
- Runs completely locally - no data leaves your machine
- Privacy-focused with local LLM and embeddings

## Architecture

![Architecture Diagram](images/architecture_diagram.png)

This application uses:
- Gemma 3 (1B parameter model) via Ollama for text generation
- HuggingFace's all-MiniLM-L6-v2 for embeddings
- LlamaIndex for document processing and knowledge extraction
- Streamlit for the user interface

## Prerequisites

- Python 3.9+
- [Ollama](https://ollama.ai/) installed with the Gemma 3 model

## Installation

1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/ai-engineering-hub.git
cd ai-engineering-hub/projects/patient-case-summary