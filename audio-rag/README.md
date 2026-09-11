# RAG over audio using Speechmatics

This project builds a RAG app over audio files.
We use:
- Speechmatics to generate speaker-labeled transcripts from audio files.
- LlamaIndex for orchestrating the RAG app.
- Voyage AI (`voyage-context-3`) for contextualized chunk embeddings.
- MongoDB Atlas Vector Search for storing the embeddings.
- OpenRouter (DeepSeek V3.2) as the LLM.
- Streamlit to build the UI.

## Installation and setup

**Setup Speechmatics**:

Get an API key from [Speechmatics](https://portal.speechmatics.com/) and set it in the `.env` file as follows:

```bash
SPEECHMATICS_API_KEY=<YOUR_API_KEY>
```

**Setup Voyage AI**:

Get an API key from [Voyage AI](https://www.voyageai.com/) for the `voyage-context-3` contextualized embedding model, then set it in the `.env` file as follows:

```bash
VOYAGE_API_KEY=<YOUR_API_KEY>
```

**Setup MongoDB Atlas**:

Create a free cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register), then set your connection string in the `.env` file as follows:

```bash
MONGODB_URI=<YOUR_MONGODB_ATLAS_CONNECTION_STRING>
```

**Setup OpenRouter**:

Get an API key from [OpenRouter](https://openrouter.ai/) and set it in the `.env` file as follows:

```bash
OPENROUTER_API_KEY=<YOUR_OPENROUTER_API_KEY>
```

**Install dependencies**:

Ensure you have Python 3.11 or later installed.

```bash
uv sync
```

**Run the app**:

```bash
uv run streamlit run app.py
```

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
