# Automated Form Filling

Automated multi-agent workflow for filling out forms: extract data from documents using OCR, map it to form fields, and generate filled PDFs. The pipeline uses a W-9 tax form as an example, which can be extended to accommodate other forms.

We use:

- [CrewAI](https://docs.crewai.com/) (agentic design) for multi-agent orchestration
- [Datalab](https://documentation.datalab.to/) (document conversion & form filling) for OCR and form filling
- [Streamlit](https://streamlit.io/) for an interactive UI
- [MiniMax-M2.1](https://openrouter.ai/minimax/minimax-m2.1) (via OpenRouter) as the LLM for the agents

## Set Up

Follow these steps one by one:

### Create .env File

Create a `.env` file in the root directory of your project with the following content:

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

This installs all required dependencies (CrewAI, Datalab SDK, Streamlit, etc.).

## Run CrewAI Workflow (CLI)

To run the form-filling workflow from the command line (e.g. with the bundled W-9 example):

```bash
python main.py
```

You can also use the workflow programmatically via `run_form_flow()` in `main.py`, passing paths to your source document, blank form PDF, and form schema (YAML).

## Run Streamlit Interface

To run the Streamlit interface:

```bash
streamlit run app.py
```

This starts the web UI where you can upload documents, choose a form schema, and run the pipeline. Use the URL shown in the terminal (e.g. `http://localhost:8501`) to open the app in your browser.

## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

## Contribution

Contributions are welcome! Feel free to fork this repository and submit pull requests with your improvements.
