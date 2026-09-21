# RAG and Text-to-SQL Streamlit Application

This Streamlit application provides a user interface for querying a database using a Retrieval-Augmented Generation (RAG) approach and a Text-to-SQL tool. The application leverages asynchronous processing to handle user queries efficiently.

## Features

- **RAG Integration**: Utilizes a RAG approach for enhanced query understanding.
- **Text-to-SQL Conversion**: Converts natural language queries into SQL commands.
- **Asynchronous Execution**: Handles queries asynchronously for improved performance.

## Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.10 or higher
- [Streamlit](https://streamlit.io/)
- [Nest Asyncio](https://pypi.org/project/nest-asyncio/)
- Create an index in LlamaCloud. This index was used in code along with LlamaCloud API Key.
  `Check "create_llama_cloud_index" function in db_init.py` for more details.

## Installation

1. **Clone the Repository**

   Clone this repository to your local machine:

   ```bash
   git clone https://github.com/patchy631/ai-engineering-hub
   cd rag_text2sql
   ```
   
2. ** Create a Python Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. **Install the Requirements**
   ```bash
   pip install -r requirements.txt 
   ```
   
4. **Run the Application**
   ```
   streamlit run rag_text_to_sql.py
   ```