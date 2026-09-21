# **RAG and Text-to-SQL Agent**

This project implements a custom agent capable of querying either:

- A **LlamaCloud index** for RAG-based retrieval.
- A **SQL query engine** as a tool.

### **Use Case**

We use PDFs of Wikipedia pages of US cities and a SQL database containing their populations and states as documents.
Find the pages here:
- [New York City](https://en.wikipedia.org/wiki/New_York_City)
- [Los Angeles](https://en.wikipedia.org/wiki/Los_Angeles)
- [Chicago](https://en.wikipedia.org/wiki/Chicago)
- [Houston](https://en.wikipedia.org/wiki/Houston)
- [Miami](https://en.wikipedia.org/wiki/Miami)
- [Seattle](https://en.wikipedia.org/wiki/Seattle)

## **Technologies Used**

- **LlamaIndex** – for orchestrating the agent.
- **LlamaTrace(Phoenix-Arize)** – for observability.
- **Streamlit** – to build the UI.
- **GPT 3.5 turbo** – as the LLM.

## **Demo**

- [**Video Demo**](demo.mp4)
- [**Hugging Face Space**](https://huggingface.co/spaces/Safni/RAG_SGL_APP)



## **Installation and Setup**

### **1. Set up LlamaCloud API**

Get an API key from [**LlamaCloud**](https://cloud.llamaindex.ai/) and add it to the `.env` file:

```ini
LLAMA_CLOUD_API_KEY=<YOUR_API_KEY>
```

### **2. Set up Observability**

Integrate **LlamaTrace** for observability. Obtain an API key from [**LlamaTrace**](https://llamatrace.com/login) and add it to the `.env` file:

```ini
PHOENIX_API_KEY=<YOUR_API_KEY>
```

### **3. Set up OpenAI API**

Get an API key from [**OpenAI**](https://platform.openai.com/) and add it to the `.env` file:

```ini
OPENAI_API_KEY=<YOUR_API_KEY>
```

### **4. Install Dependencies**

Ensure you have **Python 3.11+** installed. Then, install dependencies:

```bash
pip install -r requirements.txt
```

### **5. Run the App**

Launch the application using:

```bash
streamlit run app.py
```


## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
