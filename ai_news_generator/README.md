
# AI News Generator

This project leverages **CrewAI Flows** and Cohere's Command-R model to build an AI news generator with an agentic workflow!

> **🚀 GitHub Issue #168 Implementation**: This project has been refactored to use CrewAI Flows for creating structured, event-driven agentic workflows with better state management and modularity.

## 🆕 What's New - CrewAI Flows Implementation

This project now includes two implementations:

### 1. **Legacy Implementation** (`app.py`)
- Original crew-based approach
- Direct agent coordination
- Maintained for backwards compatibility

### 2. **New CrewAI Flows Implementation** (`app_flow.py`, `news_flow.py`)
- Event-driven workflow architecture  
- Structured state management using Pydantic models
- Better error handling and debugging
- Modular, reusable flow components
- Enhanced progress tracking

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

## 🚀 Running the Application

### Option 1: CrewAI Flows Implementation (Recommended)
```bash
streamlit run app_flow.py
```

### Option 2: Legacy Implementation (Backwards Compatibility)
```bash
streamlit run app.py  
```

## 🔧 Environment Variables

Create a `.env` file in the project directory:
```bash
COHERE_API_KEY=your_cohere_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

## 🧪 Testing

Run the validation tests to ensure everything is working:

```bash
# Structure validation (no dependencies required)
python test_simple.py

# Full functionality tests (requires API keys)
python test_flow.py
```

## 🔀 CrewAI Flows Architecture

The new implementation follows CrewAI's flows pattern:

```
🔍 Research Phase (@start)
    ↓
✍️ Content Generation (@listen) 
    ↓
🏁 Finalization (@listen)
```

### Key Components:

- **`NewsFlowState`**: Pydantic model for state management
- **`AINewsGeneratorFlow`**: Main flow class with event-driven methods
- **`ResearchReport`** & **`BlogPost`**: Structured output models
- **State Management**: Automatic state persistence between flow steps

### Benefits of Flows:

- **🔄 Event-Driven**: Each step automatically triggers the next
- **📊 State Management**: Structured data flow between components  
- **🛠️ Better Debugging**: Clear visibility into workflow progress
- **🧩 Modularity**: Reusable, testable flow components
- **⚡ Error Handling**: Built-in error recovery and validation

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## 📋 Migration Guide

If you're upgrading from the legacy implementation:

### Programmatic Usage (Old vs New)

**Legacy approach:**
```python
result = generate_content("AI trends")
content = result.raw
```

**New flows approach:**  
```python
from news_flow import kickoff_news_flow

result = kickoff_news_flow("AI trends")
content = result["blog_post"]
word_count = result["word_count"]
```

### Backwards Compatibility

- ✅ The original `app.py` still works unchanged
- ✅ All existing functionality is preserved
- ✅ New features are additive, not breaking changes
- ✅ Same API keys and environment setup

## 🤝 Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.

### Related Issues
- **GitHub Issue #168**: ✅ Implemented CrewAI flows for agentic workflows
