# Text-to-SQL Query Interface

This project combines **Retrieval-Augmented Generation (RAG)** and **Text-to-SQL** in a single query interface. It allows users to ask natural language questions, and the system generates SQL queries to fetch data from a database. The project uses:

- **SQLAlchemy** for database management.
- **Gemini API** (or other LLMs) for natural language processing and SQL generation.
- **Streamlit** to build the user interface.

A demo of the application is shown below:

- [Video Demo](https://www.canva.com/design/DAGhue4_LeI/sEMcO4zqBtOaz_sbFzLniA/watch?utm_content=DAGhue4_LeI&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=hd7ff32ef2d)

- [Post public link](https://typefully.com/t/SU568lW)

---

## Installation and Setup

### 1. Setup Gemini API

1. Get an API key from [Gemini](https://ai.google.dev/).

2. Use Streamlit secrets to securely store the API key.
Create a 
```.streamlit/secrets.toml ``` file and add:

```
GEMINI_API_KEY = "your_gemini_api_key_here"
```
---

Alternatively, You can Set the API key in the `.env` file as follows:
```plaintext
   GEMINI_API_KEY=<YOUR_API_KEY>
```

---
 Install Dependencies
 ---
 Ensure you have Python 3.11 or later installed. Must check package versions have no any conflicting dependencies.Then, install the required dependencies:

```
pip install -r requirements.txt
```
---

 Run the App
Run the Streamlit app using the following command: 

```
streamlit run app.py
```

