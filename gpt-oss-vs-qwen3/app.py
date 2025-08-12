import asyncio
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from model_service import get_parallel_responses, get_all_model_names
from code_evaluation_opik import evaluate_reasoning

load_dotenv()

# Set page config
st.set_page_config(page_title="Reasoning Model Comparison", layout="wide")

# Custom CSS for responsive containers
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
</style>
""",
    unsafe_allow_html=True,
)



# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "reference_answer" not in st.session_state:
    st.session_state.reference_answer = None
if "selected_models" not in st.session_state:
    st.session_state.selected_models = {
        "model1": None,
        "model2": None,
    }
if "last_generated_response" not in st.session_state:
    st.session_state.last_generated_response = {"model1": None, "model2": None}
if "last_thinking_content" not in st.session_state:
    st.session_state.last_thinking_content = {"model1": None, "model2": None}
if "evaluation_results" not in st.session_state:
    st.session_state.evaluation_results = {"model1": None, "model2": None}

# Main interface
st.title("Reasoning Model Comparison")
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

# If default models are not in available models, use first available
if default_model1 not in all_models:
    default_model1 = all_models[0] if all_models else "GPT-oss"
if default_model2 not in all_models:
    default_model2 = all_models[0] if all_models else "GPT-oss"

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
    st.session_state.last_generated_response = {"model1": None, "model2": None}
    st.session_state.last_thinking_content = {"model1": None, "model2": None}
    st.session_state.evaluation_results = {"model1": None, "model2": None}

with st.sidebar:
    st.title("Configuration")
    
    st.session_state.reference_answer = st.text_area(
        "Reference Answer (Optional)",
        help="Enter reference/ground truth answer to compare against",
        height=200,
    )

    # Evaluation section
    st.write("### Evaluation")
    if st.button("Evaluate Reasoning Responses"):
        if (
            st.session_state.last_generated_response["model1"]
            and st.session_state.last_generated_response["model2"]
        ):
            try:
                with st.spinner("Evaluating reasoning responses..."):
                    st.session_state.evaluation_results["model1"] = evaluate_reasoning(
                        st.session_state.last_generated_response["model1"],
                        (
                            st.session_state.reference_answer
                            if st.session_state.reference_answer
                            else None
                        ),
                    )
                    st.session_state.evaluation_results["model2"] = evaluate_reasoning(
                        st.session_state.last_generated_response["model2"],
                        (
                            st.session_state.reference_answer
                            if st.session_state.reference_answer
                            else None
                        ),
                    )
                st.success("Evaluation complete!")
            except Exception as e:
                st.error(f"Error during evaluation: {str(e)}")
                st.error("Please try again or check your evaluation configuration.")
        else:
            st.error("Please generate responses from both models first")


async def handle_chat_input(prompt: str):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get streaming responses from both models
    with st.chat_message("assistant"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"##### {st.session_state.selected_models['model1']}")
            model1_container = st.empty()
        with col2:
            st.write(f"##### {st.session_state.selected_models['model2']}")
            model2_container = st.empty()

        response1_gen, response2_gen = await get_parallel_responses(
            prompt,
            st.session_state.selected_models["model1"],
            st.session_state.selected_models["model2"]
        )

        async def process_response1(container):
            result = await response1_gen
            
            content = result.get("content", "")
            reasoning = result.get("reasoning", "")
            
            # Debug prints to see what we're getting
            print(f"DEBUG - Model 1 Content: {repr(content)}")
            print(f"DEBUG - Model 1 Reasoning: {repr(reasoning)}")
            print(f"DEBUG - Has reasoning: {bool(reasoning and reasoning.strip())}")
            
            # Display in container
            container.empty()  # Clear first
            with container.container():
                # Reasoning dropdown first (above final answer)
                if reasoning and reasoning.strip():
                    with st.expander("🧠 Thinking process", expanded=False):
                        st.markdown(reasoning)
                    st.markdown("**Final Answer:**")
                    st.session_state.last_thinking_content["model1"] = reasoning
                
                # Final answer
                st.markdown(content)
            
            return content
        
        async def process_response2(container):
            result = await response2_gen
            
            content = result.get("content", "")
            reasoning = result.get("reasoning", "")
            
            # Debug prints to see what we're getting
            print(f"DEBUG - Model 2 Content: {repr(content)}")
            print(f"DEBUG - Model 2 Reasoning: {repr(reasoning)}")
            print(f"DEBUG - Has reasoning: {bool(reasoning and reasoning.strip())}")
            
            # Display in container
            container.empty()  # Clear first
            with container.container():
                # Reasoning dropdown first (above final answer)
                if reasoning and reasoning.strip():
                    with st.expander("🧠 Thinking process", expanded=False):
                        st.markdown(reasoning)
                    st.markdown("**Final Answer:**")
                    st.session_state.last_thinking_content["model2"] = reasoning
                
                # Final answer
                st.markdown(content)
            
            return content

        # Run both responses concurrently
        try:
            final_response1, final_response2 = await asyncio.gather(
                process_response1(model1_container),
                process_response2(model2_container),
            )
        
        except Exception as e:
            st.error(f"Critical error during response generation: {str(e)}")
            final_response1 = "Error: Failed to generate response"
            final_response2 = "Error: Failed to generate response"

        message = {
            "role": "assistant",
            "content": "",
            "model1_response": final_response1,
            "model2_response": final_response2,
            "model1_thinking": st.session_state.last_thinking_content.get("model1", ""),
            "model2_thinking": st.session_state.last_thinking_content.get("model2", ""),
            "model1_name": st.session_state.selected_models["model1"],
            "model2_name": st.session_state.selected_models["model2"],
        }
        st.session_state.chat_history.append(message)
        st.session_state.last_generated_response["model1"] = final_response1
        st.session_state.last_generated_response["model2"] = final_response2


# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    if message["role"] == "assistant":
        col1, col2 = st.columns(2)
        with col1:
            model1_name = message.get("model1_name", "Model 1")
            st.write(f"##### {model1_name}")
            model1_thinking = message.get("model1_thinking", "")
            # Display thinking content in expander within this column
            if model1_thinking and model1_thinking.strip():
                with st.expander(f"🧠 Thinking process", expanded=False):
                    st.markdown(model1_thinking)
                st.markdown("**Final Answer:**")
            st.markdown(message["model1_response"])
        with col2:
            model2_name = message.get("model2_name", "Model 2")
            st.write(f"##### {model2_name}")
            model2_thinking = message.get("model2_thinking", "")
            # Display thinking content in expander within this column
            if model2_thinking and model2_thinking.strip():
                with st.expander(f"🧠 Thinking process", expanded=False):
                    st.markdown(model2_thinking)
                st.markdown("**Final Answer:**")
            st.markdown(message["model2_response"])

if prompt := st.chat_input("What reasoning question would you like to ask?"):
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
        st.error(f"An error occurred while generating responses: {str(e)}")
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
            required_metrics = ["logical_reasoning", "factual_accuracy", "coherence", "depth_of_analysis"]
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
                        "Logical Reasoning",
                        "Factual Accuracy",
                        "Coherence",
                        "Depth of Analysis",
                        "Overall Score",
                    ],
                    st.session_state.selected_models["model1"]: [
                        st.session_state.evaluation_results["model1"][
                            "detailed_metrics"
                        ]["logical_reasoning"]["score"],
                        st.session_state.evaluation_results["model1"][
                            "detailed_metrics"
                        ]["factual_accuracy"]["score"],
                        st.session_state.evaluation_results["model1"][
                            "detailed_metrics"
                        ]["coherence"]["score"],
                        st.session_state.evaluation_results["model1"][
                            "detailed_metrics"
                        ]["depth_of_analysis"]["score"],
                        st.session_state.evaluation_results["model1"]["overall_score"],
                    ],
                    st.session_state.selected_models["model2"]: [
                        st.session_state.evaluation_results["model2"][
                            "detailed_metrics"
                        ]["logical_reasoning"]["score"],
                        st.session_state.evaluation_results["model2"][
                            "detailed_metrics"
                        ]["factual_accuracy"]["score"],
                        st.session_state.evaluation_results["model2"][
                            "detailed_metrics"
                        ]["coherence"]["score"],
                        st.session_state.evaluation_results["model2"][
                            "detailed_metrics"
                        ]["depth_of_analysis"]["score"],
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
                title="Reasoning Model Performance Comparison",
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
            for metric in ["logical_reasoning", "factual_accuracy", "coherence", "depth_of_analysis"]:
                row = {
                    "Metric": metric.replace("_", " ").title(),
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
            for metric in ["logical_reasoning", "factual_accuracy", "coherence", "depth_of_analysis"]:
                row = {
                    "Metric": metric.replace("_", " ").title(),
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