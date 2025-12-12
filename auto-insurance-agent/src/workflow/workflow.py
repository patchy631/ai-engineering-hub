from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Context,
    Workflow,
    step
)
from llama_index.core.prompts import ChatPromptTemplate
from ..models.schemas import PolicyQueries, PolicyRecommendation, ClaimDecision
from ..utils.helpers import get_declarations_docs, parse_claim, parse_claim_from_json_string
from .events import (
    ClaimInfoEvent, PolicyQueryEvent, PolicyMatchedEvent,
    RecommendationEvent, DecisionEvent, LogEvent
)

# Prompts
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

class AutoInsuranceWorkflow(Workflow):
    """
    Orchestrates the AI-based auto insurance claim processing workflow.
    :param policy_retriever: Retrieves relevant policy documents.
    :param declarations_index: Optional index for fetching declarations pages.
    :param llm: Language model for generating queries and recommendations.
    :param output_dir: Directory path for output artifacts (if utilized).
    """

    def __init__(
        self,
        policy_retriever,
        declarations_index=None,
        llm=None,
        output_dir: str = "data_out",
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.policy_retriever = policy_retriever
        self.declarations_index = declarations_index
        self.llm = llm
        
    @step
    async def load_claim_info(self, ctx: Context, ev: StartEvent) -> ClaimInfoEvent:
        if self._verbose:
            ctx.write_event_to_stream(LogEvent(msg=">> Loading Claim Info"))
        
        # Handle both file path and direct claim info
        if hasattr(ev, 'claim_json_path'):
            claim_info = parse_claim(ev.claim_json_path)
        elif hasattr(ev, 'claim_json_string'):
            claim_info = parse_claim_from_json_string(ev.claim_json_string)
        else:
            raise ValueError("No claim information provided")
            
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
            # fetch policy text
            docs = await self.policy_retriever.aretrieve(query)
            if not docs:
                ctx.write_event_to_stream(LogEvent(msg=f">> Warning: No documents returned for query: {query}"))

            for d in docs:
                combined_docs[d.id_] = d

        # also fetch the declarations page for the policy holder
        try:
            if self.declarations_index:
                d_docs = get_declarations_docs(
                    claim_info.policy_number, 
                    top_k=1, 
                    declarations_index=self.declarations_index
                )
                if d_docs and len(d_docs) > 0:
                    d_doc = d_docs[0]
                    combined_docs[d_doc.id_] = d_doc
        except Exception as e:
            if self._verbose:
                ctx.write_event_to_stream(LogEvent(msg=f">> Error fetching declarations page: {e}"))

        policy_text = "\n\n".join([doc.get_content() for doc in combined_docs.values()])
        await ctx.set("policy_text", policy_text)
        return PolicyMatchedEvent(policy_text=policy_text)

    @step
    async def generate_recommendation(self, ctx: Context, ev: PolicyMatchedEvent) -> RecommendationEvent:
        if self._verbose:
            ctx.write_event_to_stream(LogEvent(msg=">> Generating Policy Recommendation"))
        claim_info = await ctx.get("claim_info")
        prompt = ChatPromptTemplate.from_messages([("user", POLICY_RECOMMENDATION_PROMPT)])
        try:
            recommendation = await self.llm.astructured_predict(
                PolicyRecommendation,
                prompt,
                claim_info=claim_info.model_dump_json(),
                policy_text=ev.policy_text
            )
            if self._verbose:
                ctx.write_event_to_stream(LogEvent(msg=f">> Recommendation: {recommendation.model_dump_json()}"))
            return RecommendationEvent(recommendation=recommendation)
        except Exception as e:
            if self._verbose:
                ctx.write_event_to_stream(LogEvent(msg=f">> Error generating recommendation: {e}"))
            raise e

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
