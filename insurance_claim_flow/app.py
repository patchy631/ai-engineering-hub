import os
import json
import asyncio

import loguru
import streamlit as st

from llama_index.llms.openai import OpenAI
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from flow import AutoInsuranceWorkflow


st.set_page_config(page_title="Auto Insurance Claim", layout="wide")


async def run_workflow(workflow, claim_json_path):
    result = await workflow.run(claim_json_path=claim_json_path)
    return result


def main():
    st.title("📋 Auto Insurance Claim Assistant")
    st.markdown(
        """
        <div style="padding: 15px; border-radius: 8px; background-color: #e6f3ff; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <span style="font-size: 1.2em; color: #333;">
                📤 Upload • ⚙️ Process • ✅ Decide — All in One Place!
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar settings
    with st.sidebar.expander("⚙️ Settings", expanded=True):
        st.markdown("### 🔑 API Credentials")
        openai_api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="Enter your OpenAI key",
            help="Required for LLM processing",
        )
        llama_cloud_api_key = st.text_input(
            "LlamaCloud API Key",
            type="password",
            placeholder="Enter your LlamaCloud key",
            help="Required for policy and declarations retrieval",
        )

        st.markdown("### 📚 Index Configuration")
        claim_index_name = st.text_input(
            "Policy Documents Index",
            value="auto-insurance-claims",
            help="Index containing general policy documents",
        )
        declarations_index_name = st.text_input(
            "Declarations Index",
            value="auto-insurance-declarations",
            help="Index containing per-user declarations",
        )

        st.markdown("### 🤖 Model Selection")
        model_option = st.selectbox(
            "Select LLM Model",
            ["gpt-4o", "gpt-4"],
            help="Choose the language model for analysis",
        )

        st.markdown("### 🛠️ Actions")
        if st.button("Reset App 🗑️", help="Clear current claim data"):
            st.session_state.claim_data = None
            st.rerun()

        # Set environment variables if keys are provided
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        if llama_cloud_api_key:
            os.environ["LLAMA_CLOUD_API_KEY"] = llama_cloud_api_key

    # Initialize session state
    if "claim_data" not in st.session_state:
        st.session_state.claim_data = None

    # Main workflow
    st.header("📥 Process Your Claim")
    with st.container():
        st.markdown(
            """
            <div style="padding: 15px; border-radius: 8px; background-color: #f9f9f9; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <span style="font-size: 1em; color: #555;">
                    Upload your claim JSON here to begin!
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "📄 Claim JSON",
            type=["json"],
            help="Upload a .json file with claim details",
            accept_multiple_files=False,
        )
        if uploaded_file:
            try:
                st.session_state.claim_data = json.load(uploaded_file)
                st.success("✅ Claim file uploaded successfully!")
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON file. Please upload a valid claim file.")

    if st.session_state.claim_data:
        claim_data = st.session_state.claim_data
        st.subheader("Claim Information 📋")
        with st.container():
            st.markdown(
                f"""
                <div style="padding: 15px; border-radius: 10px; background-color: #f9f9f9; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <p><strong>Claim Number 🔍:</strong> {claim_data["claim_number"]}</p>
                    <p><strong>Policy Number 📜:</strong> {claim_data["policy_number"]}</p>
                    <p><strong>Claimant 👤:</strong> {claim_data["claimant_name"]}</p>
                    <p><strong>Date of Loss 📅:</strong> {claim_data["date_of_loss"]}</p>
                    <p><strong>Vehicle 🚗:</strong> {claim_data.get("vehicle_details", "N/A")}</p>
                    <p><strong>Estimated Repair Cost 💰:</strong> ${claim_data["estimated_repair_cost"]:.2f}</p>
                    <p><strong>Loss Description 📝:</strong> {claim_data["loss_description"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.button(
            "⚙️ Process Claim", type="primary", help="Start analyzing the uploaded claim"
        ):
            if not openai_api_key or not llama_cloud_api_key:
                st.error("❌ Please provide API keys in the sidebar to proceed.")
            else:
                with st.status(
                    "🔄 Processing Your Claim...", expanded=True, state="running"
                ) as status:
                    status.write("📝 Parsing claim data...")
                    with open("temp_claim.json", "w") as f:
                        json.dump(claim_data, f)

                    status.write("🛠️ Setting up workflow...")
                    llm = OpenAI(model=model_option)
                    try:
                        index = LlamaCloudIndex(
                            name=claim_index_name,
                            project_name="Default",
                            api_key=llama_cloud_api_key,
                        )
                        policy_retriever = index.as_retriever(rerank_top_n=3)
                    except Exception as e:
                        status.error(f"❌ Failed to connect to policy index: {str(e)}")
                        st.stop()
                    try:
                        declarations_index = LlamaCloudIndex(
                            name=declarations_index_name,
                            project_name="Default",
                            api_key=llama_cloud_api_key,
                        )
                    except Exception as e:
                        status.error(
                            f"❌ Failed to connect to declarations index: {str(e)}"
                        )
                        st.stop()
                    workflow = AutoInsuranceWorkflow(
                        policy_retriever=policy_retriever,
                        declarations_index=declarations_index,
                        llm=llm,
                        verbose=True,
                        timeout=None,
                    )

                    status.write("🔍 Analyzing claim details...")
                    with st.spinner("Running analysis..."):
                        try:
                            result = asyncio.run(
                                run_workflow(workflow, "temp_claim.json")
                            )
                        except Exception as e:
                            status.error(f"❌ Processing failed: {str(e)}")
                            st.stop()

                    status.write("✅ Claim processed successfully!")
                    status.update(
                        label="🎉 Processing Complete!",
                        state="complete",
                        expanded=False,
                    )
                    os.remove("temp_claim.json")

                # Display retrieved information
                st.subheader("Retrieved Information 📚")
                with st.expander(f"Claims Index ({claim_index_name})"):
                    claim_text = result.get(
                        "claim_text", "No claim policy text retrieved."
                    )
                    st.markdown(f"```\n{claim_text}\n```")
                with st.expander(f"Declarations Index ({declarations_index_name})"):
                    declarations_text = result.get(
                        "declarations_text", "No declarations retrieved."
                    )
                    st.markdown(f"```\n{declarations_text}\n```")

                # Display decision
                st.subheader("Claim Decision")
                decision = result["decision"]
                status_color = "green" if decision.covered else "red"
                st.markdown(
                    f"""
                    <div style="padding: 20px; border-radius: 10px; background-color: #f9f9f9; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h3 style="color: {status_color}; margin-bottom: 15px;">
                            {"✅ Approved" if decision.covered else "❌ Denied"} 
                            <span style="font-size: 0.8em; color: #666;">(Claim #{decision.claim_number})</span>
                        </h3>
                        <p style="margin: 5px 0;">💵 <strong>Deductible:</strong> ${decision.deductible:.2f}</p>
                        <p style="margin: 5px 0;">💰 <strong>Recommended Payout:</strong> ${decision.recommended_payout:.2f}</p>
                        <p style="margin: 5px 0; line-height: 1.5;">📝 <strong>Notes:</strong> {decision.notes}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Footer
    st.markdown("---")
    st.markdown(
        "Built with LlamaIndex & Streamlit | [Code on GitHub](https://github.com/your-repo)"
    )


if __name__ == "__main__":
    main()
