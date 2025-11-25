# Paralegal AI Assistant

⚖️ An intelligent paralegal AI assistant that analyzes PDF documents and provides comprehensive answers through advanced RAG (Retrieval-Augmented Generation) with web search fallback capabilities.

## Setup Instructions

### Prerequisites
- Python 3.13+
- OpenAI API key
- Firecrawl API key (optional)
- Docker (for self-hosted Milvus)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd paralegal-agent-crew
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   FIRECRAWL_API_KEY=your_firecrawl_api_key_here
   ```

3. **Install dependencies with UV:**
   ```bash
   uv sync
   ```

### Option A: Using Local Milvus (Default)
The project works with embedded Milvus out of the box. Simply run:

```bash
uv run streamlit run app.py
```

### Option B: Self-Hosted Milvus with Docker

4. **Set up Milvus vector database:**
   
   **Quick Setup (Recommended):**
   ```bash
   # Download and run Milvus installation script
   curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed.sh
   bash standalone_embed.sh start
   ```
   
   **Alternative - Docker Compose:**
   ```bash
   # Download docker-compose file
   wget https://github.com/milvus-io/milvus/releases/download/v2.0.2/milvus-standalone-docker-compose.yml -O docker-compose.yml
   
   # Start Milvus
   docker-compose up -d
   ```

5. **Update configuration for external Milvus:**
   Modify `config/settings.py` to point to your Milvus instance:
   ```python
   milvus_host: str = "localhost"
   milvus_port: int = 19530
   ```

6. **Run the application:**
   ```bash
   uv run streamlit run app.py
   ```

7. **Open your browser and go to `http://localhost:8501`**

### Milvus Management
- **Milvus WebUI**: Access at `http://127.0.0.1:9091/webui/`
- **Stop Milvus**: `bash standalone_embed.sh stop`
- **Delete Milvus**: `bash standalone_embed.sh delete`

## About the Project

This paralegal AI assistant combines multiple technologies to provide intelligent document analysis:

- **Document Processing**: Extracts and chunks PDF documents for analysis
- **Vector Database**: Uses Milvus with binary quantization for efficient similarity search
- **Embeddings**: BGE-large-en-v1.5 model for high-quality text representations
- **Intelligent Routing**: Automatically evaluates response quality and triggers web search when needed
- **Web Search Integration**: Firecrawl integration for additional context from the web
- **Workflow Management**: CrewAI-powered agentic workflows for complex query handling

The system provides an interactive Streamlit interface where users can upload PDF documents, ask questions, and receive comprehensive answers with citations and sources. It automatically determines when to use document knowledge versus web search to provide the most accurate and complete responses.