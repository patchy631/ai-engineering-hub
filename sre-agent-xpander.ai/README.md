# Junior SRE-Agent

This project demonstrates how to build a Site Reliability Engineer (SRE) agent using Agno's Agent framework and Xpander's event streaming. It supports two modes:

* **Local CLI** for ad-hoc queries
* **Event Listener** for streaming chat events via Xpander Chat UI

We use the following tech stack:

* Agno's Agent framework
* Xpander for event streaming & agent management
* Kubernetes (kubectl CLI)

---

## Setup and Installation

Ensure you have Python 3.12 or later installed on your system.

### Clone the repository

```bash
git clone <your-repository-url>
cd sre-agent-xpander.ai
```

### Create & activate virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate    # macOS/Linux
.venv\Scripts\activate       # Windows
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure credentials

```bash
cp .env.example
cp xpander_config.json.example
```

**Configure `.env` file for OpenAI:**
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

**Configure `xpander_config.json` for Xpander credentials:**
```json
{
  "agent_id":   "your_xpander_agent_id",
  "api_key":    "your_xpander_api_key",
  "org_id":     "your_xpander_org_id",
  "base_url":   "https://agent-controller.xpander.ai"
}

## Xpander Agent Configuration

Follow these steps to configure your Xpander agent:

1. Sign in to the Xpander dashboard at [https://app.xpander.ai](https://app.xpander.ai)
2. Create a new agent (or select an existing one) and note its **Agent ID** and **Organization ID**
3. Go to the **API Keys** section and generate a new API key or use default
4. Copy the key and update your `xpander_config.json` file:

---

## Run the project

### CLI Mode

```bash
python sre_agent.py
```

Type your queries at the `➜ ` prompt and enter `exit` or `quit` to stop.

### Event Listener Mode

```bash
python xpander_handler.py
```

Incoming messages will be forwarded to the SREAgent, any detected `kubectl` commands run live, and responses streamed back via SSE.

---

## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository, create a feature branch, and submit a Pull Request with your improvements.
