import nest_asyncio
import os
from pathlib import Path
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field
import json
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import LLM
from llama_index.core.prompts import ChatPromptTemplate
from llama_index.core.types import ChatMessage
from src.parse_patient_data import parse_synthea_patient, PatientInfo
from src.bundle_creator import create_condition_bundles, ConditionBundle, ConditionBundles
from src.llama_index_retreiver import retriever
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Context,
    Workflow,
    step,
)
import logging


nest_asyncio.apply()


patient_info = parse_synthea_patient("data/almeta_buckridge.json")

condition_bundles = create_condition_bundles(patient_info)



class GuidelineQueries(BaseModel):
    """Represents a set of recommended queries to retrieve guideline sections relevant to the patient's conditions."""
    queries: List[str] = Field(
        default_factory=list,
        description="A list of query strings that can be used to search a vector index of medical guidelines."
    )

class GuidelineRecommendation(BaseModel):
    guideline_source: str = Field(..., description="The origin of the guideline (e.g., 'NHLBI Asthma Guidelines').")
    recommendation_summary: str = Field(..., description="A concise summary of the relevant recommendation.")
    reference_section: Optional[str] = Field(None, description="Specific section or reference in the guideline.")

class ConditionSummary(BaseModel):
    condition_display: str = Field(..., description="Human-readable name of the condition.")
    summary: str = Field(..., description="A concise narrative summarizing the condition’s status, relevant encounters, medications, and guideline recommendations.")

class CaseSummary(BaseModel):
    patient_name: str = Field(..., description="The patient's name.")
    age: int = Field(..., description="The patient's age in years.")
    overall_assessment: str = Field(..., description="A high-level summary synthesizing all conditions, encounters, medications, and guideline recommendations.")
    condition_summaries: List[ConditionSummary] = Field(
        default_factory=list,
        description="A list of condition-specific summaries providing insight into each condition's current management and recommendations."
    )

    def render(self) -> str:
        lines = []
        lines.append(f"Patient Name: {self.patient_name}")
        lines.append(f"Age: {self.age} years")
        lines.append("")
        lines.append("Overall Assessment:")
        lines.append(self.overall_assessment)
        lines.append("")
        
        if self.condition_summaries:
            lines.append("Condition Summaries:")
            for csum in self.condition_summaries:
                lines.append(f"- {csum.condition_display}:")
                lines.append(f"  {csum.summary}")
        else:
            lines.append("No specific conditions were summarized.")

        return "\n".join(lines)
    
    



_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)



GUIDELINE_QUERIES_PROMPT = """\
You are an assistant tasked with determining what guidelines would be most helpful to consult for a given patient's condition data. You have:

- Patient information (demographics, conditions, encounters, medications)
- A single condition bundle that includes:
  - One specific condition and its related encounters and medications
- Your goal is to produce several high-quality search queries that can be used to retrieve relevant guideline sections from a vector index of medical guidelines.

**Instructions:**
1. Review the patient info and the condition bundle. Identify the key aspects of the condition that might require guideline consultation—such as disease severity, typical management steps, trigger avoidance, or medication optimization.
2. Consider what clinicians would look up:
   - Best practices for this condition's management (e.g., stepwise therapy for asthma, maintenance therapy for atopic dermatitis)
   - Medication recommendations (e.g., use of inhaled corticosteroids, timing and dose adjustments, rescue inhaler usage, antihistamines for atopic dermatitis)
   - Encounter follow-ups (e.g., what follow-up intervals are recommended, what tests or measurements to track)
   - Patient education and preventive measures (e.g., trigger avoidance, skincare routines, inhaler technique)
3. Formulate 3-5 concise, targeted queries that, if run against a medical guideline index, would return the most relevant sections. Each query should be a natural language string that could be used with a vector-based retrieval system. 
4. Make the queries condition-specific, incorporating relevant medications or encounter findings. 
5. Return the output as a JSON object following the schema defined as a tool call.

Patient Info: {patient_info}

Condition Bundle: {condition_info}

Do not include any commentary outside the JSON."""


GUIDELINE_RECOMMENDATION_PROMPT = """\
Given the following patient condition and the corresponding relevant medical guideline text (unformatted), 
generate a guideline recommendation according to the schema defined as a tool call.

The condition details are given below. This includes the condition itself, along with associated encounters/medications
that the patient has taken already. Make sure the guideline recommendation is relevant.

**Patient Condition:**
{patient_condition_text}

**Matched Guideline Text(s):**
{guideline_text}
"""


CASE_SUMMARY_SYSTEM_PROMPT = """\
You are a medical assistant that produces a concise and understandable case summary for a clinician. 

You have access to the patient's name, age, and a list of conditions. 

For each condition, you also have related encounters, medications, and guideline recommendations. 

Your goal is to produce a `CaseSummary` object in JSON format that adheres to the CaseSummary schema, defined as a tool call.

**Instructions:**
- Use the patient's name and age as given.
- Create an `overall_assessment` that integrates the data about their conditions, encounters, medications, and guideline recommendations.
- For each condition, write a short `summary` describing:
  - The current state of the condition.
  - Relevant encounters that indicate progress or issues.
  - Medications currently managing that condition and if they align with guidelines.
  - Any key recommendations from the guidelines that should be followed going forward.
- Keep the summaries patient-friendly but medically accurate. Be concise and clear.
- Return only the final JSON that matches the schema. No extra commentary.

"""

CASE_SUMMARY_USER_PROMPT = """\
**Patient Demographics**
{demographic_info}

**Condition Information**
{condition_guideline_info}


Given the above data, produce a `CaseSummary` as per the schema.
"""

def generate_condition_guideline_str(
    bundle: ConditionBundle,
    rec: GuidelineRecommendation
) -> str:
    return f"""\
**Condition Info**:
{bundle.json()}

**Recommendation**:
{rec.json()}
"""


class PatientInfoEvent(Event):
    patient_info: PatientInfo


class ConditionBundleEvent(Event):
    bundles: ConditionBundles


class MatchGuidelineEvent(Event):
    bundle: ConditionBundle


class MatchGuidelineResultEvent(Event):
    bundle: ConditionBundle
    rec: GuidelineRecommendation


class GenerateCaseSummaryEvent(Event):
    condition_guideline_info: List[Tuple[ConditionBundle, GuidelineRecommendation]]


class LogEvent(Event):
    msg: str
    delta: bool = False


class GuidelineRecommendationWorkflow(Workflow):
    """Guidline recommendation workflow."""

    def __init__(
        self,
        guideline_retriever: BaseRetriever,
        llm: LLM | None = None,
        similarity_top_k: int = 20,
        output_dir: str = "data_out",
        **kwargs,
    ) -> None:
        """Init params."""
        super().__init__(**kwargs)

        self.guideline_retriever = guideline_retriever
        
        self.llm = llm or OpenAI(model="gpt-4o-mini")
        self.similarity_top_k = similarity_top_k

        # if not exists, create
        out_path = Path(output_dir) / "workflow_output"
        if not out_path.exists():
            out_path.mkdir(parents=True, exist_ok=True)
            os.chmod(str(out_path), 0o0777)
        self.output_dir = out_path

    @step
    async def parse_patient_info(
        self, ctx: Context, ev: StartEvent
    ) -> PatientInfoEvent:
        # load patient info from cache if exists, otherwise generate
        patient_info_path = Path(
            f"{self.output_dir}/patient_info.json"
        )
        if patient_info_path.exists():
            if self._verbose:
                ctx.write_event_to_stream(LogEvent(msg=">> Loading patient info from cache"))
            patient_info_dict = json.load(open(str(patient_info_path), "r"))
            patient_info = PatientInfo.model_validate(patient_info_dict)
        else:
            if self._verbose:
                ctx.write_event_to_stream(LogEvent(msg=">> Reading patient info"))
            patient_info = parse_synthea_patient(ev.patient_json_path)
            
            if not isinstance(patient_info, PatientInfo):
                raise ValueError(f"Invalid patient info: {patient_info}")
            # save patient info to file
            with open(patient_info_path, "w") as fp:
                fp.write(patient_info.model_dump_json())
        if self._verbose:
            ctx.write_event_to_stream(LogEvent(msg=f">> Patient Info: {patient_info.dict()}"))

        await ctx.set("patient_info", patient_info)

        return PatientInfoEvent(patient_info=patient_info)

    @step
    async def create_condition_bundles(
        self, ctx: Context, ev: PatientInfoEvent
    ) -> ConditionBundleEvent:
        """Create condition bundles."""
        # load patient condition info from cache if exists, otherwise generate
        condition_info_path = Path(
            f"{self.output_dir}/condition_bundles.json"
        )
        if condition_info_path.exists():
            condition_bundles = ConditionBundles.model_validate(
                json.load(open(str(condition_info_path), "r"))
            )
        else:
            condition_bundles = await create_condition_bundles(ev.patient_info)
            with open(condition_info_path, "w") as fp:
                fp.write(condition_bundles.model_dump_json())
            
        return ConditionBundleEvent(bundles=condition_bundles)

    @step
    async def dispatch_guideline_match(
        self, ctx: Context, ev: ConditionBundleEvent
    ) -> MatchGuidelineEvent:
        """For each condition + associated information, find relevant guidelines.

        Use a map-reduce pattern. 
        
        """
        await ctx.set("num_conditions", len(ev.bundles.bundles))
        
        for bundle in ev.bundles.bundles:
            ctx.send_event(MatchGuidelineEvent(bundle=bundle))

    @step
    async def handle_guideline_match(
        self, ctx: Context, ev: MatchGuidelineEvent
    ) -> MatchGuidelineResultEvent:
        """Generate guideline recommendation for each condition."""
        patient_info = await ctx.get("patient_info")
        
        # We will first generate the right set of questions to ask given the patient info.
        prompt = ChatPromptTemplate.from_messages([
            ("user", GUIDELINE_QUERIES_PROMPT)
        ])
        guideline_queries = await self.llm.astructured_predict(
            GuidelineQueries,
            prompt,
            patient_info=patient_info.demographic_str,
            condition_info=ev.bundle.json()
        )

        guideline_docs_dict = {}
        # fetch all relevant guidelines as text
        for query in guideline_queries.queries:
            if self._verbose:
                ctx.write_event_to_stream(LogEvent(msg=f">> Generating query: {query}"))
            cur_guideline_docs = self.guideline_retriever.retrieve(query)
            guideline_docs_dict.update({
                d.id_: d for d in cur_guideline_docs
            })
        guideline_docs = guideline_docs_dict.values()
        guideline_text="\n\n".join([g.get_content() for g in guideline_docs])
        if self._verbose:
            ctx.write_event_to_stream(
                LogEvent(msg=f">> Found guidelines: {guideline_text[:200]}...")
            )
        
        # generate guideline recommendation
        prompt = ChatPromptTemplate.from_messages([
            ("user", GUIDELINE_RECOMMENDATION_PROMPT)
        ])
        guideline_rec = await self.llm.astructured_predict(
            GuidelineRecommendation,
            prompt,
            patient_info=patient_info.demographic_str,
            condition_info=ev.bundle.json(),
            guideline_text=guideline_text
        )
        if self._verbose:
            ctx.write_event_to_stream(
                LogEvent(msg=f">> Guideline recommendation: {guideline_rec.json()}")
            )
        
        if not isinstance(guideline_rec, GuidelineRecommendation):
            raise ValueError(f"Invalid guideline recommendation: {guideline_rec}")

        return MatchGuidelineResultEvent(bundle=ev.bundle, rec=guideline_rec)

    @step
    async def gather_guideline_match(
        self, ctx: Context, ev: MatchGuidelineResultEvent
    ) -> GenerateCaseSummaryEvent:
        """Handle matching clause against guideline."""
        num_conditions = await ctx.get("num_conditions")
        events = ctx.collect_events(ev, [MatchGuidelineResultEvent] * num_conditions)
        if events is None:
            return

        match_results = [(e.bundle, e.rec) for e in events]
        # save match results
        recs_path = Path(f"{self.output_dir}/guideline_recommendations.jsonl")
        with open(recs_path, "w") as fp:
            for _, rec in match_results:
                fp.write(rec.model_dump_json() + "\n")
            
            
        return GenerateCaseSummaryEvent(condition_guideline_info=match_results)

    @step
    async def generate_output(
        self, ctx: Context, ev: GenerateCaseSummaryEvent
    ) -> StopEvent:
        if self._verbose:
            ctx.write_event_to_stream(LogEvent(msg=">> Generating Case Summary"))

        patient_info = await ctx.get("patient_info")
        demographic_info = patient_info.demographic_str

        condition_guideline_strs = []
        for condition_bundle, guideline_rec in ev.condition_guideline_info:
            condition_guideline_strs.append(
                generate_condition_guideline_str(condition_bundle, guideline_rec)
            )
        condition_guideline_str = "\n\n".join(condition_guideline_strs)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", CASE_SUMMARY_SYSTEM_PROMPT),
            ("user", CASE_SUMMARY_USER_PROMPT)
        ])
        case_summary = await self.llm.astructured_predict(
            CaseSummary,
            prompt,
            demographic_info=demographic_info,
            condition_guideline_info=condition_guideline_str
        )

        return StopEvent(result={"case_summary": case_summary})
    

llm = OpenAI(model="gpt-4o-mini")
workflow = GuidelineRecommendationWorkflow(
    guideline_retriever=retriever,
    llm=llm,
    verbose=True,
    timeout=None,  # don't worry about timeout to make sure it completes
)