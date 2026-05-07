# Biotech Agentic Analyst

An agentic workflow for analyzing scientific papers: extract figures from PDFs using Datalab, then run CrewAI agentic flow to generate structured intelligence — key findings, biological significance, quantitative highlights, and knowledge-base tags — for each figure.

We use:

- [CrewAI](https://docs.crewai.com/) for multi-agent orchestration (Flow + Crew)
- [Datalab](https://documentation.datalab.to/) for PDF conversion and figure extraction
- [OpenRouter](https://openrouter.ai/) as the LLM provider
- [Streamlit](https://streamlit.io/) for an interactive UI

## How It Works

1. Upload a scientific PDF
2. Datalab runs a convert → extract process to identify and extract all figures, axis labels, and captions
3. A CrewAI Flow with Analyst agent produces structured intelligence for each figure:
   - Chart type and key finding
   - Variables and conditions compared
   - Quantitative highlights
   - Biological significance
   - Knowledge-base tags
4. Results are displayed in the Streamlit UI with figure thumbnails

## Set Up

### Create .env File

Create a `.env` file in the root directory with the following content:

```env
OPENROUTER_API_KEY=<your_openrouter_api_key>
DATALAB_API_KEY=<your_datalab_api_key>
```

### Install Dependencies

```bash
uv sync
source .venv/bin/activate
```

On Windows (PowerShell):

```powershell
uv sync
.venv\Scripts\activate
```

## Run the Streamlit App

```bash
streamlit run app.py
```

Open the URL shown in the terminal (e.g. `http://localhost:8501`). Upload a scientific PDF in the sidebar and click **Run Analysis** to trigger the full workflow.

## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

## Contribution

Contributions are welcome! Feel free to fork this repository and submit pull requests with your improvements.
