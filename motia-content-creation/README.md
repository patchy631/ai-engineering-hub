# Social Media Automation workflow using Motia

A streamlined content generation agent built with [Motia](https://github.com/MotiaDev/motia) that transforms articles into engaging Twitter threads and LinkedIn posts using AI.

We use the following tech stack:
- Motia as the unified backend framework
- Firecrawl to scrape web content
- Ollama for serving Deepseek-R1 locally

## 🎯Overview

**Workflow**

Our workflow consists of 4 main steps:-

```
API → Scrape → Generate → Schedule
```

1. **API**: Receives article URL via POST request
2. **Scrape**: Extracts content using Firecrawl in markdown format
3. **Generate**: Creates Twitter & LinkedIn content using Deepseek-R1
4. **Schedule**: Saves content as drafts in Typefully for review

## 🛠️ Setup

### Prerequisites

- Node.js 18+
- Python 3.x
- API keys for:
  - Firecrawl
  - Typefully

### Installation

1. **Install Ollama:**
   ```bash
   # Setting up Ollama on linux
   curl -fsSL https://ollama.com/install.sh | sh

   # Pull the Deepseek-R1 model
   ollama pull deepseek-r1
   ```

2. **Install project dependencies:**
   ```bash
   npm install or pnpm install
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```
   or Create a `.env` file in the root directory with the following variables:
   ```bash
    FIRECRAWL_API_KEY=your_firecrawl_api_key
    TYPEFULLY_API_KEY=your_typefully_api_key
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```

## 🚀 Usage

### Generate Content

Send a POST request to trigger content generation:

```bash
curl -X POST http://localhost:3000/generate-content \\
  -H "Content-Type: application/json" \\
  -d '{"url": "https://example.com/article"}'
```

**Response:**
```json
{
  "message": "Content generation started",
  "requestId": "req_123456",
  "url": "https://example.com/article",
  "status": "processing"
}
```

### View Results

After processing completes:
1. Visit [Typefully](https://typefully.com/drafts)
2. Review your generated Twitter thread and LinkedIn post
3. Edit if needed and publish!

## 📁 Project Structure

```
social-media-automation/
├── steps/
│   ├── api.step.py                   # API endpoint handler
│   ├── scrape.step.py                # Firecrawl integration
│   ├── generate-linkedin.step.py     # Ollama Linkedin generation
│   ├── generate-twitter.step.py      # Ollama Twitter generation
│   ├── schedule-twitter.step.ts      # Twitter Typefully scheduling
│   └── schedule-linkedin.step.ts     # LinkedIn Typefully scheduling
├── prompts/
│   ├── twitter-prompt.txt   # Twitter generation prompt
│   └── linkedin-prompt.txt  # LinkedIn generation prompt
├── config/
│   └── index.js             # Configuration management
├── package.json
├── motia-workbench.json
├── requirements.txt
└── README.md
```

## 🔍 Monitoring

The Motia workbench provides an interactive UI where you can easily deb ug and monitor your flows as interactive diagrams. It runs automatically with the development server.

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements. 
