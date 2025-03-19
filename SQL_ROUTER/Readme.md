# Hybrid RAG System: SQL + Document Retrieval

A question-answering app combining SQL queries and document retrieval to provide insights on US cities.

## Tech Stack

- **LlamaIndex** for query routing
- **SQLite** for structured data (population, state, etc.)
- **LlamaCloud** for document retrieval (Wikipedia-based context)
- **Groq API** for LLaMA 3-powered responses
- **Streamlit** for the chat UI

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/hybrid-rag-system.git && cd hybrid-rag-system
   ```
2. **Set up a virtual environment**
   ```bash
   python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Create a `.env` file** with API keys:
   ```bash
   GROQ_API_KEY=your_groq_api_key
   LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key
   ```
5. **Run the app**
   ```bash
   streamlit run app.py
   ```

## Supported Cities

- New York City, Los Angeles, Chicago, Houston, Miami, Seattle

## Example Queries

- "Which city has the highest population?"
- "What is the historical name of Los Angeles?"
- "Where is the Space Needle located?"

## Acknowledgements

- [LlamaIndex](https://github.com/jerryjliu/llama_index)
- [Groq](https://groq.com)
- [Streamlit](https://streamlit.io)
- [HuggingFace](https://huggingface.co/)

## Typefully Draft Link

This section is provides you the typefully draft llink for the set of twitter posts I have created as given in the task .

- [Draft Link ](https://typefully.com/t/rs9pLhH)
