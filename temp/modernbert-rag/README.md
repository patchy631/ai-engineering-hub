# LLama3.2-RAG application powered by ModernBert

This project leverages a locally Llama 3.2 to build a RAG application to **chat with your docs** powered by
- ModernBert for embeddings.
- Llama 3.2 for the LLM.
- Streamlit to build the UI.

## Demo

Watch the demo video:

![Watch the demo](modernbert-demo.mp4)


## Installation and setup

**Setup Transformers**:

As of now, ModernBERT requires transformers to be installed from the (stable) main branch of the transformers repository. After the next transformers release (4.48.x), it will be supported in the python package available everywhere.

So first, create a new virtual environment.
    
```bash
python -m venv modernbert-env
source modernbert-env/bin/activate
```

Then, install the latest transformers.

```bash
pip install git+https://github.com/huggingface/transformers
```

**Setup Ollama**:
   ```bash
   # setup ollama on linux 
   curl -fsSL https://ollama.com/install.sh | sh
   # pull llama 3.2
   ollama pull llama3.2 
   ```


**Install Dependencies (in the virtual environment)**:
   Ensure you have Python 3.11 or later installed.
   ```bash
   pip install streamlit ollama llama_index-llms-ollama llama_index-embeddings-huggingface
   ```

## Running the app

Finally, run the app.

```bash
streamlit run rag-modernbert.py
```


---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
