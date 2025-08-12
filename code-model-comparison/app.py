import asyncio
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from model_service import get_parallel_responses, get_all_model_names
from code_ingestion import ingest_github_repo
from code_evaluation_opik import evaluate_code

load_dotenv()

# Set page config
st.set_page_config(page_title="Code Generation Model Comparison", layout="wide")

# Custom CSS for responsive code containers
st.markdown(
    """
<style>
    .stMarkdown {
        width: 100%;
    }
    pre {
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        max-width: 100% !important;
    }
    code {
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        max-width: 100% !important;
    }
    .streamlit-expanderContent {
        width: 100% !important;
    }
    div[data-testid="stCodeBlock"] {
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        max-width: 100% !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "context" not in st.session_state:
    st.session_state.context = None
if "reference_code" not in st.session_state:
    st.session_state.reference_code = None
if "selected_models" not in st.session_state:
    st.session_state.selected_models = {
        "model1": None,
        "model2": None,
    }
if "last_generated_code" not in st.session_state:
    st.session_state.last_generated_code = {"model1": None, "model2": None}
if "evaluation_results" not in st.session_state:
    st.session_state.evaluation_results = {"model1": None, "model2": None}

# Main interface
st.title("Code Generation Model Comparison")
powered_by_html = """
    <div style='display: flex; align-items: center; gap: 10px; margin-top: -10px;'>
        <span style='font-size: 20px; color: #666;'>Powered by</span>
        <img src="https://files.buildwithfern.com/openrouter.docs.buildwithfern.com/docs/2025-07-24T05:04:17.529Z/content/assets/logo-white.svg" width="180"> 
        <span style='font-size: 20px; color: #666;'>and</span>
        <img src="https://files.buildwithfern.com/https://opik.docs.buildwithfern.com/docs/opik/2025-08-01T07:08:31.326Z/img/logo-dark-mode.svg" width="100">
    </div>
"""
st.markdown(powered_by_html, unsafe_allow_html=True)

# Model selection section
st.write("### Select Models to Compare")
col1, col2 = st.columns(2)

# Get all available model names
all_models = get_all_model_names()

# Validate that we have models available
if not all_models:
    st.error("No models are available. Please check your configuration.")
    st.stop()

# Ensure default models are valid
default_model1 = st.session_state.selected_models["model1"]
default_model2 = st.session_state.selected_models["model2"]

# If default models are not in available models, use first two available
if default_model1 not in all_models:
    default_model1 = all_models[0] if all_models else "Claude Sonnet 4"
if default_model2 not in all_models:
    default_model2 = all_models[1] if len(all_models) > 1 else all_models[0]

# Update session state if defaults changed
if (
    default_model1 != st.session_state.selected_models["model1"]
    or default_model2 != st.session_state.selected_models["model2"]
):
    st.session_state.selected_models = {
        "model1": default_model1,
        "model2": default_model2,
    }

with col1:
    model1 = st.selectbox(
        "Select First Model",
        options=all_models,
        index=all_models.index(st.session_state.selected_models["model1"]),
        key="model1_select",
    )

with col2:
    model2 = st.selectbox(
        "Select Second Model",
        options=all_models,
        index=all_models.index(st.session_state.selected_models["model2"]),
        key="model2_select",
    )

# Update session state when models change (only if they actually changed)
if (
    model1 != st.session_state.selected_models["model1"]
    or model2 != st.session_state.selected_models["model2"]
):
    st.session_state.selected_models = {"model1": model1, "model2": model2}
    # Clear previous results when models change
    st.session_state.last_generated_code = {"model1": None, "model2": None}
    st.session_state.evaluation_results = {"model1": None, "model2": None}

with st.sidebar:
    st.title("Configuration")

    github_repo = st.text_input(
        "GitHub Repository URL", placeholder="https://github.com/username/repository"
    )

    if st.button("Ingest Repository"):
        if github_repo:
            with st.spinner("Ingesting repository..."):
                st.session_state.context = ingest_github_repo(github_repo)
            st.success("Repository ingested successfully!")
        else:
            st.error("Please enter a valid repository URL")

    st.session_state.reference_code = st.text_area(
        "Reference Code (Optional)",
        help="Enter reference/ground truth code to compare against",
        height=200,
    )

    # Evaluation section
    st.write("### Evaluation")
    if st.button("Evaluate Generated Code"):
        if (
            st.session_state.last_generated_code["model1"]
            and st.session_state.last_generated_code["model2"]
        ):
            try:
                with st.spinner("Evaluating code..."):
                    st.session_state.evaluation_results["model1"] = evaluate_code(
                        st.session_state.last_generated_code["model1"],
                        (
                            st.session_state.reference_code
                            if st.session_state.reference_code
                            else None
                        ),
                    )
                    st.session_state.evaluation_results["model2"] = evaluate_code(
                        st.session_state.last_generated_code["model2"],
                        (
                            st.session_state.reference_code
                            if st.session_state.reference_code
                            else None
                        ),
                    )
                st.success("Evaluation complete!")
            except Exception as e:
                st.error(f"Error during evaluation: {str(e)}")
                st.error("Please try again or check your evaluation configuration.")
        else:
            st.error("Please generate code from both models first")


async def handle_chat_input(prompt: str):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Validate context structure
    if not st.session_state.context or not isinstance(st.session_state.context, dict):
        st.error("Invalid context structure. Please re-ingest the repository.")
        return

    if "content" not in st.session_state.context:
        st.error(
            "Repository context is missing content. Please re-ingest the repository."
        )
        return

    # Get streaming responses from both models
    with st.chat_message("assistant"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"##### {st.session_state.selected_models['model1']}")
            model1_container = st.empty()
            model1_container = model1_container.code("", language="python")
        with col2:
            st.write(f"##### {st.session_state.selected_models['model2']}")
            model2_container = st.empty()
            model2_container = model2_container.code("", language="python")

        model1_gen, model2_gen = await get_parallel_responses(
            prompt,
            st.session_state.context,
            st.session_state.selected_models["model1"],
            st.session_state.selected_models["model2"],
        )

        async def process_model1_stream(container):
            response_text = ""
            cleaned_text = ""  # Initialize cleaned_text
            try:
                async for chunk in model1_gen:
                    response_text += chunk
                    cleaned_text = (
                        response_text.strip()
                        .removeprefix("```python")
                        .removeprefix("```")
                        .removesuffix("```")
                        .strip()
                    )
                    container.code(cleaned_text, language="python")
            except Exception as e:
                cleaned_text = f"Error processing stream: {str(e)}"
                container.code(cleaned_text, language="python")
            return cleaned_text

        async def process_model2_stream(container):
            response_text = ""
            cleaned_text = ""  # Initialize cleaned_text
            try:
                async for chunk in model2_gen:
                    response_text += chunk
                    cleaned_text = (
                        response_text.strip()
                        .removeprefix("```python")
                        .removeprefix("```")
                        .removesuffix("```")
                        .strip()
                    )
                    container.code(cleaned_text, language="python")
            except Exception as e:
                cleaned_text = f"Error processing stream: {str(e)}"
                container.code(cleaned_text, language="python")
            return cleaned_text

        # Run both streams concurrently
        try:
            final_model1_response, final_model2_response = await asyncio.gather(
                process_model1_stream(model1_container),
                process_model2_stream(model2_container),
            )
        
        except Exception as e:
            st.error(f"Critical error during model response generation: {str(e)}")
            final_model1_response = "Error: Failed to generate response"
            final_model2_response = "Error: Failed to generate response"

        message = {
            "role": "assistant",
            "content": "",
            "model1_response": final_model1_response,
            "model2_response": final_model2_response,
            "model1_name": st.session_state.selected_models["model1"],
            "model2_name": st.session_state.selected_models["model2"],
        }
        st.session_state.chat_history.append(message)
        st.session_state.last_generated_code["model1"] = final_model1_response
        st.session_state.last_generated_code["model2"] = final_model2_response


# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    if message["role"] == "assistant":
        col1, col2 = st.columns(2)
        with col1:
            model1_name = message.get("model1_name", "Model 1")
            st.write(f"##### {model1_name}")
            st.code(message["model1_response"], language="python")
        with col2:
            model2_name = message.get("model2_name", "Model 2")
            st.write(f"##### {model2_name}")
            st.code(message["model2_response"], language="python")

if prompt := st.chat_input("What code would you like to generate?"):
    if not st.session_state.context:
        st.error("Please ingest a GitHub repository first!")
    else:
        try:
            # Validate that selected models are still available
            all_models = get_all_model_names()
            if (
                st.session_state.selected_models["model1"] not in all_models
                or st.session_state.selected_models["model2"] not in all_models
            ):
                st.error(
                    "One or more selected models are no longer available. Please reselect models."
                )
            else:
                asyncio.run(handle_chat_input(prompt))
        except Exception as e:
            st.error(f"An error occurred while generating code: {str(e)}")
            st.error("Please try again or check your configuration.")

# Display evaluation results
if (
    st.session_state.evaluation_results["model1"]
    and st.session_state.evaluation_results["model2"]
):
    try:
        st.write("---")
        st.header("Evaluation results generated with GPT-4o using Opik")

        # Validate evaluation results structure
        def validate_evaluation_result(result, model_name):
            if not result or not isinstance(result, dict):
                return False
            if "detailed_metrics" not in result or "overall_score" not in result:
                return False
            required_metrics = ["correctness", "readability", "best_practices"]
            for metric in required_metrics:
                if metric not in result["detailed_metrics"]:
                    return False
                if "score" not in result["detailed_metrics"][metric]:
                    return False
            return True

        model1_valid = validate_evaluation_result(
            st.session_state.evaluation_results["model1"], "model1"
        )
        model2_valid = validate_evaluation_result(
            st.session_state.evaluation_results["model2"], "model2"
        )

        if not model1_valid:
            st.error("Invalid evaluation result structure for model 1")
        elif not model2_valid:
            st.error("Invalid evaluation result structure for model 2")
        else:
            # Only proceed with plotting if both models are valid
            plot_data = pd.DataFrame(
                {
                    "Metric": [
                        "Correctness",
                        "Readability",
                        "Best Practices",
                        "Overall Score",
                    ],
                    st.session_state.selected_models["model1"]: [
                        st.session_state.evaluation_results["model1"][
                            "detailed_metrics"
                        ]["correctness"]["score"],
                        st.session_state.evaluation_results["model1"][
                            "detailed_metrics"
                        ]["readability"]["score"],
                        st.session_state.evaluation_results["model1"][
                            "detailed_metrics"
                        ]["best_practices"]["score"],
                        st.session_state.evaluation_results["model1"]["overall_score"],
                    ],
                    st.session_state.selected_models["model2"]: [
                        st.session_state.evaluation_results["model2"][
                            "detailed_metrics"
                        ]["correctness"]["score"],
                        st.session_state.evaluation_results["model2"][
                            "detailed_metrics"
                        ]["readability"]["score"],
                        st.session_state.evaluation_results["model2"][
                            "detailed_metrics"
                        ]["best_practices"]["score"],
                        st.session_state.evaluation_results["model2"]["overall_score"],
                    ],
                }
            )

            fig = px.bar(
                plot_data.melt("Metric", var_name="Model", value_name="Score"),
                x="Metric",
                y="Score",
                color="Model",
                barmode="group",
                title="Model Performance Comparison",
                template="plotly_dark",
                color_discrete_sequence=["#00CED1", "#FF69B4"],
            )

            fig.update_layout(
                xaxis_title="Evaluation Metrics",
                yaxis_title="Score",
                legend_title="Models",
                plot_bgcolor="rgba(32, 32, 32, 1)",
                paper_bgcolor="rgba(32, 32, 32, 1)",
                bargap=0.2,
                bargroupgap=0.1,
                font=dict(color="#E0E0E0"),
                title_font=dict(color="#E0E0E0"),
                showlegend=True,
                legend=dict(
                    bgcolor="rgba(32, 32, 32, 0.8)",
                    bordercolor="rgba(255, 255, 255, 0.3)",
                    borderwidth=1,
                ),
            )

            fig.update_xaxes(
                gridcolor="rgba(128, 128, 128, 0.2)",
                zerolinecolor="rgba(128, 128, 128, 0.2)",
            )
            fig.update_yaxes(
                gridcolor="rgba(128, 128, 128, 0.2)",
                zerolinecolor="rgba(128, 128, 128, 0.2)",
            )

            st.plotly_chart(fig, use_container_width=True)

            st.write(
                f"### {st.session_state.selected_models['model1']} detailed metrics"
            )

            model1_data = []
            for metric in ["correctness", "readability", "best_practices"]:
                row = {
                    "Metric": metric.title(),
                    "Score": f"{st.session_state.evaluation_results['model1']['detailed_metrics'][metric]['score']:.2f}",
                    "Reasoning": st.session_state.evaluation_results["model1"][
                        "detailed_metrics"
                    ][metric]["reason"],
                }
                model1_data.append(row)

            model1_data.append(
                {
                    "Metric": "Overall Score",
                    "Score": f"{st.session_state.evaluation_results['model1']['overall_score']:.2f}",
                    "Reasoning": "Final weighted average",
                }
            )

            # Display Model 1 table
            model1_df = pd.DataFrame(model1_data)
            st.dataframe(
                model1_df,
                column_config={
                    "Metric": st.column_config.TextColumn("Metric", width="small"),
                    "Score": st.column_config.TextColumn("Score", width="small"),
                    "Reasoning": st.column_config.TextColumn(
                        "Reasoning", width="large"
                    ),
                },
                hide_index=True,
                use_container_width=True,
            )

            st.write(
                f"### {st.session_state.selected_models['model2']} detailed metrics"
            )

            model2_data = []
            for metric in ["correctness", "readability", "best_practices"]:
                row = {
                    "Metric": metric.title(),
                    "Score": f"{st.session_state.evaluation_results['model2']['detailed_metrics'][metric]['score']:.2f}",
                    "Reasoning": st.session_state.evaluation_results["model2"][
                        "detailed_metrics"
                    ][metric]["reason"],
                }
                model2_data.append(row)

            model2_data.append(
                {
                    "Metric": "Overall Score",
                    "Score": f"{st.session_state.evaluation_results['model2']['overall_score']:.2f}",
                    "Reasoning": "Final weighted average",
                }
            )

            # Display Model 2 table
            model2_df = pd.DataFrame(model2_data)
            st.dataframe(
                model2_df,
                column_config={
                    "Metric": st.column_config.TextColumn("Metric", width="small"),
                    "Score": st.column_config.TextColumn("Score", width="small"),
                    "Reasoning": st.column_config.TextColumn(
                        "Reasoning", width="large"
                    ),
                },
                hide_index=True,
                use_container_width=True,
            )
    except Exception as e:
        st.error(f"Error displaying evaluation results: {str(e)}")
        st.error("Please try running the evaluation again.")
