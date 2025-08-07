# CrewAI Agentic Flow Demo

A demonstration of an agentic workflow using CrewAI Flows, featuring a Researcher Agent that uses Firecrawl search tools and a Writer Agent that generates comprehensive answers based on research findings.

## Overview

This project showcases how to build sophisticated AI workflows using CrewAI's Flows API to orchestrate multiple agents working together. The workflow demonstrates:

- **Event-driven architecture** using CrewAI Flows with `@start()` and `@listen()` decorators
- **Agent specialization** with dedicated Researcher and Writer agents
- **Tool integration** with a Firecrawl search tool for web research
- **State management** for maintaining data flow between workflow steps

## Architecture

### Workflow Flow

```
User Query → Researcher Agent → Writer Agent → Final Answer
              (with Firecrawl        (synthesizes
               search tool)          research data)
```

### Components

1. **ResearchFlow**: Main flow orchestrator using CrewAI Flows
2. **Researcher Agent**: Specializes in gathering information using web search
3. **Writer Agent**: Synthesizes research findings into comprehensive answers  
4. **FirecrawlSearchTool**: Web scraping and search tool (mock implementation included)

## Agent Roles

### Researcher Agent
- **Role**: Research Specialist
- **Goal**: Gather comprehensive and accurate information from web sources
- **Tools**: FirecrawlSearchTool
- **Capabilities**: 
  - Web search and content extraction
  - Source credibility assessment
  - Information organization and summarization

### Writer Agent
- **Role**: Content Writer and Synthesizer
- **Goal**: Create comprehensive, well-structured answers by synthesizing research findings
- **Capabilities**:
  - Information synthesis and organization
  - Clear, engaging content generation
  - Source attribution and fact verification

## Flow Logic

The workflow uses CrewAI's Flows API with the following structure:

1. **`@start()` initialize_research()**: Entry point that receives the user query
2. **`@listen()` conduct_research()**: Researcher agent gathers information using Firecrawl
3. **`@listen()` generate_answer()**: Writer agent synthesizes findings into final answer

Each step maintains state and passes data to the next step in the flow.

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd crewai-agentic-flow-demo
   ```

2. **Install dependencies**:
   ```bash
   pip install -e .
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Required API Keys**:
   - `OPENAI_API_KEY`: Required for CrewAI agents (primary LLM provider)
   - `FIRECRAWL_API_KEY`: Optional - demo includes mock implementation

## Usage

### Quick Start

Run the demo script:

```bash
python run_flow.py
```

This will present you with sample queries or allow you to enter a custom query.

### Programmatic Usage

```python
from src.crewai_agentic_flow.flows import ResearchFlow

# Create and run the flow
flow = ResearchFlow()
results = flow.run_flow("What are the latest AI developments?")

print("Research Findings:", results['research_findings'])
print("Final Answer:", results['final_answer'])
```

### Advanced Usage

```python
from src.crewai_agentic_flow.flows.research_flow import FlowState, ResearchFlow

# Initialize flow with structured state
flow = ResearchFlow()
flow.state = FlowState(query="Your research question")

# Run individual steps
query = flow.initialize_research()
research_findings = flow.conduct_research(query)
final_answer = flow.generate_answer(research_findings)
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: OpenAI API key for LLM access
- `FIRECRAWL_API_KEY`: Firecrawl API key for web scraping (optional)
- `CREWAI_TELEMETRY_ENABLED`: Set to `false` to disable telemetry

### Customization

#### Adding New Tools

```python
from crewai_tools import BaseTool

class CustomTool(BaseTool):
    # Implementation here
    pass

# Add to agents
researcher = create_researcher_agent(tools=[CustomTool()])
```

#### Extending the Flow

```python
class ExtendedResearchFlow(ResearchFlow):
    @listen(generate_answer)
    def post_process(self, final_answer: str) -> str:
        # Additional processing step
        return processed_answer
```

## Mock vs Real Integration

The demo includes mock implementations to work without API keys:

### Mock Mode (Default)
- Uses simulated search results
- No external API calls required
- Perfect for testing and development

### Real Integration
- Set `FIRECRAWL_API_KEY` in environment
- Real web scraping and search
- Production-ready functionality

## File Structure

```
crewai-agentic-flow-demo/
├── README.md
├── pyproject.toml
├── .env.example
├── run_flow.py                 # Main demo script
└── src/
    └── crewai_agentic_flow/
        ├── __init__.py
        ├── agents/
        │   ├── __init__.py
        │   ├── researcher_agent.py
        │   └── writer_agent.py
        ├── tools/
        │   ├── __init__.py
        │   └── firecrawl_tool.py
        └── flows/
            ├── __init__.py
            └── research_flow.py
```

## Example Output

```
🔍 Starting research flow for query: 'What are the latest AI developments?'

📚 Conducting research on: 'What are the latest AI developments?'
[Researcher Agent executes search and gathers information]

✍️ Generating comprehensive answer...
[Writer Agent synthesizes research into final answer]

📄 Final Answer:
Based on comprehensive research, here are the latest developments in AI:

1. **Large Language Models**: Recent advances in GPT-4, Claude, and other models...
2. **Multimodal AI**: Integration of text, image, and audio processing...
3. **AI Safety**: New frameworks for responsible AI development...

[Complete structured answer with sources and insights]
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/
```

### Code Quality

```bash
# Format code
black src/

# Lint code  
flake8 src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure `OPENAI_API_KEY` is set in your environment
2. **Import Errors**: Install the package with `pip install -e .`
3. **Flow Execution Errors**: Check that all dependencies are installed

### Debug Mode

Set verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewAI) for the excellent multi-agent framework
- [Firecrawl](https://firecrawl.dev/) for web scraping capabilities
- The open source AI community for inspiration and tools