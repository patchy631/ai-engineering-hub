# RAG-SQL Assistant

A powerful application that combines Retrieval-Augmented Generation (RAG) and Text-to-SQL capabilities in a single interface.

## 📌 Introduction & Overview

The RAG-SQL Assistant provides a unified query experience that intelligently routes natural language questions to either database queries or document retrieval systems. By combining the structured data capabilities of SQL with the knowledge retrieval power of RAG, this tool delivers comprehensive answers to a wide range of questions about cities.

This project allows you to:

- Ask questions in natural language about city data
- Get direct SQL query results for structured questions
- Retrieve knowledge from documents for informational questions
- Experience intelligent query routing based on question intent

For a detailed explanation of this project, check out this Twitter thread:
<https://typefully.com/t/9Nq299N>

### Tech Stack

- **LlamaIndex**: Powers the workflow orchestration, RAG capabilities, and query routing
- **SQLAlchemy**: Handles database connection and SQL query execution
- **Streamlit**: Provides the user-friendly interface
- **OpenAI**: Drives natural language understanding and generation
- **LlamaCloud**: Manages the document index and retrieval
- **SQLite**: Stores structured city data

### Architecture

![Architecture](assets/architecture.png)

## ✨ Features

- 🧠 **Intelligent Query Routing**: Automatically determines whether to use RAG or SQL based on query type
- 📊 **SQL Query Generation**: Translates natural language to SQL for database queries
- 📚 **Document Retrieval**: Finds relevant information from documents for knowledge-based questions
- 💬 **Intuitive Chat Interface**: User-friendly Streamlit UI for conversation

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Git

### Clone the Repository

```bash
git clone https://github.com/patchy631/ai-engineering-hub.git
cd ai-engineering-hub/rag-sql-assistant
```

### Environment Setup

1. **OpenAI API Key**
   - Create an account at [OpenAI Platform](https://platform.openai.com/)
   - Generate an API key from your account dashboard
   - Copy the key for use in your `.env` file

2. **LlamaCloud Setup**
   - Sign up for a [LlamaCloud account](https://cloud.llamaindex.ai/)
   - Create a new project in your dashboard
   - Create a new index for your city documents
   - Obtain your API key, organization ID, project name, and index name

3. **Environment Variables**
   - Copy the example environment file to create your own:

     ```bash
     cp .env.example .env
     ```

   - Open the `.env` file and add your API keys and configuration:

     ```yaml
     OPENAI_API_KEY=your_openai_api_key
     LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key
     LLAMA_CLOUD_ORG_ID=your_organization_id
     LLAMA_CLOUD_PROJECT=your_project_name
     LLAMA_CLOUD_INDEX=your_index_name
     ```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## 🖥️ Usage

### Running the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The app will be available at <http://localhost:8501>

### Adding Wikipedia Files to LlamaCloud

1. Download Wikipedia pages as PDFs for the following cities:
   - [New York City](https://en.wikipedia.org/wiki/New_York_City)
   - [Los Angeles](https://en.wikipedia.org/wiki/Los_Angeles)
   - [Chicago](https://en.wikipedia.org/wiki/Chicago)
   - [Houston](https://en.wikipedia.org/wiki/Houston)
   - [Miami](https://en.wikipedia.org/wiki/Miami)
   - [Seattle](https://en.wikipedia.org/wiki/Seattle)

2. To download a Wikipedia page as PDF:
   - Open the Wikipedia page in your browser
   - Use Ctrl+P (Windows/Linux) or Cmd+P (Mac) to open the print dialog
   - Select "Save as PDF" as the destination
   - Save the file with the city name

3. Upload the PDFs to your LlamaCloud index:
   - Log in to your LlamaCloud account
   - Navigate to your project and index
   - Click "Upload" and select all your PDF files
   - Wait for the indexing process to complete

### Example Queries

#### SQL Queries

- "What is the population of New York City?"
- "Which city has the highest population?"
- "List all cities in California."

#### RAG Queries

- "Tell me about the history of Chicago."
- "What are famous landmarks in Seattle?"
- "Describe the climate of Miami."

## 🌐 Deployment

### Local Deployment

For regular local usage, run the Streamlit application as described in the Usage section.

### Cloud Deployment

#### Streamlit Cloud

1. Push your code to a GitHub repository
2. Sign up for [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app and connect to your GitHub repository
4. Set the same environment variables in Streamlit Cloud's secrets management
5. Deploy the application

#### Alternative Cloud Options

1. **Heroku**
   - Create a `Procfile` with: `web: streamlit run app.py`
   - Add a `setup.sh` file for Streamlit configuration
   - Deploy using the Heroku CLI or GitHub integration

2. **AWS/GCP/Azure**
   - Create a virtual machine instance
   - Clone your repository on the VM
   - Install dependencies and set up environment variables
   - Run the application with proper firewall/network settings

## 🤝 Contributing

Contributions are welcome! Here's how you can help improve this project:

### Contribution Process

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Test thoroughly
5. Commit with clear, descriptive messages
6. Push to your fork and submit a pull request

### Coding Standards

- Follow PEP 8 style guidelines for Python code
- Include docstrings for all functions and classes
- Write unit tests for new features
- Ensure compatibility with Python 3.9+

## 🧩 Project Structure

```yaml
rag-sql-assistant/
├── README.md              # Project documentation
├── app.py                 # Main Streamlit application
├── assets/                # Images and other assets
├── data/                  # Data files
├── requirements.txt       # Python dependencies
└── src/                   # Source code
    ├── config.py          # Configuration utilities
    ├── database/          # Database components
    │   └── city_stats.py  # City statistics database
    ├── query_processor.py # Query processing logic
    ├── rag/               # RAG components
    │   └── cloud_index.py # LlamaCloud RAG implementation
    ├── router/            # Query routing logic
    │   ├── tools.py       # SQL and RAG tools
    │   └── workflow.py    # Router workflow implementation
    └── ui/                # UI components
        ├── chat.py        # Chat interface
        ├── explainer.py   # Explainer section
        ├── main.py        # Main UI components
        └── utils.py       # UI utilities
```

## 🔄 How It Works

The system uses a router workflow to analyze each query and determine whether it should be processed using SQL or RAG:

1. **Query Analysis**: An LLM evaluates the query to determine its intent
2. **Tool Selection**: Based on the intent, either the SQL or RAG tool is selected
3. **Query Execution**: The appropriate system processes the query
4. **Response Generation**: Results are formatted and presented to the user

## 🔗 Community

### Daily Dose of Data Science

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources.

[Subscribe now!](https://join.dailydoseofds.com)

![DDODS](assets/ddods_banner.png)

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.
