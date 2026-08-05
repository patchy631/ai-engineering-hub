# DDS Assignment: Combining RAG and Text-to-SQL in a Single Query Interface

## Twitter Thread
Check out the full project details in our Twitter thread:  
[\[Typefully Draft Link\]  ](https://typefully.com/t/4Ubf8WG)


Welcome to this exciting project that blends Retrieval-Augmented Generation (RAG) and Text-to-SQL into a seamless query interface! Powered by OpenAI's LLMs, LlamaCloud, and SQLite, it delivers rich insights from structured and unstructured data.

## Features

- **Text-to-SQL**: Query a SQLite database for structured data (e.g., city populations).  
- **RAG with LlamaCloud**: Retrieve historical or unstructured data via LlamaCloud.  
- **Workflow Orchestration**: A custom LlamaIndex workflow to manage tools and results.  
- **Interactive UI**: A Streamlit-based interface with real-time updates.

## Project Structure

- **`Demo.mp4`**: A short video demo showcasing the interface in action.  
- **`Flow_diagram.png`**: A visual guide to the system architecture.  
- **`llamacloud_router.ipynb`**: Jupyter notebook with the workflow implementation.  
- **`my_agent.py`**: Core logic for workflow, tool integration, and query processing.  
- **`script.py`**: Streamlit app for the user interface and workflow integration.  
- **`city_stats.db`**: Persistent SQLite database with city statistics (auto-created).  
- **`README.md`**: This file with setup and usage instructions.  
- **`requirements.txt`**: List of required Python packages.

## Prerequisites

- Python 3.8 or higher  
- API keys for OpenAI and LlamaCloud  
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Combining_RAG_and_Text-to-SQL_Assignment_submission
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export LLAMA_CLOUD_API_KEY="your-llama-cloud-api-key"
   export LLAMA_CLOUD_ORG_ID="your-llama-cloud-organization-id"
   ```

## Usage

1. **Run the Streamlit Application**:
   ```bash
   streamlit run script.py
   ```

2. **Enter Queries**:
   - Examples:  
     - "Which city has the highest population?"  
     - "What is the historical name of Los Angeles?"  
     - "How do people in Chicago get around?"  

3. **View Results**:
   - Watch step-by-step updates and the final answer in the Streamlit UI.  
   - Check `Demo.mp4` for a live demo.

4. **Explore the Diagram**:
   - View `Flow_diagram.png` for the system architecture.

5. **Notebook Option**:
   - Run `llamacloud_router.ipynb` in Jupyter for an interactive workflow view.

## Database Details

The SQLite database (`city_stats.db`) stores city data with this schema:

| City Name       | Population | State       |
|-----------------|------------|-------------|
| New York City   | 8,336,000  | New York    |
| Los Angeles     | 3,822,000  | California  |
| Chicago         | 2,665,000  | Illinois    |
| Houston         | 2,303,000  | Texas       |
| Miami           | 449,514    | Florida     |
| Seattle         | 749,256    | Washington  |

- Auto-generated with sample data if missing.

## Key Components

### Workflow (`EnhancedRouterOutputAgentWorkflow`)

- Manages query routing with LlamaIndex.  
- Logs steps and infers tools (e.g., `sql_tool` for population, `llama_cloud_tool` for history).

### Tools

- **`sql_tool`**: Queries the SQLite database.  
- **`llama_cloud_tool`**: Fetches data from LlamaCloud.

## Customization

- **New Tools**: Edit `my_agent.py` to add tools to `EnhancedRouterOutputAgentWorkflow`.  
- **UI Adjustments**: Modify `script.py` to enhance the Streamlit interface.  
- **Query Logic**: Update `infer_tools` in `my_agent.py` for better tool selection.

## Troubleshooting

- **API Errors**: Verify API keys in environment variables.  
- **Database Issues**: Delete `city_stats.db` and rerun to regenerate.  
- **Streamlit/Jupyter Failures**: Ensure Python version and packages match prerequisites.

## Contributing

- Fork the repo and submit pull requests with enhancements.  
- Report issues or ideas via GitHub Issues.

## License

MIT License. See the `LICENSE` file for details.

## Acknowledgments

- [OpenAI](https://openai.com) for LLM support.  
- [LlamaCloud](https://llama.cloud) for RAG features.  
- [Streamlit](https://streamlit.io) for the UI.  
- [Jupyter](https://jupyter.org) for notebook support.