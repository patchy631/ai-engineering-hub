# AI Agent with RAG and SQL Capabilities

This repository contains an intelligent agent implementation that combines Retrieval Augmented Generation (RAG) with SQL capabilities to answer questions based on documents and database data.

## 📚 Components

### 1. Jupyter Notebook (`rag_sql.ipynb`)
The notebook contains the core implementation of the AI agent with:
- RAG (Retrieval Augmented Generation) implementation
- SQL query generation and execution
- Document processing and indexing
- Intelligent query routing between RAG and SQL
- Example usage and test cases

### 2. Streamlit Web Interface (`rag_sql_app_upload.py`)
A user-friendly web interface that provides:
- PDF document upload and processing
- Interactive chat interface
- Automatic query handling
- Real-time responses
- Chat history tracking

## 🚀 Getting Started

### Prerequisites
```bash
pip install -r requirements.txt
```

Required packages:
- streamlit
- llama-index
- openai
- pandas
- python-dotenv
- sentence-transformers
- PyPDF2

### Setting Up

1. **OpenAI API Key**
   - Get your API key from [OpenAI Platform](https://platform.openai.com/account/api-keys)
   - You can input it directly in the Streamlit interface

2. **Running the Notebook**
   ```bash
   jupyter notebook rag_sql.ipynb
   ```
   - Follow the cells in sequence
   - Modify the example queries as needed
   - Experiment with different documents and databases

3. **Running the Streamlit App**
   ```bash
   streamlit run rag_sql_app_upload.py
   ```
   - Open the displayed URL in your browser
   - Enter your OpenAI API key in the sidebar
   - Upload PDFs or select a directory containing PDFs
   - Start asking questions!

## 💡 Features

### RAG Capabilities
- Document chunking and indexing
- Semantic search
- Context-aware responses
- Source attribution

### SQL Capabilities
- Automatic SQL query generation
- Database schema understanding
- Query execution and result formatting
- Error handling

### Web Interface
- Modern, responsive design
- Real-time chat interface
- Document management
- Session persistence
- Error handling and user feedback

## 📖 Usage

1. **Document Upload**
   - Use the sidebar to upload PDF files
   - Or specify a directory containing PDFs
   - Click "Process PDFs" to index the documents

2. **Asking Questions**
   - Type your question in the input field
   - The agent automatically determines whether to use RAG or SQL
   - View responses in the chat interface
   - Chat history is preserved during the session

3. **Best Practices**
   - Upload relevant documents for better context
   - Ask clear, specific questions
   - Check the chat history for context
   - Ensure proper PDF formatting for best results

## 🔧 Customization

### Notebook Customization
- Modify the chunking parameters
- Adjust the embedding model
- Change the LLM model
- Customize the SQL database connection

### Streamlit App Customization
- Modify the UI styling in the CSS section
- Adjust the document processing parameters
- Change the chat interface layout
- Add additional features as needed

## 🤝 Contributing

Feel free to:
- Open issues
- Submit pull requests
- Suggest improvements
- Report bugs

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LlamaIndex](https://www.llamaindex.ai/)
- Powered by [OpenAI](https://openai.com/)
- UI built with [Streamlit](https://streamlit.io/)
