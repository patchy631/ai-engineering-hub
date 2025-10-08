# Parlant Guidelines vs Traditional LLM Prompt: Life Insurance Agent Demo

This project demonstrates the advantages of **Parlant's structured approach** over traditional monolithic LLM prompts for building conversational agents.

## Quick Start

**Terminal 1 - Start the server:**
```bash
uv run parlant_agent_server.py
```

**Terminal 2 - Run the comparison:**
```bash
uv run demo_comparison.py
```

## Demo Queries

The demo tests 5 realistic scenarios:
- Policy replacement with critical warnings
- Coverage calculation with specific parameters  
- Health condition impact assessment
- Mixed topics with boundary maintenance
- Decision making with conflicting rules

## Project Structure

```
parlant-conversational-agent/
├── parlant_agent_server.py      # Parlant agent with tools & guidelines
├── demo_comparison.py            # Main comparison demo runner
├── traditional_llm_prompt.py     # Monolithic prompt approach
├── parlant_client_utils.py      # Parlant API client utilities
├── rich_table_formatter.py      # Beautiful console table rendering
└── pyproject.toml               # Project dependencies (uv)
```

## Setup

```bash
uv sync  # Install dependencies
```

## Requirements

- Python 3.10+ (required for Parlant)
- `uv` package manager
- OpenAI API key in `.env` file

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements. 

