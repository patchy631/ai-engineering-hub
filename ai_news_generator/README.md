
# 🤖 AI News Generator with CrewAI Flows

An advanced AI-powered news article generator that uses **CrewAI Flows** to orchestrate multiple specialized AI agents in a sophisticated multi-phase workflow. This project demonstrates the power of **agentic workflows** for creating comprehensive, well-researched, and professionally edited content.

## ✨ Features

### 🔄 Multi-Phase CrewAI Flow Workflow
- **Phase 1: Research** - Comprehensive topic investigation with fact-checking
- **Phase 2: Content Creation** - Strategic content planning and writing
- **Phase 3: Editing** - Professional copy editing and technical review
- **Phase 4: Finalization** - Article structuring and quality metrics

### 🤖 Specialized AI Agents
- **Research Team**: Senior Research Analyst, Fact Checker, Data Synthesizer
- **Content Team**: Content Strategist, Content Writer, SEO Specialist  
- **Editing Team**: Copy Editor, Technical Editor, Publishing Editor

### 📊 Advanced Features
- Real-time workflow progress tracking
- Source credibility assessment
- Readability analysis and scoring
- Professional markdown formatting
- Comprehensive citation management
- Processing time and quality metrics

### 🎯 Professional Output
- Well-structured articles with proper headings
- Inline citations and references
- SEO-optimized content
- Quality metrics and readability scores
- Downloadable markdown and summary reports

## 🏗️ Architecture

```
ai_news_generator/
├── src/ai_news_flow/              # Core flow implementation
│   ├── main.py                    # Main flow orchestrator
│   ├── models.py                  # Pydantic data models
│   ├── tools/                     # Custom tools
│   │   └── custom_tools.py        # Credibility checker, readability analyzer
│   └── crews/                     # Agent crews
│       ├── research_crew/         # Research phase agents
│       ├── content_crew/          # Content creation agents
│       └── editing_crew/          # Editing and finalization agents
├── app.py                         # Streamlit web interface
├── pyproject.toml                 # Project dependencies
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or later
- API Keys (see setup section)

### Installation

1. **Clone and setup**:
   ```bash
   cd ai_news_generator
   pip install -e .
   ```

2. **Get API Keys**:
   - [Serper API Key](https://serper.dev/) - For web search functionality
   - [Cohere API Key](https://dashboard.cohere.com/api-keys) - For LLM processing

3. **Configure Environment**:
   Create a `.env` file:
   ```env
   SERPER_API_KEY=your_serper_key_here
   COHERE_API_KEY=your_cohere_key_here
   ```

4. **Run the Web Interface**:
   ```bash
   streamlit run app.py
   ```

5. **Or use Command Line**:
   ```bash
   python src/ai_news_flow/main.py "Your topic here"
   ```

## 💡 Usage Examples

### Web Interface
1. Open the Streamlit app
2. Enter your topic (e.g., "AI developments in healthcare 2025")
3. Adjust settings (temperature, max sources)
4. Click "Generate Article"
5. Watch the real-time workflow progress
6. Download the final article and metrics

### Command Line
```bash
# Generate article about AI trends
python src/ai_news_flow/main.py "Artificial Intelligence trends in 2025"

# The flow will automatically:
# 1. Research the topic comprehensively
# 2. Create engaging content
# 3. Edit and polish the article
# 4. Output the final result
```

## 🎛️ Configuration Options

- **Temperature**: Control creativity vs focus (0.0-1.0)
- **Max Sources**: Number of research sources to gather (5-20)
- **Topic Specificity**: More specific topics yield better results

## 🔧 Advanced Features

### CrewAI Flow Integration
- Uses `@start()`, `@listen()` decorators for flow control
- State management with Pydantic models
- Automatic phase transitions
- Error handling and recovery

### Custom Tools
- **Source Credibility Tool**: Evaluates source reliability
- **Readability Analyzer**: Calculates reading difficulty
- **Enhanced Search**: Structured search results

### Quality Metrics
- Processing time tracking
- Word count analysis
- Readability scoring
- Source credibility assessment

## 📈 Workflow Details

### Phase 1: Research (🔍)
1. **Senior Research Analyst** searches for comprehensive information
2. **Fact Checker** verifies accuracy and credibility
3. **Data Synthesizer** organizes findings into structured report

### Phase 2: Content Creation (✍️)
1. **Content Strategist** plans article structure and narrative
2. **Content Writer** creates engaging, accessible content
3. **SEO Specialist** optimizes for search and readability

### Phase 3: Editing (📝)
1. **Copy Editor** improves grammar, style, and clarity
2. **Technical Editor** verifies facts and citations
3. **Publishing Editor** finalizes formatting and structure

### Phase 4: Finalization (🎯)
1. Creates structured NewsArticle object
2. Calculates final metrics
3. Prepares downloadable outputs

## 🛠️ Development

### Project Structure
- Uses **Poetry** for dependency management
- **Pydantic** for data validation
- **CrewAI Flows** for workflow orchestration
- **Streamlit** for web interface

### Running Tests
```bash
pytest  # Run test suite (when tests are implemented)
```

### Code Quality
```bash
black src/  # Format code
isort src/  # Sort imports
flake8 src/  # Check style
```

## 🤝 Contributing

We welcome contributions! Here are ways to help:

1. **Bug Reports**: Open issues with detailed descriptions
2. **Feature Requests**: Suggest new functionality
3. **Code Contributions**: Submit pull requests
4. **Documentation**: Improve README and code comments

### Development Setup
```bash
git clone <repository-url>
cd ai_news_generator
pip install -e ".[dev]"  # Install with dev dependencies
```

## 📊 Performance

- **Typical Generation Time**: 2-5 minutes
- **Research Sources**: 5-15 high-quality sources
- **Article Length**: 800-2000 words
- **Accuracy**: High (fact-checked and verified)

## 🔍 Troubleshooting

### Common Issues
1. **API Key Errors**: Ensure both SERPER_API_KEY and COHERE_API_KEY are set
2. **Import Errors**: Check Python path and dependencies
3. **Generation Failures**: Verify internet connection and API quotas

### Debug Mode
```bash
export CREWAI_DEBUG=true
python src/ai_news_flow/main.py "your topic"
```

## 📝 License

This project is part of the AI Engineering Hub educational resources.

## 🌟 What's New in v2.0

- ✅ **CrewAI Flows Integration**: Complete workflow automation
- ✅ **Multi-Phase Processing**: Research → Content → Editing → Finalization  
- ✅ **Real-time Progress Tracking**: Visual workflow indicators
- ✅ **Quality Metrics**: Comprehensive article analysis
- ✅ **Professional UI**: Enhanced Streamlit interface
- ✅ **Modular Architecture**: Separate crews for each phase
- ✅ **Advanced Tools**: Credibility checking and readability analysis

---

## 📬 Stay Updated!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons when you subscribe to our newsletter! 

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

**Built with ❤️ using CrewAI Flows, Streamlit, and Cohere's Command R7B**
