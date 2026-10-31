# YouTube Research Agent with CrewAI and Apify

Ask a research question about one or more YouTube videos and get a sourced answer. The project pulls each video's transcript, then a two-agent CrewAI crew summarizes the videos and writes an answer that cites which video each point came from.

We use:

- [CrewAI](https://docs.crewai.com/) for multi-agent orchestration
- [Apify](https://apify.com/) through CrewAI's `ApifyActorsTool` to fetch YouTube transcripts
- OpenAI `gpt-4o-mini` as the LLM (swap in Ollama or any other provider CrewAI supports)
- [Streamlit](https://streamlit.io/) for an interactive UI

## How It Works

1. You enter one or more YouTube URLs and a research question
2. `ApifyActorsTool(actor_name="johnvc/YoutubeTranscripts")` fetches the transcripts (plus title and channel) for all videos in a single run
3. The **Transcript Analyst** agent summarizes each video and pulls out the points relevant to your question
4. The **Research Writer** agent turns those notes into a short markdown brief with a direct answer and a list of sources

Agent and task prompts live in `config.yaml`, so you can change the crew's behavior without touching the code.

## Set Up

### Get API Keys

- **Apify**: create an account and copy your API token from **Settings > API & Integrations** in the Apify Console
- **OpenAI**: create an API key in the OpenAI dashboard

### Create .env File

Create a `.env` file in the project directory (see `.env.example`):

```env
APIFY_API_TOKEN=<your_apify_api_token>
OPENAI_API_KEY=<your_openai_api_key>
```

Optionally set `MODEL` to use a different LLM, for example `MODEL=gpt-4o`.

### Install Dependencies

Ensure you have Python 3.11 or later installed.

```bash
uv sync
source .venv/bin/activate
```

Or with pip:

```bash
pip install crewai "crewai-tools[apify]" python-dotenv pyyaml streamlit
```

## Run the Project

### Streamlit App

```bash
streamlit run app.py
```

Paste one or more YouTube URLs in the sidebar (one per line), enter your question and click **Run Research**.

### Command Line

```bash
python research_crew.py "https://www.youtube.com/watch?v=VIDEO_ID" -q "What does the speaker recommend?"
```

Pass several URLs to research across multiple videos. Use `-l` to pick a transcript language other than English, for example `-l es`.

## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

## Contribution

Contributions are welcome! Feel free to fork this repository and submit pull requests with your improvements.
