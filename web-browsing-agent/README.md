# Web Browsing Multi-Agent Workflow

We're building a local, multi-agent browser automation system powered by CrewAI and Stagehand. It leverages autonomous agents to plan, execute, and synthesize web automation tasks using natural language queries.

How It Works:

1.  **Query Submission**: User submits natural language query describing desired browser automation task.
2.  **Task Planning**: A **Planner Agent** interprets query and generates structured automation plan, including website URL and task description.
3.  **Plan Execution**: **Browser Automation Agent** executes plan using Stagehand Tool, which autonomously navigates web pages, interacts with elements, and extracts relevant content.
4.  **Response Synthesis**: **Synthesis Agent** takes raw output from execution phase and converts it into clean user-friendly response.
5.  **Final Output**: User receives a polished result containing results of web automation task, such as extracted data or completed actions.

We use:

- [Stagehand](https://docs.stagehand.dev/) for open-source AI browser automation
- [CrewAI](https://docs.crewai.com) for multi-agent orchestration

## Set Up

Follow these steps one by one:

### Create .env File

Create a `.env` file in the root directory of your project with the following content:

```env
OPENAI_API_KEY=<your_openai_api_key>
MODEL_API_KEY=<your_openai_api_key>
```

### Download Ollama

Download and install [Ollama](https://ollama.com/download) for your operating system. Ollama is used to run large language models locally.

For example, on linux, you can use the following command:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Pull the required model:

```bash
ollama pull gpt-oss
```

### Install Playwright

Install Playwright for browser automation from the official website: [Playwright](https://playwright.dev/docs/intro).

### Install Dependencies

```bash
uv sync
source .venv/bin/activate
```

This command will install all the required dependencies for the project. Additionally, make sure to install the necessary browser binaries by running:

```bash
playwright install
```

## Run CrewAI Agentic Workflow

To run the CrewAI flow, execute the following command:

```bash
python flow.py
```

Running this command will start the CrewAI agentic workflow, which will handle the multi-agent orchestration for web browsing tasks using Stagehand as AI powered browser automation.

## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

## Contribution

Contributions are welcome! Feel free to fork this repository and submit pull requests with your improvements.
