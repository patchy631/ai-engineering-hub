# Pixeltable MCP Server

We're building a unified multimodal data storage and orchestration solution powered by Pixeltable. It enables incremental storage, transformation, indexing, and orchestration of your multimodal data—providing a single, seamless way to store and search across text, images, audio, and video.

To demonstrate the usage, we have created MCP servers on top of Pixeltable infra for different modalities and connected them to Agents powered by local LLMs. You can also use these servers as part of your own solution.

How It Works:

1.  **Query Submission**: A user submits a query of any modality (text, image, video, or audio).
2.  **Smart Routing**: A **Router Agent** classifies the query and directs it to the appropriate specialist.
3.  **Specialist Execution**: The designated **Specialist Agent** (Document, Image, Video, or Audio) uses its dedicated Pixeltable MCP server to execute the task—be it indexing, insertion, or searching.
4.  **Response Synthesis**: The output is then passed to a **Synthesis Agent**.
5.  **Final Output**: This final agent refines the retrieved information into a polished, user-friendly response.

We use:

- [Pixeltable](https://docs.pixeltable.com) for multimodal AI data infrastructure
- [CrewAI](https://docs.crewai.com) for multi-agent orchestration
- [Ollama](https://ollama.com) for running large language models locally

## Set Up

Follow these steps one by one:

### Create .env File

Create a `.env` file in the root directory of your project with the following content:

```env
OPENAI_API_KEY=<your_openai_api_key>
```

### Download Ollama

Download and install [Ollama](https://ollama.com/download) for your operating system. Ollama is used to run large language models locally.

For example, on linux, you can use the following command:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Pull the required model:

```bash
ollama pull gemma3
```

### Install Dependencies

```bash
uv sync
```

## Run MCP Server

To run all 4 (audio, video, image, and doc) Pixeltable MCP servers, execute the following docker compose command:

```bash
docker compose --env-file .env up --build
```

Each service runs on its designated port (8080 for audio, 8081 for video, 8082 for image, 8083 for doc).

## Use MCP Server

Our Pixeltable servers are ready, so now it's time to integrate the MCP servers as tools within CrewAI!

We will create crews of agents linked to their respective Pixeltable MCP servers for tool discovery and execution. Next, we will use the CrewAI flow to orchestrate a multimodal, multi-agent system capable of performing complex tasks such as audio and video indexing, semantic image search, and more.

Please refer to the `crewai_mcp.ipynb` notebook for detailed instructions and the complete code to build the CrewAI flow described above.

## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

## Contribution

Contributions are welcome! Feel free to fork this repository and submit pull requests with your improvements.
