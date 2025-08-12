# Claude Sonnet 4 vs OpenAI o4-mini on code generation using DeepEval

This application compares the code generation capabilities of Claude Sonnet 4 and OpenAI o4-mini using DeepEval metrics. The app allows users to ingest code from a GitHub repository as context and generate new code based on that context. Both models run parallely side by side giving a fair comparison of their capabilities. Finally DeepEval evaluates both models on custom code metrics and 
provide a detailed performance comparison with neat and clean visuals.

We use:
- LiteLLM for orchestration
- DeepEval for evaluation
- Gitingest for ingesting code
- Streamlit for the UI

---
## Setup and Installation

Ensure you have Python 3.12 or later installed on your system.

Install dependencies:
```bash
uv sync
```

Copy `.env.example` to `.env` and configure the following environment variables:
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

Run the Streamlit app:
```bash
streamlit run app.py
```

## Usage

1. Enter a GitHub repository URL in the sidebar
2. Click "Ingest Repository" to load the repository context
3. Enter your code generation prompt in the chat
4. View the generated code from both models side by side
5. Click on "Evaluate Code" to evaluate code using DeepEval
6. View the evaluation metrics comparing both models' performance

## Evaluation Metrics

The app evaluates generated code using three comprehensive metrics powered by DeepEval:

- **Code Correctness**: Evaluates the functional correctness of the generated code

- **Code Readability**: Measures how easy the code is to understand and maintain

- **Best Practices**: Assesses adherence to coding standards and coding best practices

Each metric is scored on a scale of 0-10, with the following general interpretation:
- 0-2: Major issues or non-functional code
- 3-5: Basic implementation with significant gaps
- 6-8: Good implementation with minor issues
- 9-10: Excellent implementation meeting all criteria

The overall score is calculated as an average of these three metrics.

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements. 