
# RAG over excel sheets

This project leverages LlamaIndex and IBM's Docling for RAG over excel sheets. You can also use it for ppts and other complex docs,

## Installation and setup

**Install Dependencies**:
   Ensure you have Python 3.11 or later installed.
   ```bash
   pip install -q --progress-bar off --no-warn-conflicts llama-index-core llama-index-readers-docling llama-index-node-parser-docling llama-index-embeddings-huggingface llama-index-llms-huggingface-api llama-index-readers-file python-dotenv llama-index-llms-ollama
   ```


   Download the Qwen3 LLM locally
   ```bash
   ollama pull qwen3
   ```

---

## 🐞 Issue You may face
### 1. Pickle Error with `@st.cache_resource`
The app might fail with: `An error occurred: cannot pickle 'classmethod' object`

> ✅ **Solution**: Don’t cache non-picklable objects like the Ollama client or embeddings. Instead, store them in Streamlit's session state:
> ```python
> if "llm_client" not in st.session_state:
>     st.session_state.llm_client = Ollama(model="llama3.2")
> ```

### 2. App Extremely Slow (incase Used another Large Model)
This often happens due to high memory usage. `ollama` was observed using 10+ GB RAM on an 8 GB Mac, leading to heavy swapping. Large embedding models like `bge-large-en-v1.5` also consume significant memory.

> ✅ **Solution**:
> * **Use smaller Ollama models**:
>     * `qwen2:1.5b`
>     * `llama3.2:1b`
>     * `mistral:7b-instruct-q4_K_M`
> * **Use smaller embeddings**:
>     ```python
>     HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
>     ```

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
