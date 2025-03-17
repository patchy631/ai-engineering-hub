
# RAG + Text-to-SQL Query Interface

**Combine document retrieval and database querying in one natural interface.** This project demonstrates a unified query app that can handle both free-form questions and SQL queries, using a Retrieval-Augmented Generation (RAG) pipeline alongside Text-to-SQL capabilities. With a single input box, users can ask questions in plain English or write SQL commands, and get responses backed by either unstructured documents or a SQL database, respectively.

## Overview

**Why this project?** In many real-world scenarios, valuable information is spread across text documents and relational databases. A user might ask: *“What are the key findings from last quarter’s report?”* (unstructured data) or *“How many sales did we make last quarter?”* (structured data). Instead of building separate systems, this interface uses an LLM (Large Language Model) to route queries to the correct backend:
- *Natural language questions* trigger a **RAG** workflow – the system retrieves relevant documents (using embeddings stored in a vector database) and the LLM generates an answer with those do ([Building a Local RAG api with LlamaIndex, Qdrant, Ollama and FastAPI | Otmane Boughaba.](https://otmaneboughaba.com/posts/local-rag-api/#:~:text=A%20better%20approach%20would%20be,discussed%20in%20the%20next%20sections))xt.
- *Database questions* trigger a **Text-to-SQL** workflow – the LLM translates the question into a SQL query, executes it on the database, and forma ([SQL Index Guide (Core) - LlamaIndex  0.6.18](https://llama-index.readthedocs.io/zh/latest/examples/index_structs/struct_indices/SQLIndexDemo.html#:~:text=,embedding%20token%20usage%3A%200%20tokens))43†L373-L381】.

**Tech Stack:**
- **LlamaIndex** – Acts as the orchestration layer, providing tools for document indexing/retrieval and text-to-SQL query handling.
- **Ollama** – Runs the LLM locally (e.g., a Llama 2 model), so no external API is needed. The LLM powers both the query router and answer generation.
- **Qdrant** – (Optional) Serves as the vector database for document embeddings. It enables semantic search to find relevant text snippets for answering questions.
- **Streamlit** – Provides the web UI, making it easy for users to interact with the system (enter queries and view answers in a browser).

The architecture is as follows: user queries go to LlamaIndex, which uses an LLM-based router to decide between querying the **Document Index** (via Qdrant) or the **SQL Database**. Relevant information is fetched, then the LLM (via Ollama) generates a final answer, which is displayed in Streamlit.

## Installation

### Prerequisites
- **Python 3.9+** and **pip** installed.
- **Ollama** installed on your machine (for local LLM inference). Follow the [Ollama installation guide](https://ollama.ai/docs/installation) for your platform. Once installed, download a model, for example:  
  ```bash
  ollama pull llama2
  ``` 
  This pulls a Llama 2 model (7B chat) for use. *(Feel free to use any compatible model with Ollama.)*
- **Qdrant** vector database (optional for larger document sets). You can run Qdrant easily via Docker:  
  ```bash
  docker run -d -p 6333:6333 qdrant/qdrant
  ``` 
  *(If you skip Qdrant, the app can fall back to an in-memory vector store for small data, though using Qdrant is recommended for persistence and performance.)*
- A SQL database with your structured data. For demo purposes, you can use SQLite or any SQLAlchemy-supported database. Ensure you have the connection details or a URI for it. (The example in this project uses a SQLite database with a sample table.)

### Setup Steps

1. **Clone the repository**:  
   ```bash
   git clone https://github.com/yourusername/rag-text-to-sql-demo.git
   cd rag-text-to-sql-demo
   ```

2. **Install Python dependencies**:  
   We recommend using a virtual environment. Then run:  
   ```bash
   pip install -r requirements.txt
   ```  
   This will install LlamaIndex, Streamlit, Qdrant client, SQLAlchemy, and other needed libraries.

3. **Configure the application**:  
   - **Documents**: Put the files you want to use for document QA in the `data/` directory (or adjust the path in the code). Supported formats include text, PDFs, etc. The example uses `data/` folder for simplicity.  
   - **Database**: If using SQLite, you can place your database file in the project directory and update the connection string in the code (e.g., `engine = create_engine("sqlite:///mydata.db")`). For other databases, update the SQLAlchemy connection URL accordingly.  
   - **LLM Model**: By default, the app is set to use the model you pulled in Ollama (e.g., `llama2` if you followed above). Check the `app.py` (or relevant config) to ensure the model name matches what you have. You can change it to any model Ollama supports.

4. **Start the supporting services**:  
   - Make sure **Qdrant** is running (if used). The Docker command above will run it on `localhost:6333`. No further config needed if using default URL.  
   - Start **Ollama** server:  
     ```bash
     ollama serve
     ```  
     This will run Ollama on `localhost:11434` by default. The app will connect to this for LLM queries.

5. **Run the Streamlit app**:  
   From the project directory, execute:  
   ```bash
   streamlit run app.py
   ```  
   This will launch the web application. Streamlit will open a browser window (usually at `http://localhost:8501`) for you to interact with the app.

## Usage

Once the Streamlit app is running, you’ll see a single text input field in your browser.

- **Ask a question in natural language** about the content of your documents or data. For example: *“What policies do we have on remote work?”* When you submit, the app will:  
  1. Use the LLM (via LlamaIndex’s router) to determine that this is a question for unstructured data.  
  2. Embed your query and perform a similarity search in the document index (using Qdrant) to retrieve relevant text passages.  
  3. Feed those passages into the LLM (running in Ollama) to generate a f ([Building a Local RAG api with LlamaIndex, Qdrant, Ollama and FastAPI | Otmane Boughaba.](https://otmaneboughaba.com/posts/local-rag-api/#:~:text=A%20better%20approach%20would%20be,discussed%20in%20the%20next%20sections))er.  
  4. Display the answer, often with citations or source info if implemented (so you know which document it came from).

- **Ask a question that involves aggregated data or facts from the database**. For example: *“How many sales did we make last quarter?”* or *“List the top 5 products by revenue.”* On submission, the app will:  
  1. Recognize that this query likely needs the structured database.  
  2. Use the LLM to convert the natural language question into a SQL query  ([SQL Index Guide (Core) - LlamaIndex  0.6.18](https://llama-index.readthedocs.io/zh/latest/examples/index_structs/struct_indices/SQLIndexDemo.html#:~:text=,embedding%20token%20usage%3A%200%20tokens))43†L373-L381】 — behind the scenes it might produce something like `SELECT SUM(sales) FROM ... WHERE quarter='Q4';`.  
  3. Execute the generated SQL on your database via SQLAlchemy, get the result, and possibly let the LLM format the result into a nice answer or table.  
  4. Return the answer to you in the chat interface. (If the question was already a raw SQL query, the app will directly execute it and return the results without LLM intervention.)

- **Submit a direct SQL query** if you prefer. You can also type actual SQL (e.g., `SELECT * FROM sales LIMIT 5;`). The app will detect the input is SQL (likely by simple check or the router) and run it on the database, returning the results in text or a table. This is useful for expert users who want precise control.

The interface will label or handle responses so you know whether the answer came from documents or the database. For instance, it might show sources for document-based answers, or show a table for SQL query results.

**Note:** The first time you ask a question, the LLM may take a few seconds to respond, especially if the model is large. Subsequent queries are typically faster. Ensure your machine has enough resources for the chosen model.

## How It Works (Behind the Scenes)

When you enter a query, the system goes through these steps:
1. **Query Routing** – LlamaIndex uses an LLM (via the RouterQueryEngine) to analyze the query. It has two options (tools): “Vector DB search” or “SQL query”. It chooses the one that the query is be ([Combining Text-to-SQL with Semantic Search for Retrieval Augmented Generation — LlamaIndex - Build Knowledge Assistants over your Enterprise Data](https://www.llamaindex.ai/blog/combining-text-to-sql-with-semantic-search-for-retrieval-augmented-generation-c60af30ec3b#:~:text=1,original%20question%20into%20a%20more)). (For example, a query containing keywords like *“how many”*, *“total”,* or *specific columns* might lean towards SQL, whereas an open-ended question or something referencing a policy or report goes to RAG.)

2. **Retrieval or SQL Execution** –  
   - If the query is routed to **RAG**: The query is embedded into a vector, and Qdrant is queried for similar vectors (document chunks). The top relevant documents are fetched. These docs are then given to the LLM along with the original question, prompting it to compose a helpful answer grounded in the docs.  
   - If the query is routed to **Text-to-SQL**: The LLM takes the question and the known database schema to create a valid SQL query. The app executes this SQL on the database. If the query is successfully executed and returns results, those results can be returned as-is or fed back into the LLM to generate a more user-friendly sentence. If the question was already in SQL form, this step is straightforward execution.

3. **Response Generation** – The final answer is presented in the Streamlit UI. For document-based answers, you might see a synthesized paragraph with citations pointing to the source documents. For SQL-based answers, you might see a summarized sentence or a small table of results. The design is customizable – you can choose to display raw SQL results or a narrated answer.

This combination approach ensures **accuracy** and **completeness**:
- The RAG component keeps the LLM’s answers grounded in *your documents*, mitigating hallucinations and providing traceable sources.
- The Text-to-SQL component allows the LLM to perform **precise calculations and data retrieval** that might be impossible to get from just reading documents (e.g., summing up millions of records, or applying filters).

## Customization

- **Using a Different LLM**: You can swap out the model by pulling a different model with Ollama (or even adjust the code to use an OpenAI API or other LLM service if you prefer). Just ensure the LLM is powerful enough to handle text-to-SQL conversions if your database is complex. For example, GPT-4 or a fine-tuned Llama could yield better SQL generation for very compli ([Query Engine for Text-To-SQL: Everything You Need To Get Started](https://phoenix.arize.com/how-to-set-up-a-sql-router-query-engine-for-effective-text-to-sql/#:~:text=Questions%20that%20ask%20for%20specific,an%20answer%20to%20the%20question))28†L243-L246】.
- **Modifying Prompting or Logic**: The current router logic uses LlamaIndex’s default prompt to decide the route. You can fine-tune this by providing custom prompt instructions (e.g., some queries might need both routes – you could then always do the SQL first, then RAG, as shown in adva ([Combining Text-to-SQL with Semantic Search for Retrieval Augmented Generation — LlamaIndex - Build Knowledge Assistants over your Enterprise Data](https://www.llamaindex.ai/blog/combining-text-to-sql-with-semantic-search-for-retrieval-augmented-generation-c60af30ec3b#:~:text=detailed%20question%20given%20the%20results,and%20then%20LLM%20response%20synthesis))). LlamaIndex makes it easy to adjust these under the hood if needed.
- **Scaling Document Search**: Qdrant is capable of scaling to millions of vectors. Ensure you chunk your documents properly (LlamaIndex’s `SimpleDirectoryReader` with default chunking or `SentenceWindowNodeParser` can help) so that each chunk is a manageable size for the LLM context. You can also configure embedding model in LlamaIndex for vectorization.
- **Security**: If exposing this app, be mindful that it can execute SQL. You might want to implement checks or parameterization to avoid any harmful queries (especially if connected to a production database).

## Troubleshooting

- If the Streamlit app doesn’t launch or you see an error about ports, verify that nothing else is running on port 8501, or specify a different port with `streamlit run app.py --server.port 8502`.
- If the LLM is not responding or you get errors connecting to Ollama, make sure you ran `ollama serve` and that the model was pulled successfully. You can test Ollama by running a quick prompt in the terminal: `ollama run llama2: "Hello"` to see if it generates text. Also, check that the URL in the code for Ollama is correct (default is `http://localhost:11434`).
- If document queries aren’t finding relevant info, ensure your documents are loaded correctly and that the embeddings are being generated. You might need to increase the number of results (`similarity_top_k`) or check that the questions relate to the content in `data/`. Adding more documents or improving the embedding model could help.
- For text-to-SQL, if the LLM produces incorrect SQL (it can happen with very complex queries), you might need to refine the prompt or provide example query patterns. Using a more capable model or fine-tuning on your schema (few-shot examples) can imp ([Query Engine for Text-To-SQL: Everything You Need To Get Started](https://phoenix.arize.com/how-to-set-up-a-sql-router-query-engine-for-effective-text-to-sql/#:~:text=Conclusion))28†L259-L264】. The LlamaIndex framework allows plugging in different LLMs – experiment to see which works best for your data.

## Acknowledgments

- **LlamaIndex** – for the powerful framework that made integrating RAG and text-to-SQL relatively str ([Query Engine for Text-To-SQL: Everything You Need To Get Started](https://phoenix.arize.com/how-to-set-up-a-sql-router-query-engine-for-effective-text-to-sql/#:~:text=By%20defining%20two%20different%20tools%2C,a%20basic%20RAG%20use%20case))28†L228-L236】.  
- **Ollama** – for simplifying local model deployment. Running LLMs locally gives control and privacy.  
- **Qdrant** – for the efficient vector search capabilities.  
- **Streamlit** – for making UI development a breeze.

Feel free to explore the code in this repository to understand more. Each component (document index, router, SQL execution) is commented for clarity. If you have suggestions or run into issues, please open an issue or pull request. We welcome contributions!

**Happy querying!** 🎉

