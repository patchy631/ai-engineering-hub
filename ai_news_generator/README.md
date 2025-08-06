
# AI News Generator - CrewAI Flows Edition

This project leverages **CrewAI Flows** and Cohere's Command-R:7B model to build an advanced AI news generator with enhanced agentic workflow orchestration!

## ✨ New Features with CrewAI Flows

- **Enhanced Workflow Management**: Sequential flow execution with proper state management
- **Better Error Handling**: Comprehensive error tracking and recovery mechanisms
- **Improved Agent Coordination**: Structured communication between research and writing agents
- **State Persistence**: Maintains context and data flow between different phases
- **Flow Visualization**: Clear understanding of workflow execution steps

## Architecture

The application now uses CrewAI Flows with the following structure:

1. **NewsGenerationState**: Pydantic model for state management
2. **NewsGenerationFlow**: Flow class with decorated methods
   - `@start()` - Research phase with Senior Research Analyst
   - `@listen()` - Content generation phase with Content Writer
3. **Sequential Execution**: Research → Content Generation → Output

## Installation and Setup

**Get API Keys**:
   - [Serper API Key](https://serper.dev/)
   - [Cohere API Key](https://dashboard.cohere.com/api-keys)

**Install Dependencies**:
   Ensure you have Python 3.11 or later installed.
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install manually:
   ```bash
   pip install crewai crewai-tools streamlit python-dotenv pydantic
   ```

**Environment Setup**:
   Create a `.env` file in the project root:
   ```
   SERPER_API_KEY=your_serper_api_key_here
   COHERE_API_KEY=your_cohere_api_key_here
   ```

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
