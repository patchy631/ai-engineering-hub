# Database Memory Agent

We're building a Database Memory Agent with RAG (Retrieval Augmented Generation) capabilities that integrates MongoDB Atlas Vector Search for semantic document retrieval, Voyage AI for embeddings, and OpenAI for intelligent responses. The agent uses tools (vector search and calculator) to answer questions from uploaded documents and perform calculations, with context-aware memory across conversations.

We use:

- [MongoDB Atlas Vector Search](https://www.mongodb.com/products/platform/atlas-vector-search) for semantic search and document storage
- [Voyage AI](https://www.voyageai.com/) for generating embeddings (voyage-3-large model)
- [OpenAI](https://openai.com/) for LLM responses (gpt-4o)
- [Streamlit](https://streamlit.io/) to wrap the logic in an interactive UI

## Set Up

### Prerequisites

You must have the following:

- One of the following MongoDB cluster types:

  - An [Atlas cluster](https://www.mongodb.com/docs/atlas/tutorial/create-new-cluster/) running MongoDB version 6.0.11, 7.0.2, or later. Ensure that your IP address (Internet Protocol address) is included in your Atlas project's [access list](https://www.mongodb.com/docs/atlas/security/ip-access-list/).

  - A local Atlas deployment created using the Atlas CLI. To learn more, see [Create a Local Atlas Deployment](https://www.mongodb.com/docs/atlas/cli/current/atlas-cli-deploy-local/).

  - A MongoDB Community or Enterprise cluster with [Search and Vector Search](https://www.mongodb.com/docs/manual/administration/install-community/#std-label-community-search-deploy) installed.

- A Voyage AI API key.

- An OpenAI API key.

### Configure Environment Variables

Copy `.env.example` to `.env` and configure the following environment variables:

```env
MONGODB_URI="<mongodb-connection-string>"
VOYAGE_API_KEY="<your-voyage-api-key>"
OPENAI_API_KEY="<your-openai-api-key>"
```

Replace `<mongodb-connection-string>` with the connection string for your Atlas cluster or local Atlas deployment.

**Atlas Cluster:**

Your connection string should use the following format:

```
mongodb+srv://<db_username>:<db_password>@<clusterName>.<hostname>.mongodb.net
```

To learn more, see [Connect to a Cluster via Drivers](https://www.mongodb.com/docs/atlas/driver-connection/).

**Local or Self-Managed:**

Your connection string should use the following format:

```
mongodb://localhost:<port-number>/?directConnection=true
```

To learn more, see [Connection Strings](https://www.mongodb.com/docs/manual/reference/connection-string/).

### Install Dependencies

```bash
uv sync
```

### Run the Application

Run the application with:

```bash
streamlit run app.py
```

Or use the CLI version:

```bash
python main.py
```

[Get your Voyage AI API keys here](https://dashboard.voyageai.com/)

[Get your OpenAI API keys here](https://platform.openai.com/api-keys)

## Project Structure

```
database-memory-agent/
├── .env                 # Environment variables (create from .env.example)
├── config.py            # MongoDB and API configuration
├── ingest_data.py       # PDF ingestion and vector index creation
├── tools.py             # Agent tools (vector search, calculator)
├── memory.py            # Chat history storage
├── planning.py          # Agent planning and response generation
├── app.py              # Streamlit web application
├── main.py             # CLI application
├── pyproject.toml      # Project dependencies
└── README.md           # This file
```

## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

## Contribution

Contributions are welcome! Feel free to fork this repository and submit pull requests with your improvements.
