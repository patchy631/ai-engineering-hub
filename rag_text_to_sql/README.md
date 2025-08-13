# City Information Assistant
A smart chatbot that combines RAG and SQL capabilities to answer questions about US cities. This application uses LlamaIndex for orchestration, GPT-4o-mini for natural language understanding, and provides a clean Streamlit interface.

## Features
- Unified interface combining RAG and SQL in one chatbot
- Smart routing using GPT-4o-mini to select appropriate tools
- Efficient workflow system for query execution
- Dual data sources merging statistics with Wikipedia content
- User-friendly Streamlit chat interface
## Getting Started
Follow these instructions to set up and run the project on your local machine.

### Prerequisites
- Python 3.8 or higher
- Git (optional)
### Installation
1. Clone the repository (optional)
```bash
git clone https://github.com/yourusername/city-information-assistant.git
cd city-information-assistant
 ```
```

2. Create and activate a virtual environment
```bash
python -m venv your_venv_name
your_venv_name\Scripts\activate
 ```

3. Create a requirements.txt file
Create a file named requirements.txt with the following content:

```plaintext
streamlit
llama-index-core
llama-index-llms-openai
llama-index-indices-managed-llama-cloud
python-dotenv
nest-asyncio
sqlalchemy
 ```

4. Install dependencies
```bash
pip install -r requirements.txt
 ```

5. Set up environment variables
Create a .env file in the project root directory with the following content:

```plaintext
OPENAI_API_KEY=your_openai_api_key
ORG_ID=your_llamacloud_organization_id
API_KEY=your_llamacloud_api_key
NAME=your_llamacloud_index_name
 ```

Replace the placeholder values with your actual API keys and credentials.

### Running the Application
1. Start the Streamlit app
```bash
streamlit run app.py
 ```

2. Access the application
Open your web browser and navigate to:

```plaintext
http://localhost:8501
 ```

## Usage
Once the application is running, you can:

1. Type questions about US cities in the chat input
2. Ask about population statistics (e.g., "What is the population of Chicago?")
3. Ask general knowledge questions about cities (e.g., "Tell me about the history of Seattle")
4. The application will automatically route your question to the appropriate data source
## Project Structure
- app.py : Main application file containing the Streamlit UI and workflow logic
- .env : Environment variables for API keys and configuration
- requirements.txt : Python dependencies
## Technologies Used
- Streamlit : For the web interface
- LlamaIndex : For RAG orchestration and workflow management
- OpenAI GPT-4o-mini : For natural language understanding
- SQLite : For in-memory database storage
- SQLAlchemy : For database ORM and query management
- LlamaCloud : For document indexing and semantic search
## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- LlamaIndex for providing the tools for building RAG applications
- OpenAI for the GPT models
- Streamlit for the easy-to-use web framework