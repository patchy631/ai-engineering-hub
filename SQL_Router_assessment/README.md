# LlamaCloud SQL Router 🦙

A Streamlit-based application that combines RAG (Retrieval-Augmented Generation) and Text-to-SQL capabilities in a single query interface. This application can query both a LlamaCloud index for RAG-based retrieval and a SQL database containing city information.

## Features

- Query a SQL database containing US city population data
- Query a LlamaCloud index for semantic information about cities
- Automatic query routing to the appropriate tool
- Interactive chat interface
- Real-time data visualization
- Built-in example queries

## Prerequisites

- Python 3.7+
- OpenAI API key
- LlamaCloud account with API key (optional, for RAG features)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The application requires the following API keys and configuration:

1. **Required**:
   - OpenAI API key

2. **Optional** (for LlamaCloud features):
   - LlamaCloud API key
   - LlamaCloud Index Name
   - LlamaCloud Project Name
   - LlamaCloud Organization ID

## Running the Application

1. Start the Streamlit application:
```bash
streamlit run streamlit_application.py
```

2. Open your web browser and navigate to the URL shown in the terminal (typically `http://localhost:8501`)

3. Enter your API keys in the sidebar configuration panel

## Usage

1. Once the application is running and configured, you can:
   - Ask questions about city populations and statistics
   - Query semantic information about cities (if LlamaCloud is configured)
   - View the SQL database contents
   - Try example queries from the provided list

Example queries:
- "Which city has the highest population?"
- "What state is Houston located in?"
- "List all of the places to visit in Miami."
- "Compare the populations of New York City and Los Angeles."

## Database Schema

The application includes a SQL database with the following structure:

Table: `city_stats`
- `city_name` (String, Primary Key)
- `population` (Integer)
- `state` (String)

## Dependencies

- streamlit
- llama-index
- nest-asyncio
- sqlalchemy
- openai
- pandas

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.


## License

This repository is licensed under the MIT License. 

## Support

For support, please contact Sathvik Divili at divilisathvik@gmail.com

## Tweet Thread

Typefully twitter tweet thread draft link: https://typefully.com/t/Yv64cni
