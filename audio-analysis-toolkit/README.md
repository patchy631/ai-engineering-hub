# AssemblyAI Audio Analysis Toolkit

This project demonstrates how to build an audio analysis system powered by AssemblyAI and the Model Context Protocol (MCP).

We use the following tech stack:

- AssemblyAI for audio transcription and analysis (audio-RAG)
- Streamlit for the interactive web UI
- Cursor as the MCP host for programmatic access

## Setup and Installation

Ensure you have Python 3.12 or later installed on your system.

### Install dependencies

```bash
# Clone the repository and navigate to the project directory
# git clone <your-repo-url>
cd project-name

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# MacOS/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configure environment variables
Copy `.env.example` to `.env` and configure the following environment variables:

```
ASSEMBLYAI_API_KEY=your_assemblyai_api_key
```

## Usage

### 1. Run as a Streamlit App (Interactive UI)

Launch the web app for interactive audio analysis:

```bash
streamlit run app.py
```

- **Upload Audio**: Drag and drop or browse for audio files (WAV, MP3, MP4, M4A, FLAC)
- **Processing**: The app automatically processes your audio with AssemblyAI
- **Analysis**: Navigate through different tabs to explore results:
  - View timestamped transcription
  - Read AI-generated summaries
  - Analyze speaker patterns
  - Explore sentiment analysis
  - Discover key topics
  - Chat with your audio content

### 2. Run as an MCP Server (for Cursor/Agent Integration)

First, set up your MCP server as follows:

1. Go to Cursor settings
2. Select MCP Tools
3. Add new global MCP server.
4. In the JSON file, add this:

```json
{
    "mcpServers": {
        "assemblyai": {
            "command": "python",
            "args": [
                "server.py"
            ],
            "env": {
                "ASSEMBLYAI_API_KEY": "YOUR_ASSEMBLYAI_API_KEY"
            }
        }
    }
}
```
You should now be able to see the MCP server listed in the MCP settings. In Cursor MCP settings make sure to toggle the button to connect the server to the host.

Done! Your server is now up and running.

## MCP Tools

The custom MCP server provides the following tools:

- **transcribe_audio**: Ingests and transcribes audio, returning sentences with timestamps
- **get_audio_data**: Retrieves features from the last transcript, including:
  - Full transcript text
  - Timestamped sentences
  - Summary
  - Speaker labels
  - Sentiment analysis
  - Topic categories

You can now ingest your audio files, retrieve relevant data, and query it all using the Cursor Agent or any MCP-compatible client. The agent can analyze, summarize, and answer questions about your audio just with a single query.

## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

## Contribution

Contributions are welcome! Feel free to fork this repository and submit pull requests with your improvements.


