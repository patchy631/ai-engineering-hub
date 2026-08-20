# Brand monitoring flow using DeepSeek-R1, CrewAI, Xquik and Bright Data

This project runs an automated brand monitoring workflow with AI agents:
- [Xquik](https://docs.xquik.com/sdks/python) searches recent X/Twitter mentions and returns engagement data.
- [Bright Data](https://brdta.com/dailydoseofds) scrapes LinkedIn, Instagram, YouTube and web pages.
- CrewAI orchestrates the agents.
- DeepSeek-R1 analyzes each mention.

The brand monitoring output is shown here: [Sample output](brand-monitoring-demo.mp4)

The final report groups mentions by platform. Each item includes its source link and an AI-generated summary. It analyzes brand mentions and engagement; it does not enrich company records.

---
## Setup

**Get an Xquik API key**:
- Follow the [Xquik Python SDK guide](https://docs.xquik.com/sdks/python).
- Store the key in `brand_monitoring_flow/.env` after copying `.env.example`.

```bash
X_TWITTER_SCRAPER_API_KEY="..."
```

Xquik is an independent third-party service. Not affiliated with X Corp. "Twitter" and "X" are trademarks of X Corp.

**Get Bright Data credentials**:
- Go to [Bright Data](https://brdta.com/dailydoseofds) and sign up for an account.
- Select "Proxies & Scraping" and create a new "SERP API"
- Select "Native proxy-based access"
- You will find your username and password there.
- Store it in the .env file of the src/ folder (after renaming the .env.example file to .env)

```
BRIGHT_DATA_USERNAME="..."
BRIGHT_DATA_PASSWORD="..."
```

- Also get the Bright Data API key from your dashboard.

```
BRIGHT_DATA_API_KEY="..."
```

**Setup Ollama**:
   ```bash
   # setup ollama on linux 
   curl -fsSL https://ollama.com/install.sh | sh
   # pull deepseek-r1 model
   ollama pull deepseek-r1
   ```


**Install Dependencies**:
   Install Python 3.10, 3.11, or 3.12.
   ```bash
   cd brand_monitoring_flow
   pip install -e .
   ```

---

## Run the project

From `brand_monitoring_flow`, head to the app folder:
```
cd src
```

and run the project by running the following command:

```bash
streamlit run brand_monitoring_app.py
```

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
