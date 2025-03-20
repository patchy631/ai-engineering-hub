import loguru

from llama_index.core.workflow import StartEvent, StopEvent, Context, Workflow, step
from llama_index.core.prompts import ChatPromptTemplate

from models import PolicyQueries, PolicyRecommendation, ClaimDecision
from utils import (
    fetch_declaration_documents,
    extract_claim_data,
    process_claim_json,
)
from events import (
    ClaimInfoEvent,
    PolicyQueryEvent,
    PolicyMatchedEvent,
    RecommendationEvent,
    DecisionEvent,
)


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
    def __init__(
        self,
        policy_retriever,
        declarations_index=None,
        llm=None,
        output_dir: str = "data_out",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.policy_retriever = policy_retriever
        self.declarations_index = declarations_index
        self.llm = llm

    @step
    async def load_claim_info(self, ctx: Context, ev: StartEvent) -> ClaimInfoEvent:
        if self._verbose:
            loguru.logger.info(">> Loading Claim Info")
        if hasattr(ev, "claim_json_path"):
            claim_info = extract_claim_data(ev.claim_json_path)
        elif hasattr(ev, "claim_json_string"):
            claim_info = process_claim_json(ev.claim_json_string)
        else:
            raise ValueError("No claim information provided")
        await ctx.set("claim_info", claim_info)
        return ClaimInfoEvent(claim_info=claim_info)

    @step
    async def generate_policy_queries(
        self, ctx: Context, ev: ClaimInfoEvent
    ) -> PolicyQueryEvent:
        if self._verbose:
            loguru.logger.info(">> Generating Policy Queries")
        prompt = ChatPromptTemplate.from_messages(
            [("user", GENERATE_POLICY_QUERIES_PROMPT)]
        )
        queries = await self.llm.astructured_predict(
            PolicyQueries, prompt, claim_info=ev.claim_info.model_dump_json()
        )
        return PolicyQueryEvent(queries=queries)

    @step
    async def retrieve_policy_text(
        self, ctx: Context, ev: PolicyQueryEvent
    ) -> PolicyMatchedEvent:
        if self._verbose:
            loguru.logger.info(">> Retrieving policy sections")
        claim_info = await ctx.get("claim_info")
        # Retrieve from claims index
        claim_docs = {}
        for query in ev.queries.queries:
            if self._verbose:
                loguru.logger.info(f">> Query: {query}")
            docs = await self.policy_retriever.aretrieve(query)
            if not docs:
                loguru.logger.info(
                    f">> Warning: No documents returned for query: {query}"
                )
            for d in docs:
                claim_docs[d.id_] = d
        claim_text = (
            "\n\n".join([doc.get_content() for doc in claim_docs.values()])
            if claim_docs
            else "No claim policy text retrieved."
        )
        loguru.logger.info(f"Claim text: {claim_text}")
        # Retrieve from declarations index
        declarations_text = "No declarations retrieved."
        if self.declarations_index:
            try:
                d_docs = fetch_declaration_documents(
                    claim_info.policy_number,
                    max_results=1,
                    decl_index=self.declarations_index,
                )
                if d_docs and len(d_docs) > 0:
                    declarations_text = d_docs[0].get_content()
            except Exception as e:
                if self._verbose:
                    loguru.logger.error(f">> Error fetching declarations page: {e}")

        # Store both in context
        await ctx.set("claim_text", claim_text)
        await ctx.set("declarations_text", declarations_text)
        # Combine for downstream steps (if needed)
        policy_text = f"{claim_text}\n\n{declarations_text}"
        return PolicyMatchedEvent(policy_text=policy_text)

    @step
    async def generate_recommendation(
        self, ctx: Context, ev: PolicyMatchedEvent
    ) -> RecommendationEvent:
        if self._verbose:
            loguru.logger.info(">> Generating Policy Recommendation")
        claim_info = await ctx.get("claim_info")
        prompt = ChatPromptTemplate.from_messages(
            [("user", POLICY_RECOMMENDATION_PROMPT)]
        )
        recommendation = await self.llm.astructured_predict(
            PolicyRecommendation,
            prompt,
            claim_info=claim_info.model_dump_json(),
            policy_text=ev.policy_text,
        )
        return RecommendationEvent(recommendation=recommendation)

    @step
    async def finalize_decision(
        self, ctx: Context, ev: RecommendationEvent
    ) -> DecisionEvent:
        if self._verbose:
            loguru.logger.info(">> Finalizing Decision")
        claim_info = await ctx.get("claim_info")
        rec = ev.recommendation
        covered = "covered" in rec.recommendation_summary.lower() or (
            rec.settlement_amount is not None and rec.settlement_amount > 0
        )
        deductible = rec.deductible if rec.deductible is not None else 0.0
        recommended_payout = rec.settlement_amount if rec.settlement_amount else 0.0
        decision = ClaimDecision(
            claim_number=claim_info.claim_number,
            covered=covered,
            deductible=deductible,
            recommended_payout=recommended_payout,
            notes=rec.recommendation_summary,
        )
        return DecisionEvent(decision=decision)

    @step
    async def output_result(self, ctx: Context, ev: DecisionEvent) -> StopEvent:
        if self._verbose:
            loguru.logger.info(">> Finalizing Output")
        claim_text = await ctx.get(
            "claim_text", default="No claim policy text retrieved."
        )
        declarations_text = await ctx.get(
            "declarations_text", default="No declarations retrieved."
        )
        return StopEvent(
            result={
                "decision": ev.decision,
                "claim_text": claim_text,
                "declarations_text": declarations_text,
            }
        )
