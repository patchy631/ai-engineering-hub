# Audio Index MCP Server for Pixeltable

This MCP (Model-Client-Protocol) server provides a powerful audio indexing and search capability built on top of the Pixeltable SDK. It allows you to:

1. Create searchable indexes of audio content
2. Transcribe audio files using OpenAI's Whisper model
3. Perform semantic search on audio content using embeddings
4. Retrieve relevant audio segments based on natural language queries

## Features

- **Audio Transcription**: Automatically transcribes audio files using OpenAI's Whisper model
- **Chunking**: Splits audio into manageable segments for better search precision
- **Sentence Splitting**: Further divides transcriptions into sentences for fine-grained retrieval
- **Semantic Search**: Uses sentence embeddings to find content based on meaning, not just keywords
- **Multiple Indexes**: Create and manage multiple audio indexes for different collections

## Setup

### Clone the repo
```bash
gh repo clone pixeltable/mcp-server-pixeltable
```

### Docker Setup

#### Build the Docker image
```bash
cd servers/audio-index
docker build -t audio-index-mcp-server .
```

#### Run the Docker container
```bash
docker run -p 8080:8080 audio-index-mcp-server
```

This will start the MCP server on port 8080, making it accessible at `http://localhost:8080`.


## Add the tool to Cursor

1. Go to Cursor MCP settings
2. Add MCP > Add Name > Type = 'SSE'
3. For the URL, enter: `http://localhost:8080/sse`

## Available Tools

The server provides the following tools:

1. **setup_audio_index**: Create a new audio index
   - Parameters: `table_name` (name for your index), `openai_api_key` (for Whisper transcription)

2. **insert_audio**: Add an audio file to an index
   - Parameters: `table_name` (index to use), `audio_location` (URL or path to audio file)

3. **query_audio**: Search for content in an audio index
   - Parameters: `table_name` (index to search), `query_text` (your search query), `top_n` (number of results, default=5)

4. **list_tables**: Show all available audio indexes


## Requirements

The server requires the following dependencies:
- pixeltable
- openai-whisper
- sentence-transformers
- mcp
- uvicorn
- starlette
- and other dependencies listed in requirements.txt