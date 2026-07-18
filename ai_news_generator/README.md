
# AI News Generator

This project leverages CrewAI Flows and Cohere's Command-R:7B model to build an AI news generator with an agentic workflow!

## Installation and setup

**Get API Keys**:
   - [Serper API Key](https://serper.dev/)
   - [Cohere API Key](https://dashboard.cohere.com/api-keys)


**Install Dependencies**:
   Ensure you have Python 3.11 or later installed.
   ```bash
   pip install crewai crewai-tools streamlit python-dotenv
   ```

## Architecture

This application uses CrewAI Flows to create an agentic workflow with two main phases:

### Phase 1: Research Phase (@start)
- **Agent**: Senior Research Analyst
- **Task**: Conduct comprehensive research on the given topic
- **Tools**: SerperDev (web search)
- **Output**: Structured research brief with citations

### Phase 2: Writing Phase (@listen)
- **Agent**: Content Writer  
- **Task**: Transform research into engaging blog post
- **Input**: Research output from Phase 1
- **Output**: Polished markdown blog post

The flow ensures that the writing phase only begins after the research phase completes, creating a structured agentic workflow.

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
