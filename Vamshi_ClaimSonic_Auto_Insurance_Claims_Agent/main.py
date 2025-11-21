import os
import json
import asyncio
from dotenv import load_dotenv
from typing import List, Optional

from llama_index.core.llms import LLM
from pydantic import BaseModel, Field
from llama_index.llms.openai import OpenAI
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.prompts import ChatPromptTemplate
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_index.core.vector_stores.types import ( MetadataInfo, MetadataFilters)

from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Context,
    Workflow,
    step
)

# ---------- Import Streamlit and ace ----------
import streamlit as st
from streamlit_ace import st_ace

st.set_page_config(
    page_title="ClaimSonic: Auto Claim Wizard 🚗",
    page_icon="🚗",
    layout="centered",
    initial_sidebar_state="expanded"  # Always open
)

# ---------- Loading Environment variables ----------

load_dotenv() 


# ---------- Define our Data Models ----------

class ClaimInfo(BaseModel):
    """
        Input Claim Information schema by the Claim Adjuster.
        Extracted Insurance claim information.
    
    """

    claim_number: str
    policy_number: str
    claimant_name: str
    date_of_loss: str
    loss_description: str
    estimated_repair_cost: float
    vehicle_details: Optional[str] = None


class PolicyQueries(BaseModel):
    """
        Policy Conditions and Policy Queries.
        defining the schema to generate guideline (in this case, 
        coverage guideline) queries and for storing recommendations.
    
    """
    
    queries: List[str] = Field(
        default_factory=list,
        description="A list of query strings to retrieve relevant policy sections."
    )

class PolicyRecommendation(BaseModel):
    """
        Guideline/Policy recommendation schema.
        Policy recommendation regarding a given claim.
    
    """
    
    policy_section: str = Field(..., description="The policy section or clause that applies.")
    recommendation_summary: str = Field(..., description="A concise summary of coverage determination.")
    deductible: Optional[float] = Field(None, description="The applicable deductible amount.")
    settlement_amount: Optional[float] = Field(None, description="Recommended settlement payout.")


class ClaimDecision(BaseModel):
    """
        Final Claim Decision schema.
        Claim decision information for a given claim.

    """
    claim_number: str
    covered: bool
    deductible: float
    recommended_payout: float
    notes: Optional[str] = None


# ---------- Utility: Parse Claim JSON Text ----------

def parse_claim_from_text(json_text: str) -> ClaimInfo:
    data = json.loads(json_text)
    return ClaimInfo(**data)

# ---------- Utility: Reads the prompts from the markdown files ----------

def load_prompt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
    
GENERATE_POLICY_QUERIES_PROMPT = load_prompt("./prompts/Policy_Queries.md")
POLICY_RECOMMENDATION_PROMPT = load_prompt("./prompts/Policy_Recommendation.md")

# ---------- Connect to Existing Indexes ----------
# Index for general auto insurance policies
index = LlamaCloudIndex(
    name="auto_insurance_policies_0",
    project_name="DailyDoseofDS",
    organization_id= os.environ["LLAMA_ORG_ID"], 
    api_key= os.environ["LLAMA_CLOUD_API_KEY"] # organization_id and api_key can be set here if required.
)
retriever = index.as_retriever(rerank_top_n=3)

# Index for declarations pages
declarations_index = LlamaCloudIndex(
    name="auto_insurance_declarations_0",
    project_name="DailyDoseofDS",
    organization_id= os.environ["LLAMA_ORG_ID"], 
    api_key= os.environ["LLAMA_CLOUD_API_KEY"] # organization_id and api_key can be set here if required.
)

def get_declarations_docs(policy_number: str, top_k: int = 1):
    """

    Retrieve declarations docs for the given policy using metadata filtering.
    
    """

    filters = MetadataFilters.from_dicts([
        {"key": "policy_number", "value": policy_number}
    ])
    retriever = declarations_index.as_retriever(
        retrieval_mode="files_via_metadata", 
        rerank_top_n=top_k, 
        filters=filters)
    
    # semantic query matters less here
    return retriever.retrieve(f"declarations page for {policy_number}")


# ---------- Instantiate the LLM (e.g., OpenAI GPT-4) ----------

llm = OpenAI(model="gpt-4o", api_key=os.environ["OPENAI_API_KEY"])


# ---------- Define Workflow Events ----------
class ClaimInfoEvent(Event):
    claim_info: ClaimInfo

class PolicyQueryEvent(Event):
    queries: PolicyQueries

class PolicyMatchedEvent(Event):
    policy_text: str

class RecommendationEvent(Event):
    recommendation: PolicyRecommendation

class DecisionEvent(Event):
    decision: ClaimDecision

class LogEvent(Event):
    msg: str
    delta: bool = False


# ---------- Build the Auto Insurance Workflow ----------

class AutoInsuranceWorkflow(Workflow):
    """

        Auto Insurance Claim Workflow.
        Workflow to process an auto insurance claim and generate a recommendation.

        ctx & step decorators are used to define the workflow's passing informaton and lineage.
    
    """
    def __init__(
        self, 
        policy_retriever: BaseRetriever, 
        llm: LLM | None = None, 
        output_dir: str = "data_out", 
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.policy_retriever = policy_retriever
        self.llm = llm or OpenAI(model="gpt-4o")
    
    @step
    async def load_claim_info(self, ctx: Context, ev: StartEvent) -> ClaimInfoEvent:
        claim_info = parse_claim_from_text(ev.claim_json_text)
        await ctx.set("claim_info", claim_info)
        if self._verbose:
            ctx.write_event_to_stream(LogEvent(msg=f"Loaded claim info for {claim_info.claim_number}"))
        return ClaimInfoEvent(claim_info=claim_info)

    @step
    async def generate_policy_queries(self, ctx: Context, ev: ClaimInfoEvent) -> PolicyQueryEvent:
        if self._verbose:
            ctx.write_event_to_stream(LogEvent(msg=">> Generating Policy Queries"))
        prompt = ChatPromptTemplate.from_messages([("user", GENERATE_POLICY_QUERIES_PROMPT)])
        queries = await self.llm.astructured_predict(
            PolicyQueries,
            prompt,
            claim_info=ev.claim_info.model_dump_json()
        )
        return PolicyQueryEvent(queries=queries)

    @step
    async def retrieve_policy_text(self, ctx: Context, ev: PolicyQueryEvent) -> PolicyMatchedEvent:
        if self._verbose:
            ctx.write_event_to_stream(LogEvent(msg=">> Retrieving policy sections"))

        claim_info = await ctx.get("claim_info")
        
        combined_docs = {}
        for query in ev.queries.queries:
            if self._verbose:
                ctx.write_event_to_stream(LogEvent(msg=f">> Query: {query}"))
            # fetch policy text
            docs = await self.policy_retriever.aretrieve(query)
            for d in docs:
                combined_docs[d.id_] = d

        # also fetch the declarations page for the policy holder
        d_doc = get_declarations_docs(claim_info.policy_number)[0]
        combined_docs[d_doc.id_] = d_doc
        
        policy_text = "\n\n".join([doc.get_content() for doc in combined_docs.values()])
        await ctx.set("policy_text", policy_text)
        return PolicyMatchedEvent(policy_text=policy_text)

    @step
    async def generate_recommendation(self, ctx: Context, ev: PolicyMatchedEvent) -> RecommendationEvent:
        if self._verbose:
            ctx.write_event_to_stream(LogEvent(msg=">> Generating Policy Recommendation"))
        claim_info = await ctx.get("claim_info")
        prompt = ChatPromptTemplate.from_messages([("user", POLICY_RECOMMENDATION_PROMPT)])
        recommendation = await self.llm.astructured_predict(
            PolicyRecommendation,
            prompt,
            claim_info=claim_info.model_dump_json(),
            policy_text=ev.policy_text
        )
        if self._verbose:
            ctx.write_event_to_stream(LogEvent(msg=f">> Recommendation: {recommendation.model_dump_json()}"))
        return RecommendationEvent(recommendation=recommendation)

    @step
    async def finalize_decision(self, ctx: Context, ev: RecommendationEvent) -> DecisionEvent:
        if self._verbose:
            ctx.write_event_to_stream(LogEvent(msg=">> Finalizing Decision"))
        claim_info = await ctx.get("claim_info")
        rec = ev.recommendation
        covered = "covered" in rec.recommendation_summary.lower() or (rec.settlement_amount is not None and rec.settlement_amount > 0)
        deductible = rec.deductible if rec.deductible is not None else 0.0
        recommended_payout = rec.settlement_amount if rec.settlement_amount else 0.0
        decision = ClaimDecision(
            claim_number=claim_info.claim_number,
            covered=covered,
            deductible=deductible,
            recommended_payout=recommended_payout,
            notes=rec.recommendation_summary
        )
        return DecisionEvent(decision=decision)

    @step
    async def output_result(self, ctx: Context, ev: DecisionEvent) -> StopEvent:
        if self._verbose:
            ctx.write_event_to_stream(LogEvent(msg=f">> Decision: {ev.decision.model_dump_json()}"))
        return StopEvent(result={"decision": ev.decision})

workflow = AutoInsuranceWorkflow(policy_retriever=retriever, llm=llm, verbose=True, timeout=None)


# ---------- Helper to Display Step Logs in Sidebar ----------
def display_log(message: str, color: str = "#4CAF50"):
    st.markdown(f"""
    <div style="padding: 8px; margin-bottom: 6px; background-color: {color}; color: white; border-radius: 4px;">
      {message}
    </div>
    """, unsafe_allow_html=True)

# ---------- Function to Run the Workflow Asynchronously ----------
async def run_workflow(claim_json_text: str):

    st.write("Running the Claim Workflow...")
    handler = workflow.run(claim_json_text=claim_json_text)

    async for event in handler.stream_events():
        if isinstance(event, LogEvent):
            if event.delta:
                display_log(event.msg)
            else:
                display_log(event.msg)
            
    return await handler

# ---------- Custom CSS for Styling ----------

st.markdown("""
<style>
.main {
    background-color: #f9fafb;
    font-family: 'Inter', sans-serif;
}     
.decision-output {
   background-color: #1E1E1E;
   border-radius: 10px;
   padding: 1rem;
   margin-top: 1.5rem;
   box-shadow: 0px 5px 15px rgba(0,0,0,0.5);
   color: #ffffff;
}
.decision-output h4 {
   color: #ffffff;
   margin-bottom: 0.5rem;
}
.decision-output p {
   margin: 0.5rem 0;
}
.decision-output .number {
   color: #FFD700;
   font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


# ---------- Main Content Container ----------
st.markdown("<div class='main'>", unsafe_allow_html=True)
st.header("ClaimSonic: Auto Claim Agent 🚗")
st.markdown("<p class='subheader'>claim adjuster's smart assistant for processing auto insurance claims.</p>", unsafe_allow_html=True)
st.info("Please input a JSON with details from the claims portal, including claim number, date of loss, claimant name, policy number, loss description, estimated repair cost, and vehicle details.")

    
# ---------- Use ACE Editor for JSON Input ----------
claim_json_input = st_ace(
    value="""{
  "claim_number": "",
  "policy_number": "",
  "claimant_name": "",
  "date_of_loss": "",
  "loss_description": "",
  "estimated_repair_cost": "",
  "vehicle_details": ""
}""",
    language='json',
    theme='monokai',
    keybinding='vscode',
    height=200,
    font_size=14,
    show_gutter=True,
    wrap=True,
)

if st.button("Run Claim Workflow"):
    with st.spinner("Generating decision..."):
        result = asyncio.run(run_workflow(claim_json_input))
        decision = result["decision"]
        st.markdown(f"""
        <div class='decision-output'>
            <h4>Final Claim Decision</h4>
            <p><strong>Claim Number:</strong> <span class="number">{decision.claim_number}</span></p>
            <p><strong>Covered:</strong> <span class="number">{'Yes' if decision.covered else 'No'}</span></p>
            <p><strong>Deductible:</strong> <span class="number">${decision.deductible:.2f}</span></p>
            <p><strong>Recommended Payout:</strong> <span class="number">${decision.recommended_payout:.2f}</span></p>
            <p><strong>Notes:</strong> {decision.notes}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)



    
# ---------- The side bar with some info on the app ----------
st.sidebar.markdown("""
<div style="max-width: 300px; padding: 1rem; background-color: #1c1c1c; border-radius: 10px; box-shadow: 0px 5px 15px rgba(0,0,0,0.5);">
  <h3 style="color: #00796b; monospace;">ClaimSonic 🚗</h3>
  <ul style="color: #ffffff; font-size: 0.9rem; line-height: 1.4; padding-left: 1rem; margin: 0;">
    <li><strong>Parse Claim:</strong> Extract key fields (claim #, date, name, policy, loss, cost).</li>
    <li><strong>Index Docs:</strong> Load policy documents via LlamaCloud or similar.</li>
    <li><strong>Generate Queries:</strong> Build indexed vector queries for precise coverage.</li>
    <li><strong>Match Policy:</strong> Use LLM to assess coverage, deductibles & endorsements.</li>
    <li><strong>Output:</strong> Summarize the final settlement & payment terms.</li>
  </ul>
</div>
""", unsafe_allow_html=True)


