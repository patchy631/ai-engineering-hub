
# AI News Generator with CrewAI Flows

This project leverages **CrewAI Flows** and Cohere's Command-R:7B model to build an advanced AI news generator with event-driven, agentic workflows!

## Features

- 🌊 **CrewAI Flows**: Event-driven workflow orchestration
- 🔄 **State Management**: Structured data flow between AI agents
- 🎯 **Task Chaining**: Sequential execution with @start and @listen decorators
- ⚡ **Optimized Performance**: Better control and coordination of AI agents
- 📊 **Real-time Feedback**: Visual flow execution progress

## Architecture

The application uses CrewAI Flows to create a structured, event-driven workflow:

```python
class AINewsGeneratorFlow(Flow[NewsGenerationState]):
    
    @start()
    def research_phase(self):
        # Research agent conducts comprehensive topic research
        # Updates state with research findings
        
    @listen(research_phase)
    def content_writing_phase(self, research_report: str):
        # Writing agent transforms research into engaging content
        # Uses structured state for data flow
```

### Flow Execution:
1. **Research Phase** (⚙️ `@start()`): Senior Research Analyst conducts comprehensive research
2. **Content Writing Phase** (🔊 `@listen(research_phase)`): Content Writer transforms research into engaging blog posts
3. **State Management**: Structured state ensures proper data flow between phases

## Installation and Setup

**Get API Keys**:
   - [Serper API Key](https://serper.dev/)
   - [Cohere API Key](https://dashboard.cohere.com/api-keys)

**Install Dependencies**:
   Ensure you have Python 3.11 or later installed.
   ```bash
   pip install crewai crewai-tools streamlit python-dotenv pydantic
   ```

**Environment Setup**:
   1. Copy `.env.example` to `.env`
   2. Add your API keys to the `.env` file
   
**Run the Application**:
   ```bash
   streamlit run app.py
   ```

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
