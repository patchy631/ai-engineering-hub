# Multimodal Agentic RAG System

This application implements a Retrieval-Augmented Generation (RAG) system that combines audio transcription, vector database storage, and CrewAI Flows for orchestrated processing. The system allows users to ingest multimodal data (audio, text) into a vector database and then query it using voice input.

We use:
- CrewAI Flows for orchestrated processing
- AssemblyAI for audio transcription
- Milvus for vector database storage
- OpenAI for embeddings and LLM

---
## Setup and Installation

Ensure you have Python 3.10 or later installed on your system.

Install dependencies:
```bash
pip install -r requirements.txt
```

Start Milvus using Docker:
```bash
docker-compose up -d
```

Copy `.env.example` to `.env` and configure the following environment variables:
```
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

Run the application:
```bash
python main.py
```

## Usage

1. **Data Ingestion**: Place your data (audio, text files) in the `data/` directory
2. **System Setup**: The system automatically processes and stores data in the vector database
3. **Voice Input**: Record your voice query using the microphone
4. **Audio Transcription**: AssemblyAI transcribes your voice to text
5. **Vector Search**: OpenAI generates embeddings and searches Milvus vector database
6. **Research Agent**: CrewAI Research Agent analyzes search results and finds relevant information
7. **Response Agent**: CrewAI Response Agent synthesizes information into comprehensive answer
8. **Final Response**: View the agent-generated response based on your knowledge base

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.


