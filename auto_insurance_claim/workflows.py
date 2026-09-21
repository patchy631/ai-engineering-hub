from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Context,
    Workflow,
    step
)
from llama_index.core.prompts import ChatPromptTemplate
from llama_index.core.retrievers import BaseRetriever
import streamlit as st 
import json
from prompts import POLICY_RECOMMENDATION_PROMPT,\
    GENERATE_POLICY_QUERIES_PROMPT
from schema import ClaimInfo, PolicyQueries, PolicyRecommendation, ClaimDecision    
from api import ollama_llm
from declarations import get_declarations_docs

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
    return ClaimInfo.model_validate(data)  # replace "ClaimInfo".model_validate with actual ClaimInfo class method

class AutoInsuranceWorkflow(Workflow):
    """
    Workflow for processing auto insurance claims.
    
    This workflow handles the entire lifecycle of an auto insurance claim:
    1. Loading claim information from a JSON file
    2. Generating policy queries based on the claim
    3. Retrieving relevant policy text
    4. Generating policy recommendations
    5. Finalizing the claim decision
    6. Outputting the result
    """
    def __init__(
        self, 
        policy_retriever: BaseRetriever, 
        llm: ollama_llm,  
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.policy_retriever = policy_retriever
        self.llm = llm 
            
    @step
    async def load_claim_info(self, ctx: Context, ev: StartEvent) -> ClaimInfoEvent:
        if self._verbose:
            ctx.write_event_to_stream(LogEvent(msg=">> Loading Claim Info"))
        claim_info = parse_claim(ev.claim_json_path)
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
        claim_info = await ctx.get("claim_info")
        
        combined_docs = {}
        for query in ev.queries.queries:
            if self._verbose:
                ctx.write_event_to_stream(LogEvent(msg=f">> Query: {query}"))
            retriever = self.policy_retriever.as_retriever()
            docs = await retriever.aretrieve(query)
            for d in docs:
                combined_docs[d.id_] = d

        # also fetch the declarations page for the policy holder
        declaration_doc = get_declarations_docs(claim_info.policy_number)
        if declaration_doc: 
            d_doc = declaration_doc[0]
            combined_docs[d_doc.id_] = d_doc
        else:
            ctx.write_event_to_stream(LogEvent(
               msg=f"No declarations found for policy number: {claim_info.policy_number}"
            )) 
            st.warning(f"No declarations found for policy number: {claim_info.policy_number}")
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
            st.info("Finalizing Decision")
        claim_info = await ctx.get("claim_info")
        rec = ev.recommendation
        summary_lower = rec.recommendation_summary.lower()
        covered = (
            ("covered" in summary_lower and "not covered" not in summary_lower)
            or (rec.settlement_amount is not None and rec.settlement_amount > 0)
        )
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
            st.info(f">> Decision: {ev.decision.model_dump_json()}")
        return StopEvent(result={"decision": ev.decision})
    
