# AI Podcast Generator
Transform any web article or blog post into an engaging podcast between two speakers using [Minimax](https://www.minimax.io/) M2.1 and [Minimax](https://www.minimax.io/) Speech 2.6's state of the art capabilities.

## Overview

AI Podcast Generator is an intelligent tool that converts written content into natural-sounding podcast dialogues. Simply provide a URL, and the system will:

- Scrape and extract clean content from any webpage
- Generate an engaging two-host podcast script with natural conversation flow
- Converts the text script into audio segments for the podcast
- Merge all segments into a complete, ready-to-listen podcast

### Tech Stack

- **Minimax-M2.1** for intelligent script generation and dialogue conversion
- **Minimax Speech 2.6** for natural-sounding text-to-speech with multiple voice options
- **Firecrawl** for robust web scraping and content extraction
- **Streamlit** for an intuitive and interactive web interface

## How It Works

1. **Content Extraction**: Firecrawl scrapes the provided URL and extracts clean, structured content
2. **Script Generation**: Minimax-M2.1 analyzes the content and creates an engaging podcast dialogue between two hosts
4. **Audio Synthesis**: Each dialogue segment is converted to speech using Minimax's advanced TTS models
5. **Merging**: All audio segments are seamlessly combined into a single podcast file
6. **Delivery**: Users can listen to, download, and share their AI-generated podcast

## Installation & Setup

**Prerequisites**: Python 3.12+
    
1. **Install dependencies:**
    First, install `uv` and set up the environment:
    ```bash
    # MacOS/Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Windows
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

    Install dependencies:
    ```bash
    # Create a new directory for our project
    uv init ai-podcast-generator
    cd ai-podcast-generator

    # Create virtual environment and activate it
    uv venv
    source .venv/bin/activate  # MacOS/Linux

    .venv\Scripts\activate     # Windows

    # Install dependencies
    uv sync
    ```

2. **Set up environment variables:**
   Create a `.env` file with your API keys as specified in `.env.example` file:
   ```env
   MINIMAX_API_KEY=<YOUR_MINIMAX_API_KEY>
   FIRECRAWL_API_KEY=<YOUR_FIRECRAWL_API_KEY>
   OPENROUTER_API_KEY=<YOUR_OPENROUTER_API_KEY>
   ```

3. **Get your API keys:**

   - **Minimax**: [platform.minimax.io](https://platform.minimax.io)
   - **Firecrawl**: [firecrawl.dev](https://firecrawl.dev)
   - **OpenRouter**: [openrouter.ai](https://openrouter.ai)

   You can enter these keys directly in the app's sidebar when you run it.

## Usage

### Running the Web Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Using the Application

1. **Enter API Keys**: Input your Firecrawl, OpenRouter, and Minimax API keys in the left sidebar
2. **Provide URL**: Enter the URL of the article or blog post you want to convert
3. **Generate**: Click "Generate Podcast" and watch the magic happen
4. **Listen & Download**: Once complete, listen to your podcast or download it for later


## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.