
# AI News Generator

This project leverages **CrewAI Flows** and Cohere's Command-R:7B model to build a modular, agentic AI news generator! 

The application has been refactored to use CrewAI's new Flow-based architecture, providing better modularity, state management, and workflow orchestration.

## ✨ Features

- **Flow-Based Architecture**: Built using CrewAI Flows with `@start` and `@listen` decorators
- **Two-Phase Workflow**: Research phase followed by content writing phase
- **Modular Design**: Separate agents for research and content writing
- **State Management**: Proper state handling between workflow phases
- **Multiple Interfaces**: Both CLI and Streamlit web interface
- **Structured Output**: Well-formatted markdown blog posts with citations

## 🏗️ Architecture

The application uses a **Flow-based architecture** with two main phases:

```
┌─────────────────┐    @start     ┌─────────────────┐
│  Research Phase │──────────────▶│  Writing Phase  │
│                 │    @listen    │                 │
├─────────────────┤               ├─────────────────┤
│ • Web search    │               │ • Content       │
│ • Fact checking │               │   generation    │
│ • Source        │               │ • Formatting    │
│   validation    │               │ • Citations     │
└─────────────────┘               └─────────────────┘
```

### Core Components

- **`NewsGeneratorFlow`**: Main Flow class orchestrating the workflow
- **Research Agent**: Senior Research Analyst for comprehensive research
- **Writing Agent**: Content Writer for transforming research into engaging content
- **State Management**: Pydantic models for structured data flow

## Installation and setup

**Get API Keys**:
   - [Serper API Key](https://serper.dev/)
   - [Cohere API Key](https://dashboard.cohere.com/api-keys)

**Install Dependencies**:
   Ensure you have Python 3.11 or later installed.
   ```bash
   pip install crewai crewai-tools streamlit python-dotenv
   ```

**Environment Setup**:
   Create a `.env` file in the project directory:
   ```env
   SERPER_API_KEY=your_serper_api_key_here
   COHERE_API_KEY=your_cohere_api_key_here
   ```

## 🚀 Usage

### Command Line Interface

Run the flow directly from the command line:

```bash
# Basic usage
python main.py --topic "Latest developments in artificial intelligence"

# Save to file
python main.py --topic "Climate change solutions" --output article.md

# Verbose mode
python main.py --topic "Blockchain innovations" --verbose
```

### Streamlit Web Interface

Launch the interactive web interface:

```bash
streamlit run app.py
```

Then open your browser to the displayed URL (typically `http://localhost:8501`).

### Programmatic Usage

Use the flow in your own Python code:

```python
from news_flow import NewsGeneratorFlow

# Create and run the flow
flow = NewsGeneratorFlow()
result = flow.kickoff(inputs={"topic": "Your topic here"})
print(result)

# Or use the convenience function
from news_flow import generate_content_with_flow

content = generate_content_with_flow("Your topic here")
print(content)
```

## 🔧 Flow Implementation Details

### Flow Structure

The `NewsGeneratorFlow` class implements the CrewAI Flow pattern:

```python
class NewsGeneratorFlow(Flow[ResearchState]):
    @start()
    def research_phase(self) -> str:
        # Initial research using Senior Research Analyst
        
    @listen(research_phase)
    def writing_phase(self, research_results: str) -> str:
        # Content writing using research results
```

### State Management

The flow uses structured state management with Pydantic models:

```python
class ResearchState(BaseModel):
    topic: str
    research_brief: str
    sources: list[str] = []
    key_findings: list[str] = []
```

### Agent Specialization

- **Senior Research Analyst**: Handles web research, fact-checking, and source validation
- **Content Writer**: Transforms research into engaging, well-structured blog content

## 🧪 Testing

Test the basic functionality:

```bash
# Test the flow with a simple topic
python main.py --topic "Python programming" --verbose

# Test the web interface
streamlit run app.py
```

## 📁 Project Structure

```
ai_news_generator/
├── app.py              # Streamlit web interface
├── main.py            # CLI entry point
├── news_flow.py       # Core Flow implementation
├── README.md          # This file
└── .env              # Environment variables (create this)
```

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
