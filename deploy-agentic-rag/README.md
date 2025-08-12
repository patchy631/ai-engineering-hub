# 100% private Agentic RAG API

This is a simple API that uses CrewAI and LitServe to create a 100% private Agentic RAG API.

## How to use

1. Clone the repo
2. Install the dependencies:

```bash
pip install crewai crewai-tools litserve
```

Download Ollama and run the following command to download the Qwen3 model:

```bash
ollama pull qwen3
```

3. Run the server:

```bash
python server.py
```

4. Run the client:

```bash
python client.py --query "What is the Qwen3?"
```

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.