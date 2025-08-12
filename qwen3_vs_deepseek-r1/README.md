# Alibaba's Qwen3 and DeepSeek-R1 compared using RAG

This tutorials build a RAG app powered by [LlamaIndex](https://www.llamaindex.ai/) to compare Qwen3 and DeepSeek-R1. We have used [Opik](https://github.com/comet-ml/opik) for evaluation and observability, which is 100% open-source and nicely integrates with alsmot all popular frameworks.

### Setup

To sync dependencies, run:

```sh
uv sync
```


Download the Qwen3 and DeepSeek-R1 models from [Ollama](https://ollama.com/library) as follows:

```sh
ollama pull qwen3
ollama pull deepseek-r1
```

### Environment Variables

You need to set up the following environment variables:

```sh
OPIK_API_KEY=...
OPIK_USERNAME=...
```

Ensure these variables are configured correctly before running the application use `.env.example` as reference and create your own `.env` file.

Run the streamlit app using `streamlit run app.py`

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.

