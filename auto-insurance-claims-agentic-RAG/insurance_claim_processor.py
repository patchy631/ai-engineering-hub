import nest_asyncio
nest_asyncio.apply()

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import os
import json
import asyncio
from dotenv import load_dotenv

# SCHEMAS
class ClaimInfo(BaseModel):
    """Extracted Insurance claim information."""
    claim_number: str
    policy_number: str
    claimant_name: str
    date_of_loss: str
    loss_description: str
    estimated_repair_cost: float
    vehicle_details: Optional[str] = None

class PolicyQueries(BaseModel):
    queries: List[str] = Field(
        default_factory=list,
        description="A list of query strings to retrieve relevant policy sections."
    )

class PolicyRecommendation(BaseModel):
    """Policy recommendation regarding a given claim."""
    policy_section: str = Field(..., description="The policy section or clause that applies.")
    recommendation_summary: str = Field(..., description="A concise summary of coverage determination.")
    deductible: Optional[float] = Field(None, description="The applicable deductible amount.")
    settlement_amount: Optional[float] = Field(None, description="Recommended settlement payout.")

class ClaimDecision(BaseModel):
    claim_number: str
    covered: bool
    deductible: float
    recommended_payout: float
    notes: Optional[str] = None

# PROMPTS
GENERATE_POLICY_QUERIES_PROMPT = """\
You are an assistant tasked with determining what insurance policy sections to consult for a given auto claim.

**Instructions:**
1. Review the claim data, including the type of loss (rear-end collision), estimated repair cost, and policy number.
2. Identify what aspects of the policy we need:
   - Collision coverage conditions
   - Deductible application
   - Any special endorsements related to rear-end collisions or no-fault scenarios
3. Produce 3-5 queries that can be used against a vector index of insurance policies to find relevant clauses.

Claim Data:
{claim_info}

Return a JSON object matching the PolicyQueries schema.
"""

POLICY_RECOMMENDATION_PROMPT = """\
Given the retrieved policy sections for this claim, determine:
- If the collision is covered
- The applicable deductible
- Recommended settlement amount (e.g., cost minus deductible)
- Which policy section applies

Claim Info:
{claim_info}

Policy Text:
{policy_text}

Return a JSON object matching PolicyRecommendation schema.
"""

# WORKFLOW DEFINITIONS
from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Context,
    Workflow,
    step
)
from llama_index.core.llms import LLM
from llama_index.core.prompts import ChatPromptTemplate
from llama_index.core.retrievers import BaseRetriever

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

def parse_claim(file_path: str) -> ClaimInfo:
    with open(file_path, "r") as f:
        data = json.load(f)
    return ClaimInfo.model_validate(data)

def parse_claim_dict(claim_data: Dict[str, Any]) -> ClaimInfo:
    return ClaimInfo.model_validate(claim_data)

class AutoInsuranceWorkflow(Workflow):
    def __init__(
        self, 
        policy_retriever: BaseRetriever, 
        declarations_retriever_func,
        llm: LLM | None = None, 
        output_dir: str = "data_out", 
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.policy_retriever = policy_retriever
        self.declarations_retriever_func = declarations_retriever_func
        self.llm = llm

    @step
    async def load_claim_info(self, ctx: Context, ev: StartEvent) -> ClaimInfoEvent:
        if self._verbose:
            ctx.write_event_to_stream(LogEvent(msg=">> Loading Claim Info"))
        
        # Handle both file path and direct json
        if hasattr(ev, 'claim_json_path') and ev.claim_json_path:
            claim_info = parse_claim(ev.claim_json_path)
        elif hasattr(ev, 'claim_data') and ev.claim_data:
            claim_info = parse_claim_dict(ev.claim_data)
        else:
            raise ValueError("No claim data provided")
            
        await ctx.set("claim_info", claim_info)
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
        
        # Get claim_info from context
        claim_info = await ctx.get("claim_info")
        
        combined_docs = {}
        for query in ev.queries.queries:
            if self._verbose:
                ctx.write_event_to_stream(LogEvent(msg=f">> Query: {query}"))
            # fetch policy text
            docs = await self.policy_retriever.aretrieve(query)
            for d in docs:
                combined_docs[d.id_] = d

        # Also fetch the declarations page for the policy holder
        declaration_docs = self.declarations_retriever_func(str(claim_info.policy_number))
        if declaration_docs:  # Check if list is not empty
            d_doc = declaration_docs[0]
            combined_docs[d_doc.id_] = d_doc
        else:
            # Log the issue if verbose mode is on
            if self._verbose:
                ctx.write_event_to_stream(LogEvent(msg=f">> Warning: No declaration docs found for policy {claim_info.policy_number}"))
        
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

# HELPER FUNCTION
async def stream_workflow(workflow, **workflow_kwargs):
    handler = workflow.run(**workflow_kwargs)
    events = []
    async for event in handler.stream_events():
        if isinstance(event, LogEvent):
            events.append(event.msg)
            if event.delta:
                print(event.msg, end="")
            else:
                print(event.msg)
    
    result = await handler
    return result, events

# SETUP FUNCTION
def setup_workflow():
    # Load environmental variables
    load_dotenv()
    
    # Load API keys and project info
    gemini_key = os.getenv("GOOGLE_API_KEY")
    llama_cloud_key = os.getenv("LLAMA_CLOUD_API_KEY")
    project_name = os.getenv("PROJECT_NAME")
    organization_id = os.getenv("ORGANIZATION_ID")
    
    # Set up the indices
    from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
    from llama_index.llms.gemini import Gemini
    
    # Initialize policy index
    policy_index = LlamaCloudIndex(
        name="auto_insurance_policies_0", 
        project_name=project_name,
        organization_id=organization_id,
        api_key=llama_cloud_key
    )
    policy_retriever = policy_index.as_retriever(rerank_top_n=3)
    
    # Initialize declarations index
    declarations_index = LlamaCloudIndex(
        name="auto_insurance_declarations_0", 
        project_name=project_name,
        organization_id=organization_id,
        api_key=llama_cloud_key
    )
    
    # Declarations retriever function
    from llama_index.core.vector_stores.types import MetadataFilters
    
    def get_declarations_docs(policy_number: str, top_k: int = 1):
        """Get declarations retriever."""
        # build retriever and query engine
        filters = MetadataFilters.from_dicts([
            {"key": "policy_number", "value": policy_number}
        ])
        retriever = declarations_index.as_retriever(
            rerank_top_n=top_k, 
            filters=filters
        )
        # semantic query matters less here
        return retriever.retrieve(f"declarations page for {policy_number}")
    
    # Set up LLM
    llm = Gemini(
        model="models/gemini-2.0-flash", 
        google_api_key=gemini_key,
        temperature=0.3
    )
    
    # Create and return workflow
    workflow = AutoInsuranceWorkflow(
        policy_retriever=policy_retriever,
        declarations_retriever_func=get_declarations_docs,
        llm=llm,
        verbose=True,
        timeout=None,  # don't worry about timeout to make sure it completes
    )
    
    return workflow

# MAIN PROCESSING FUNCTION
def process_claim(claim_json_path=None, claim_data=None):
    """Process a claim either from a file path or from a dictionary."""
    workflow = setup_workflow()
    
    # Run the workflow with async handling
    kwargs = {}
    if claim_json_path:
        kwargs['claim_json_path'] = claim_json_path
    elif claim_data:
        kwargs['claim_data'] = claim_data
    else:
        raise ValueError("Either claim_json_path or claim_data must be provided")
    
    result, events = asyncio.run(stream_workflow(workflow, **kwargs))
    
    return result["decision"], events