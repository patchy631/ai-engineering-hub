# Auto Insurance Claim Processing

A streamlined application for processing auto insurance claims against policy documents using LLM-powered workflows.

## Overview

This application automates the analysis of auto insurance claims by retrieving relevant policy sections, comparing claim details against policy provisions, and providing structured recommendations for claim approval and payout amounts. It uses a combination of vector search retrieval, LLM-based reasoning, and workflow automation to streamline the claims processing workflow.

## Features

- Upload and process insurance claim files in JSON format
- Automated policy retrieval based on intelligent query generation
- Policy declaration document retrieval based on policy number
- Structured decision outputs including coverage determination, applicable deductible, and recommended settlement
- Streamlit-based user interface for easy interaction
- Traceability with Opik integration
- Asynchronous processing with proper error handling

## Architecture

The application consists of several components:

- **Streamlit UI**: Web interface for claim file upload and result display
- **LlamaIndex**: Vector storage and retrieval for policy documents
- **Workflow Engine**: Multi-step processing pipeline using LlamaIndex workflow tools
- **LLM Integration**: Using Ollama for structured reasoning and recommendations
- **Vector Store**: LlamaCloud for storing and retrieving policy documents
- **Tracing**: Opik for workflow tracing and monitoring

### Workflow Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Upload Claim│────▶│Generate     │────▶│Retrieve     │────▶│Generate     │
│ JSON File   │     │Policy       │     │Policy       │     │Recommend-   │
└─────────────┘     │Queries      │     │Text         │     │ation        │
                    └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                                                                   ▼
                                        ┌─────────────┐     ┌─────────────┐
                                        │Present      │◀────│Finalize     │
                                        │Decision     │     │Decision     │
                                        └─────────────┘     └─────────────┘
```

## Prerequisites

- Python 3.8+
- Ollama (with llama3.1 model installed)
- LlamaCloud account and API key
- Opik account for tracking (optional)
- Streamlit for UI rendering

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/auto-insurance-claim-processing.git
cd auto-insurance-claim-processing
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with the required environment variables:
```
LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key
ORGANIZATION_ID=your_llama_cloud_org_id
OPIK_API_KEY=your_opik_api_key
OPIK_WORKSPACE=your_opik_workspace
OPIK_PROJECT_NAME=your_opik_project_name
```

## Usage
1. Ensure you have Ollama LLM running locally. Check out the installation 
[here](https://github.com/ollama/ollama).


2. Start the Streamlit application:
```bash
streamlit run app.py
```

3. Upload a claim file (JSON format)
4. Review the generated recommendation and decision

### Example Claim File

```json
{
  "claim_number": "C12345",
  "policy_number": "P98765",
  "claimant_name": "John Smith",
  "date_of_loss": "2023-11-15",
  "loss_description": "Rear-end collision at stop light",
  "estimated_repair_cost": 3500.00,
  "vehicle_details": "2020 Toyota Camry"
}
```

### Example Output

```json
{
  "claim_number": "C12345",
  "covered": true,
  "deductible": 500.00,
  "recommended_payout": 3000.00,
  "notes": "Claim is covered under collision coverage. Deductible of $500 applies."
}
```

## Project Structure

- `app.py`: Streamlit web application
- `api.py`: Client connections for LlamaCloud, Ollama, and other APIs
- `declarations.py`: Handling for policy declaration documents
- `prompts.py`: LLM prompt templates
- `schema.py`: Pydantic models for structured data
- `workflows.py`: LlamaIndex workflow components
- `requirements.txt`: Package dependencies

## Workflow Process

1. **Load Claim Info**: Parse the uploaded JSON claim file
2. **Generate Policy Queries**: Use LLM to create targeted queries for policy retrieval
3. **Retrieve Policy Text**: Fetch relevant policy sections from the vector store
4. **Generate Recommendation**: Analyze claim against policy to create a structured recommendation
5. **Finalize Decision**: Convert the recommendation into a formal claim decision
6. **Output Result**: Return the decision to the user interface

## Development

### Adding New Features

To add new query types or processing steps:
1. Define new schema models in `schema.py`
2. Create additional prompt templates in `prompts.py`
3. Extend the workflow in `workflows.py` with new step methods

### Custom Policy Indexing

To index your own policy documents:
1. Format policy documents appropriately (markdown recommended)
2. Use LlamaCloud to create and populate the vector index
3. Update the index name in `api.py`

### Environment Setup for Development

For local development, you may want to set up a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Troubleshooting

- **Connection Issues**: Ensure all environment variables are properly set
- **LLM Errors**: Check that Ollama is running with the correct model loaded
- **Retrieval Problems**: Verify LlamaCloud API keys and permissions
- **UI Issues**: Make sure Streamlit is properly installed and running
- **Workflow Errors**: Check logs for specific error messages in each step

## Performance Considerations

- The application uses async processing to handle multiple requests efficiently
- Policy retrieval is optimized using vector search for faster results
- Consider batching multiple claims for better throughput in production

## Security Notes

- API keys should be kept secure and not committed to version control
- Consider implementing authentication for the Streamlit interface in production
- Ensure proper data handling procedures for sensitive insurance information


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
