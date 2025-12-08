# RAG & Text-to-SQL Agentic Workflow

This project builds an agentic workflow combining SQL querying with semantic search allowing users to ask questions about cities in natural language. The system/agent automatically routes the query to either a SQL query engine or a semantic search/RAG engine based on the question type. 

We use:

- **LlamaIndex** for orchestrating the agentic workflow
- **Qdrant VectorDB** for storing vector embeddings
- **Ollama** for locally serving Mistral-7B large language model
- **SQLite** for storing structured city data in a SQL database
- **Streamlit** to build the UI

A demo of the app is shown below: 

[Video demo](demo.gif)

You can also watch the full video on YouTube:

[Watch Full Video](https://youtu.be/etlCp9kqg8Y)

[Typefully Draft](https://typefully.com/preview/x/GtkzPoB)

## Directory structure
```
.
├── assets/                   # Images/logos for the UI
├── docs/                     # City PDF files for semantic search
├── app.py                    # Streamlit application
├── workflow.py               # Main agent logic 
├── demo.gif                  # Demo video for the app
├── requirements.txt          # Python dependencies
├── agent_workflow.html       # Flowchart of the agentic workflow
├── README.md                 # Readme file containing guidelines for the project
└── .gitignore                # Files/folders to exclude from version control
```
## Installation and setup

### Setup Qdrant VectorDB
Run Qdrant locally using Docker:  
   ```bash
   docker run -p 6333:6333 -p 6334:6334 \
   -v $(pwd)/qdrant_storage:/qdrant/storage:z \
   qdrant/qdrant
   ```

### Setup Ollama
Ollama is required to run the LLM locally. 
Install it from https://ollama.com

or install with a simple command
```bash
# setup ollama on linux 
curl -fsSL https://ollama.com/install.sh | sh
```
```bash
# setup ollama on macOS
brew install ollama
```  
After installation pull the Mistral-7B model
```bash
# pull mistral-7b model
ollama pull mistral:7b
```


### Install Dependencies

   Ensure you have Python 3.11 or later installed and create a virtual environment before installing the packages (recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

Then install the required dependencies using the command:

```bash
pip install -r requirements.txt
```

### Run the project


   Finally, run the app by running the following command:

   ```bash
   streamlit run app.py
   ```

## How It Works?

When a user asks a question:

1. **Query Routing**:
   
   - The system analyzes the user's question to determine if it's about city statistics or general knowledge (landmarks, history, etc.)

   - Statistics based questions (e.g., population, state data) are routed to the SQL engine.

   - Qualitative queries (e.g., culture, landmarks) are routed to the semantic search engine.

2. **SQL Engine**:

   - The LLM translates natural language queries into SQL.

   - These are then executed against the SQLite database containing city statistics.

3. **Semantic Search (RAG)**:

   - The system retrieves relevant information from city documents stored in the Qdrant vector database using similarity search.

   - The LLM then synthesizes a response based on the retrieved context.

4. **Response Generation**:

   - The agent system combines the results and displays the final generated response in the chat interface.

### Example Usage

Try asking questions like:

- Which city has the highest population?
- Where is the Space Needle located?
- List some places to visit in Hyderabad.
- What are some cultural differences between Mumbai and Los Angeles?


### Supported Cities
This project currently has support for following cities:

- **USA**: New York City, Los Angeles, Chicago, Houston, Miami, Seattle
- **India**: Mumbai, Delhi, Bengaluru, Hyderabad, Ahmedabad

### Customization

You can extend this application by:

- Adding more cities to the database
- Expanding the database schema with additional information  (e.g., area, population density etc.)
- Implementing more sophisticated query routing logic
- Adding support for additional file formats (e.g., CSV, JSON)

## Contact Me
For questions, or feedback, feel free to reach out to me at:
- [**Email**](mailto:nikhil.sfw@gmail.com)
- [**LinkedIn**](https://www.linkedin.com/in/nikhil-kotra/)
- [**GitHub**](https://www.github.com/nikhil-1e9)
