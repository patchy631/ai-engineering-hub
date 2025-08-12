import asyncio
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from model_service import get_parallel_responses
from code_ingestion import ingest_github_repo
from code_evaluation import evaluate_code

load_dotenv()

# Set page config
st.set_page_config(
    page_title="Code Generation Model Comparison",
    layout="wide"
)

# Custom CSS for responsive code containers
st.markdown("""
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
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'context' not in st.session_state:
    st.session_state.context = None
if 'reference_code' not in st.session_state:
    st.session_state.reference_code = None
if 'last_generated_code' not in st.session_state:
    st.session_state.last_generated_code = {"claude": None, "qwen3-coder": None}
if 'evaluation_results' not in st.session_state:
    st.session_state.evaluation_results = {"claude": None, "qwen3-coder": None}

with st.sidebar:
    st.title("Configuration")
    
    github_repo = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/username/repository"
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
        height=200
    )

    # Evaluation section
    st.write("### Evaluation")
    if st.button("Evaluate Generated Code"):
        if st.session_state.last_generated_code["claude"] and st.session_state.last_generated_code["qwen3-coder"]:
            with st.spinner("Evaluating code..."):
                st.session_state.evaluation_results["claude"] = evaluate_code(
                    st.session_state.last_generated_code["claude"],
                    st.session_state.reference_code if st.session_state.reference_code else None
                )
                st.session_state.evaluation_results["qwen3-coder"] = evaluate_code(
                    st.session_state.last_generated_code["qwen3-coder"],
                    st.session_state.reference_code if st.session_state.reference_code else None
                )
            st.success("Evaluation complete!")
        else:
            st.error("Please generate code from both models first")

async def handle_chat_input(prompt: str):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get streaming responses from both models
    with st.chat_message("assistant"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("##### Claude Sonnet 4")
            claude_container = st.empty()
            claude_container = claude_container.code("", language="python")
        with col2:
            st.write("##### Qwen3-Coder")
            qwen3_coder_container = st.empty()
            qwen3_coder_container = qwen3_coder_container.code("", language="python")
        
        claude_gen, qwen3_coder_gen = await get_parallel_responses(prompt, st.session_state.context)
        
        async def process_claude_stream(container):
            response_text = ""
            async for chunk in claude_gen:
                response_text += chunk
                cleaned_text = response_text.strip().removeprefix("```python").removeprefix("```").removesuffix("```").strip()
                container.code(cleaned_text, language="python")
            return cleaned_text

        async def process_qwen3_coder_stream(container):
            response_text = ""
            async for chunk in qwen3_coder_gen:
                response_text += chunk
                cleaned_text = response_text.strip().removeprefix("```python").removeprefix("```").removesuffix("```").strip()
                container.code(cleaned_text, language="python")
            return cleaned_text

        # Run both streams concurrently
        final_claude_response, final_qwen3_coder_response = await asyncio.gather(
            process_claude_stream(claude_container),
            process_qwen3_coder_stream(qwen3_coder_container)
        )
        
        message = {
            "role": "assistant",
            "content": "",
            "claude_response": final_claude_response,
            "qwen3-coder_response": final_qwen3_coder_response
        }
        st.session_state.chat_history.append(message)
        st.session_state.last_generated_code["claude"] = final_claude_response
        st.session_state.last_generated_code["qwen3-coder"] = final_qwen3_coder_response

# Main interface
st.title("Claude Sonnet 4 vs Qwen3-Coder using DeepEval")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    if message["role"] == "assistant":
        col1, col2 = st.columns(2)
        with col1:
            st.write("##### Claude Sonnet 4")
            st.code(message["claude_response"], language="python")
        with col2:
            st.write("##### Qwen3-Coder")
            st.code(message["qwen3-coder_response"], language="python")

if prompt := st.chat_input("What code would you like to generate?"):
    if not st.session_state.context:
        st.error("Please ingest a GitHub repository first!")
    else:
        asyncio.run(handle_chat_input(prompt))

# Display evaluation results
if st.session_state.evaluation_results["claude"] and st.session_state.evaluation_results["qwen3-coder"]:
    st.write("---")
    st.header("Evaluation results generated with GPT-4o using DeepEval")

    plot_data = pd.DataFrame({
        'Metric': ["Correctness", "Readability", "Best Practices", "Overall Score"],
        'Claude': [
            st.session_state.evaluation_results['claude']['detailed_metrics']['correctness']['score'],
            st.session_state.evaluation_results['claude']['detailed_metrics']['readability']['score'],
            st.session_state.evaluation_results['claude']['detailed_metrics']['best_practices']['score'],
            st.session_state.evaluation_results['claude']['overall_score']
        ],
        'Qwen3-Coder': [
            st.session_state.evaluation_results['qwen3-coder']['detailed_metrics']['correctness']['score'],
            st.session_state.evaluation_results['qwen3-coder']['detailed_metrics']['readability']['score'],
            st.session_state.evaluation_results['qwen3-coder']['detailed_metrics']['best_practices']['score'],
            st.session_state.evaluation_results['qwen3-coder']['overall_score']
        ]
    })
    
    fig = px.bar(
        plot_data.melt('Metric', var_name='Model', value_name='Score'),
        x='Metric',
        y='Score',
        color='Model',
        barmode='group',  
        title='Model Performance Comparison',
        template='plotly_dark',  
        color_discrete_sequence=['#00CED1', '#FF69B4'] 
    )
    
    fig.update_layout(
        xaxis_title="Evaluation Metrics",
        yaxis_title="Score",
        legend_title="Models",
        plot_bgcolor='rgba(32, 32, 32, 1)',  
        paper_bgcolor='rgba(32, 32, 32, 1)',  
        bargap=0.2,  
        bargroupgap=0.1,  
        font=dict(color='#E0E0E0'),  
        title_font=dict(color='#E0E0E0'),  
        showlegend=True,
        legend=dict(
            bgcolor='rgba(32, 32, 32, 0.8)',
            bordercolor='rgba(255, 255, 255, 0.3)',
            borderwidth=1
        )
    )
    
    fig.update_xaxes(
        gridcolor='rgba(128, 128, 128, 0.2)',
        zerolinecolor='rgba(128, 128, 128, 0.2)'
    )
    fig.update_yaxes(
        gridcolor='rgba(128, 128, 128, 0.2)',
        zerolinecolor='rgba(128, 128, 128, 0.2)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("### Claude Sonnet 4 detailed metrics")
    
    claude_data = []
    for metric in ["correctness", "readability", "best_practices"]:
        row = {
            "Metric": metric.title(),
            "Score": f"{st.session_state.evaluation_results['claude']['detailed_metrics'][metric]['score']:.2f}",
            "Reasoning": st.session_state.evaluation_results['claude']['detailed_metrics'][metric]['reason']
        }
        claude_data.append(row)
    
    claude_data.append({
        "Metric": "Overall Score",
        "Score": f"{st.session_state.evaluation_results['claude']['overall_score']:.2f}",
        "Reasoning": "Final weighted average"
    })
    
    # Display Claude table
    claude_df = pd.DataFrame(claude_data)
    st.dataframe(
        claude_df,
        column_config={
            "Metric": st.column_config.TextColumn("Metric", width="small"),
            "Score": st.column_config.TextColumn("Score", width="small"),
            "Reasoning": st.column_config.TextColumn("Reasoning", width="large")
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.write("### Qwen3-Coder detailed metrics")
    
    qwen3_coder_data = []
    for metric in ["correctness", "readability", "best_practices"]:
        row = {
            "Metric": metric.title(),
            "Score": f"{st.session_state.evaluation_results['qwen3-coder']['detailed_metrics'][metric]['score']:.2f}",
            "Reasoning": st.session_state.evaluation_results['qwen3-coder']['detailed_metrics'][metric]['reason']
        }
        qwen3_coder_data.append(row)
    
    qwen3_coder_data.append({
        "Metric": "Overall Score",
        "Score": f"{st.session_state.evaluation_results['qwen3-coder']['overall_score']:.2f}",
        "Reasoning": "Final weighted average"
    })
    
    # Display Qwen3-Coder table
    qwen3_coder_df = pd.DataFrame(qwen3_coder_data)
    st.dataframe(
        qwen3_coder_df,
        column_config={
            "Metric": st.column_config.TextColumn("Metric", width="small"),
            "Score": st.column_config.TextColumn("Score", width="small"),
            "Reasoning": st.column_config.TextColumn("Reasoning", width="large")
        },
        hide_index=True,
        use_container_width=True
    ) 