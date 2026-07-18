# Job Application Automation Multi-Agent Workflow

We're building a local, multi-agent job application automation system powered by CrewAI and Stagehand. It automates the entire job application process from resume optimization to form submission using autonomous AI agents.

How It Works:

1.  **Resume Parsing**: A **Parser Agent** extracts structured data (contact info, skills, experience, education) from your resume file.
2.  **Job Description Fetching**: A **Fetcher Agent** scrapes and extracts job description details from the provided job posting URL.
3.  **Resume Analysis**: An **Analyzer Agent** compares your resume against the job description to identify gaps and optimization opportunities.
4.  **Resume Optimization**: An **Optimizer Agent** tailors your resume content for ATS compatibility, aligning it with the job requirements.
5.  **Resume Generation**: A **Generator Agent** formats the optimized resume into a clean, ready-for-submission version.
6.  **Job Application Submission**: A **Submitter Agent** uses Stagehand to autonomously navigate to the job application page, fill out required form fields with your profile data and optimized resume, and submit the application.

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
GOOGLE_API_KEY=<your_google_api_key>
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
python main.py
```

Running this command will start the CrewAI agentic workflow, which will handle the multi-agent orchestration for job application automation tasks using Stagehand as AI powered browser automation.

## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

## Contribution

Contributions are welcome! Feel free to fork this repository and submit pull requests with your improvements.
