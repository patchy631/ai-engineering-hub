# Chat with Code using Qwen3-Coder

Enhance your experience with GitHub repositories through a natural language interface. We are developing a Streamlit app that enables users to communicate with code using the Qwen3-Coder model. This app offers a user-friendly interface for querying code and receiving responses, along with the additional advantage of validating those responses using Cleanlab Codex.

We use:

- [Llama_Index](https://docs.llamaindex.ai/en/stable/) for orchestration
- [Milvus](https://milvus.io/) to self-host a VectorDB
- [Cleanlab](https://help.cleanlab.ai/codex/) codex to validate the response
- [OpenRouterAI](https://openrouter.ai/docs/quick-start) to access Alibaba's Qwen3-Coder

## Set Up

Follow these steps one by one:

### Setup Milvus VectorDB

Milvus provides an installation script to install it as a docker container.

To install Milvus in Docker, you can use the following command:

```bash
curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed.sh

bash standalone_embed.sh start
```

### Install Dependencies

```bash
uv sync
```

## Run the Notebook

You can run the `notebook.ipynb` file to test the functionality of the code in a Jupyter Notebook environment. This notebook will guide you through the process of querying code and validating responses.

## Run the Application

To run the Streamlit app, use the following command:

```bash
streamlit run app.py
```

Open your browser and navigate to `http://localhost:8501` to access the app.

## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

## Contribution

Contributions are welcome! Feel free to fork this repository and submit pull requests with your improvements.
