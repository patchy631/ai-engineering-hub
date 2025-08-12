# Run GPT-OSS Locally with Thinking UI 🧠

Experience the power of GPT-OSS reasoning locally - see exactly how the model thinks through problems before giving you answers.

## Why This Matters

- 🏠 **100% Local**: Run GPT-OSS on your own hardware using Ollama
- 🧠 **See The Thinking**: Watch the model's reasoning process unfold in expandable panels
- 🔒 **Privacy First**: Your conversations never leave your machine
- ⚡ **GPT-OSS:20B**: Advanced reasoning capabilities with native thinking support
- 💰 **Zero Cost**: No API fees or usage limits

## Key Features

- **Thinking UI**: Expandable panels show model's reasoning process
- **Real-time Streaming**: See responses generate as the model thinks
- **Chat History**: Full conversation history with thinking processes preserved
- **Clean Interface**: Professional UI with OpenAI and Ollama logos

## Installation and Setup

### Prerequisites
- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### 1. Setup Ollama

```bash
# Install Ollama (Linux/macOS)
curl -fsSL https://ollama.com/install.sh | sh

# Pull the GPT-OSS model
ollama pull gpt-oss:20b
```

### 2. Install Dependencies

**Using uv (recommended):**
```bash
uv sync
```

**Using pip:**
```bash
pip install streamlit ollama
```

### 3. Run the App

```bash
uv run streamlit run app.py
# or with pip: streamlit run app.py
```

The app will be available at `http://localhost:8501` (or 8502 if 8501 is busy).

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
