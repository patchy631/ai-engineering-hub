
# AI News Generator with CrewAI Flows

This project leverages **CrewAI Flows** and Cohere's Command-R:7B model to build an intelligent, agentic AI news generator! The application now uses CrewAI's Flow architecture for better workflow orchestration, event-driven processing, and modular design.

## 🚀 What's New: CrewAI Flows Implementation

This version features a complete refactor using CrewAI Flows with the following improvements:
- **Event-driven workflow** using `@start` and `@listen` decorators
- **State management** for seamless data passing between phases
- **Modular architecture** making it easy to extend with additional workflow steps
- **Better error handling** and workflow control
- **Two-phase process**: Research → Content Writing

## 🔧 Installation and Setup

### Prerequisites
- Python 3.11 or later
- API Keys required:
  - [Serper API Key](https://serper.dev/) for web search
  - [Cohere API Key](https://dashboard.cohere.com/api-keys) for LLM

### Install Dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install crewai>=0.80.0 crewai-tools>=0.15.0 streamlit>=1.30.0 python-dotenv>=1.0.0 pydantic>=2.0.0
```

### Environment Setup
Create a `.env` file in the project directory:
```env
SERPER_API_KEY=your_serper_api_key_here
COHERE_API_KEY=your_cohere_api_key_here
```

## 🎯 Usage

### Run Streamlit Web Interface
```bash
streamlit run app.py
```

The web interface provides:
- **Topic Input**: Enter any topic you want to research and write about
- **Temperature Control**: Adjust creativity level (0.0-1.0)
- **Two-tab Results**: View both final article and research results
- **Download Options**: Save both research and final content as markdown files

### Run Command Line Interface
```bash
python main.py
```

Or use the Flow programmatically:
```python
from main import generate_news_content

# Generate content for a topic
result = generate_news_content("Latest AI developments", temperature=0.7)

print(f"Topic: {result['topic']}")
print(f"Research: {result['research_results'][:200]}...")
print(f"Article: {result['final_content'][:200]}...")
```

## 🔄 CrewAI Flow Architecture

### Flow Structure
```python
class NewsGeneratorFlow(Flow[NewsGeneratorState]):
    @start()
    def research_topic(self) -> str:
        # Phase 1: Comprehensive research using Senior Research Analyst
        
    @listen(research_topic)
    def write_content(self, research_results: str) -> str:
        # Phase 2: Transform research into engaging content
```

### Flow Phases
1. **🔍 Research Phase** (`@start`):
   - Senior Research Analyst agent researches the topic
   - Gathers recent developments, trends, expert opinions
   - Performs fact-checking and source verification
   - Returns structured research brief

2. **✍️ Content Writing Phase** (`@listen`):
   - Content Writer agent transforms research into blog post
   - Maintains factual accuracy while creating engaging content
   - Formats output in markdown with proper citations
   - Returns polished article

### State Management
The Flow uses instance variables for state management:
- `topic`: The research topic
- `research_results`: Output from research phase
- `final_content`: Final blog post content
- `temperature`: LLM temperature setting

## 🧪 Testing

Run the test suite to verify the Flow implementation:
```bash
python test_flow.py
```

The tests verify:
- Flow structure and initialization
- State management functionality  
- Method existence and decorators
- Event-driven workflow setup

## 📁 Project Structure

```
ai_news_generator/
├── main.py              # CrewAI Flow implementation
├── app.py               # Streamlit web interface
├── test_flow.py         # Test suite for Flow
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── .env                # Environment variables (create this)
```

## 🔧 Extending the Flow

The modular Flow architecture makes it easy to add new phases:

```python
@listen(write_content)
def review_content(self, final_content: str) -> str:
    # Add content review phase
    reviewer_agent = Agent(...)
    review_task = Task(...)
    # ... implementation
    
@listen(review_content)  
def publish_content(self, reviewed_content: str) -> str:
    # Add publishing phase
    # ... implementation
```

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## 🤝 Contribution

Contributions are welcome! The new CrewAI Flow architecture makes it easier to contribute:
- Add new workflow phases
- Improve agent prompts and behaviors  
- Enhance state management
- Add new output formats

Please fork the repository and submit a pull request with your improvements.
