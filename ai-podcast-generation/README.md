# 🎙️ Podsite - AI Podcast Generation

Transform web content and text into engaging AI-generated podcasts with natural-sounding conversations between two speakers.

## 🚀 Two Versions Available

### 📱 Regular Version (`app.py`)
- Uses **OpenAI GPT-4** for script generation
- Requires OpenAI API key
- Fast and reliable cloud-based AI
- Pay-per-use pricing model

### 🔓 Open Source Version (`app_oss.py`)
- Uses **Ollama** with local AI models
- No API keys required for script generation
- Completely private and offline
- Free to use after setup

## ✨ Features

- **🌐 Website Scraping**: Extract content from any URL using Firecrawl
- **📋 Text Input**: Paste any text content directly
- **🎭 Multiple Styles**: Choose from Conversational, Interview, Debate, or Educational formats
- **⏱️ Flexible Duration**: Generate podcasts from 5 to 20 minutes
- **🎵 AI Audio Generation**: Convert scripts to natural-sounding speech using Kokoro TTS
- **📥 Export Options**: Download both scripts (JSON) and audio files (WAV)
- **📚 Source Management**: Store multiple sources and generate podcasts from any of them

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or 3.12
- [uv](https://github.com/astral-sh/uv) package manager

**For Regular Version (`app.py`):**
- OpenAI API key (required)
- Firecrawl API key (optional, for web scraping)

**For Open Source Version (`app_oss.py`):**
- Ollama installed and running
- A local AI model (e.g., `gpt-oss:20b`)

### Installation

1. Navigate to the project:
```bash
cd ai-podcast-generation
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Set up your environment variables:
```bash
cp .env.example .env
```

4. Add your API keys to `.env` (for regular version):
```
OPENAI_API_KEY=your_openai_api_key_here
FIRECRAWL_API_KEY=your_firecrawl_api_key_here  # Optional
```

### Running the Apps

**Regular Version (OpenAI):**
```bash
uv run streamlit run app.py
```

**Open Source Version (Ollama):**
```bash
# First, ensure Ollama is running with your model
ollama serve
ollama pull gpt-oss:20b  # or your preferred model

# Then run the OSS app
uv run streamlit run app_oss.py
```

Both apps will open in your default browser at `http://localhost:8501`

## 📖 Usage

### Step 1: Add Sources

Navigate to the "📁 Add Sources" tab:

**Option A: Scrape Website**
1. Select the "🌐 Website" tab
2. Enter a URL (e.g., https://example.com/article)
3. Click "Add Website"
4. Wait for the content to be scraped
5. Requires FIRECRAWL_API_KEY in .env

**Option B: Paste Text**
1. Select the "📋 Text" tab
2. Enter a source name
3. Paste your content
4. Click "Add Text"

Your sources will appear in the sidebar with:
- Source name/title
- Type (Website or Text)
- Word count
- Delete button (🗑️) to remove

### Step 2: Generate Podcast

1. Navigate to the "🎙️ Studio" tab
2. Select a source from the dropdown
3. Choose your podcast style:
   - **Conversational**: Natural, friendly discussion
   - **Interview**: Q&A format
   - **Debate**: Different perspectives
   - **Educational**: Explanatory with clarifying questions
4. Choose duration (5, 10, 15, or 20 minutes)
5. Click "🎙️ Generate Podcast"
6. Wait for script and audio generation
7. Download the results!

## 🏗️ Project Structure

```
ai-podcast-generation/
├── app.py                          # Main Streamlit application
├── src/
│   ├── podcast/
│   │   ├── script_generator.py    # Podcast script generation
│   │   └── text_to_speech.py      # Audio generation with TTS
│   └── web_scraping/
│       └── web_scraper.py          # Web content extraction
├── outputs/                        # Generated audio files
├── pyproject.toml                  # Project dependencies (uv)
├── .env.example                    # Environment variables template
└── README.md                       # This file
```

## 🛠️ Technology Stack

- **Streamlit**: Web interface
- **OpenAI GPT-4**: Script generation via CrewAI
- **Kokoro TTS**: Natural text-to-speech synthesis
- **Firecrawl**: Web content extraction
- **uv**: Fast Python package management

## 📝 Example Output

The app generates:

1. **Podcast Script** (JSON format):
   - Structured dialogue between Speaker 1 and Speaker 2
   - Metadata including source, duration, and line count

2. **Audio Files** (WAV format):
   - Individual segments for each speaker turn
   - Complete combined podcast with natural pauses
   - High-quality 24kHz audio

## 🔧 Configuration

### Podcast Settings

- **Style**: Conversational, Interview, Debate, Educational
- **Duration**: 5, 10, 15, or 20 minutes
- Configured in the Studio tab

### Audio Settings

Modify in `src/podcast/text_to_speech.py`:
- Speaker voices (default: `af_heart` and `am_liam`)
- Sample rate (default: 24000 Hz)
- Pause duration between segments (default: 0.2s)

## 🐛 Troubleshooting

### Web Scraping Not Available

If you see "Web scraping will not be available":
- Add `FIRECRAWL_API_KEY` to your `.env` file
- Get a key from https://www.firecrawl.dev
- Restart the app

### TTS Not Available

If you see "TTS not available":
```bash
uv pip install kokoro>=0.9.4
```

### OpenAI API Errors

- Check your API key is correctly set in `.env`
- Ensure you have sufficient API credits
- Verify your API key has access to GPT-4 models

### Import Errors

Make sure all dependencies are installed:
```bash
uv sync
```

## 💡 Workflow

```
1. Add Source (URL or Text)
   ↓
2. Content is stored in session
   ↓
3. Select source in Studio
   ↓
4. Generate script (GPT-4)
   ↓
5. Generate audio (Kokoro TTS)
   ↓
6. Download script & audio
```

## 📄 License

This project is part of the AI Engineering Hub.

## 🙏 Acknowledgments

- Inspired by NotebookLM's podcast generation feature
- Uses Kokoro TTS for natural-sounding speech synthesis
- Powered by OpenAI's language models
- Web scraping by Firecrawl

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

Built with ❤️ using Streamlit and AI
