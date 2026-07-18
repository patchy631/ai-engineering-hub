from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path
import json
import os
import logging
import asyncio
from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Context,
    Workflow,
    step,
)
from llama_index.core.llms import LLM
from llama_index.llms.openai import OpenAI
from llama_index.core.retrievers import BaseRetriever

from .data_models import (
    PatientInfo, 
    ConditionBundles, 
    ConditionBundle, 
    GuidelineRecommendation,
    CaseSummary
)
from .data_extraction import parse_synthea_patient
from .condition_mapping import create_condition_bundles
from .guideline_retrieval import (
    generate_guideline_queries,
    generate_guideline_recommendation
)
from .case_summary import generate_case_summary

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

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
    content_type: str = "text"  # Can be "text", "json", or other formats
    data: Optional[Dict[str, Any]] = None  # For structured data like JSON

class GuidelineRecommendationWorkflow(Workflow):
    """Guideline recommendation workflow."""

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
                ctx.write_event_to_stream(LogEvent(
                    msg=f">> Patient Info:",
                    content_type="json",
                    data=patient_info.model_dump()
                ))
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
            if self._verbose:
                ctx.write_event_to_stream(LogEvent(msg=">> Loading condition bundles from cache"))
            condition_bundles = ConditionBundles.model_validate(
                json.load(open(str(condition_info_path), "r"))
            )
        else:
            if self._verbose:
                ctx.write_event_to_stream(LogEvent(msg=">> Creating condition bundles"))
            try:
                # Use a smaller model with increased timeout
                condition_mapping_llm = OpenAI(model="gpt-4o-mini", timeout=120)
                condition_bundles = await create_condition_bundles(
                    ev.patient_info, 
                    llm=condition_mapping_llm
                )
                
                # Save to cache
                with open(condition_info_path, "w") as fp:
                    fp.write(condition_bundles.model_dump_json())
                    
                if self._verbose:
                    ctx.write_event_to_stream(LogEvent(msg=f">> Created {len(condition_bundles.bundles)} condition bundles"))
            except Exception as e:
                if self._verbose:
                    ctx.write_event_to_stream(LogEvent(msg=f">> Error creating condition bundles: {str(e)}"))
                    ctx.write_event_to_stream(LogEvent(msg=">> Using fallback approach"))
                
                # Create a basic mapping where each condition is mapped to all encounters and medications
                bundles = []
                for condition in ev.patient_info.conditions:
                    bundle = ConditionBundle(
                        condition=condition,
                        encounters=ev.patient_info.recent_encounters,
                        medications=ev.patient_info.current_medications
                    )
                    bundles.append(bundle)
                
                condition_bundles = ConditionBundles(bundles=bundles)
                
                # Save to cache
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
        guideline_queries = await generate_guideline_queries(
            patient_info=patient_info,
            condition_bundle=ev.bundle,
            llm=self.llm
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
        guideline_rec = await generate_guideline_recommendation(
            patient_info=patient_info,
            condition_bundle=ev.bundle,
            guideline_text=guideline_text,
            llm=self.llm
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
        
        case_summary = await generate_case_summary(
            patient_info=patient_info,
            condition_guideline_info=ev.condition_guideline_info,
            llm=self.llm
        )

        return StopEvent(result={"case_summary": case_summary}) 