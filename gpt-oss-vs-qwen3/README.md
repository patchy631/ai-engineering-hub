# Reasoning Model Comparison using Opik

This application compares the reasoning capabilities of different frontier models using Opik's G-Eval metrics. The app allows users to ask reasoning questions to two models simultaneously and evaluate their responses across multiple dimensions. Both models run in parallel side-by-side, giving a fair comparison of their reasoning abilities. The system evaluates responses using custom reasoning metrics and provides detailed performance comparisons with clean visualizations.

We use:

- LiteLLM for model orchestration
- Opik for evaluation and observability with G-Eval
- Streamlit for the UI
- OpenRouter for accessing multiple AI models

---

## Setup and Installation

Ensure you have Python 3.12 or later installed on your system.

Install dependencies:

```bash
uv sync
```

Copy `.env.example` to `.env` and configure the following environment variables:

```
OPENAI_API_KEY=your_openai_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Look for the `.opik.config` file in the root directory and set your respective credentials for Opik.

Run the Streamlit app:

```bash
streamlit run app.py
```

## Usage

1. Select the models you want to compare from the dropdown menu
2. Enter your reasoning question in the chat interface
3. View the generated responses from both models side by side
4. Optionally add a reference answer in the sidebar for comparison
5. Click on "Evaluate Reasoning Responses" to evaluate responses using Opik
6. View the evaluation metrics comparing both models' reasoning performance

## Evaluation Metrics

The app evaluates reasoning responses using four comprehensive metrics powered by Opik's G-Eval:

### 1. **Logical Reasoning** 
Assesses the coherence and validity of logical steps and conclusions. Evaluates:
- Logical consistency throughout the response
- Identification of logical fallacies or contradictions  
- Validity of conclusions drawn from premises
- Overall reasoning structure and flow

### 2. **Factual Accuracy**
Evaluates the correctness of factual claims and information. Assesses:
- Accuracy of factual claims made in the response
- Detection of misleading or incorrect information
- Whether claims are properly supported or justified
- Reliability of information sources if mentioned

### 3. **Coherence**
Measures how well-structured and clear the response is. Evaluates:
- Overall organization and structure of the response
- Clear transitions between ideas and concepts
- Clarity and readability of the writing
- Whether the response follows a logical sequence

### 4. **Depth of Analysis**
Assesses the thoroughness and insight of the reasoning. Evaluates:
- Depth and thoroughness of the analysis provided
- Evidence of critical thinking and insight
- Whether multiple perspectives are considered where appropriate
- If the response goes beyond surface-level observations

Each metric is scored on a scale of 0-10, with the following general interpretation:

- **0-2**: Major issues (logical fallacies, factual errors, poor structure, superficial analysis)
- **3-5**: Basic implementation with significant gaps
- **6-8**: Good performance with minor issues
- **9-10**: Excellent performance meeting all criteria

The **overall score** is calculated as an average of these four metrics, with a passing threshold of 7.0 (70%).

## Key Features

- **Side-by-side comparison**: Compare responses from two different reasoning models simultaneously
- **Real-time streaming**: See responses being generated in real-time
- **Comprehensive evaluation**: Four distinct reasoning metrics for thorough assessment
- **Reference comparison**: Optional reference answer comparison for better evaluation context
- **Visual analytics**: Clean charts and detailed breakdowns of evaluation results
- **Model flexibility**: Easy switching between different AI models via dropdown selection

---

## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.