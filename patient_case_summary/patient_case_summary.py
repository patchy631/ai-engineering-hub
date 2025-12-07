#!/usr/bin/env python
# coding: utf-8

# # Patient Case Summary Workflow
# 
# <a href="https://colab.research.google.com/github/run-llama/llamacloud-demo/blob/main/examples/document_workflows/patient_case_summary/patient_case_summary.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>
# 
# This tutorial shows you how to build an agentic workflow that can extract key details from a given patient, check clinical guidelines to see whether the patient's status meets recommended care standards, and then produce a human-readable case summary that a clinician can review.
# 
# ![](patient_case_summary.png)
# 
# We use [Synthea](https://github.com/synthetichealth/synthea) to generate synthetic patient data, which contains a comprehensive set of information surrounding the patient. This includes, among other attributes, active patient conditions, encounters, and medications.
# 
# Given a sample patient, we extract out the relevant information, and use it to retrieve relevant medical guidelines that provide recommendations on continued treatment, and present it to a clinician.

# In[ ]:


get_ipython().system('pip install llama-index llama-index-indices-managed-llama-cloud llama-cloud llama-parse')


# In[90]:


import nest_asyncio

nest_asyncio.apply()


# ## Setup
# 
# We define code snippets which will parse a patient bundle and extract out relevant fields of interest, including:
# 1. Patient demographics
# 2. Condition
# 3. Medication request
# 4. Observation (vital signs)
# 5. Immunization & Procedures
# 
# 
# We also setup an index for relevant clinical guidelines (e.g. ADA for diabetes). 

# In[91]:


from typing import List, Optional
from pydantic import BaseModel, Field

class ConditionInfo(BaseModel):
    code: str
    display: str
    clinical_status: str

class EncounterInfo(BaseModel):
    date: str = Field(..., description="Date of the encounter.")
    reason_display: Optional[str] = Field(None, description="Reason for the encounter.")
    type_display: Optional[str] = Field(None, description="Type or class of the encounter.")

class MedicationInfo(BaseModel):
    name: str = Field(..., description="Name of the medication.")
    start_date: Optional[str] = Field(None, description="When the medication was prescribed.")
    instructions: Optional[str] = Field(None, description="Dosage instructions.")

class PatientInfo(BaseModel):
    given_name: str
    family_name: str
    birth_date: str
    gender: str
    conditions: List[ConditionInfo] = Field(default_factory=list)
    recent_encounters: List[EncounterInfo] = Field(default_factory=list, description="A few recent encounters.")
    current_medications: List[MedicationInfo] = Field(default_factory=list, description="Current active medications.")

    @property
    def demographic_str(self) -> str:
        """Get demographics string."""
        return f"""\
Given name: {self.given_name}
Family name: {self.family_name}
Birth date: {self.birth_date}
Gender: {self.gender}"""


# In[92]:


def parse_synthea_patient(file_path: str, filter_active: bool = True) -> PatientInfo:
    # Load the Synthea-generated FHIR Bundle
    with open(file_path, "r") as f:
        bundle = json.load(f)

    patient_resource = None
    conditions = []
    encounters = []
    medication_requests = []

    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        resource_type = resource.get("resourceType")

        if resource_type == "Patient":
            patient_resource = resource
        elif resource_type == "Condition":
            conditions.append(resource)
        elif resource_type == "Encounter":
            encounters.append(resource)
        elif resource_type == "MedicationRequest":
            medication_requests.append(resource)

    if not patient_resource:
        raise ValueError("No Patient resource found in the provided file.")

    # Extract patient demographics
    name_entry = patient_resource.get("name", [{}])[0]
    given_name = name_entry.get("given", [""])[0]
    family_name = name_entry.get("family", "")
    birth_date = patient_resource.get("birthDate", "")
    gender = patient_resource.get("gender", "")

    # Define excluded conditions
    excluded_conditions = {"Medication review due (situation)", "Risk activity involvement (finding)"}
    condition_info_list = []
    for c in conditions:
        code_info = c.get("code", {}).get("coding", [{}])[0]
        condition_code = code_info.get("code", "Unknown")
        condition_display = code_info.get("display", "Unknown")
        clinical_status = (
            c.get("clinicalStatus", {})
             .get("coding", [{}])[0]
             .get("code", "unknown")
        )
        
        # Check exclusion and active filters
        if condition_display not in excluded_conditions:
            if filter_active:
                if clinical_status == "active":
                    condition_info_list.append(
                        ConditionInfo(
                            code=condition_code,
                            display=condition_display,
                            clinical_status=clinical_status
                        )
                    )
            else:
                # Include conditions regardless of their status if filter_active is False
                condition_info_list.append(
                    ConditionInfo(
                        code=condition_code,
                        display=condition_display,
                        clinical_status=clinical_status
                    )
                )

    # Parse encounters
    def get_encounter_date(enc):
        period = enc.get("period", {})
        start = period.get("start")
        return datetime.fromisoformat(start) if start else datetime.min

    encounters_sorted = sorted(encounters, key=get_encounter_date)
    recent_encounters = encounters_sorted[-3:] if len(encounters_sorted) > 3 else encounters_sorted

    encounter_info_list = []
    for e in recent_encounters:
        period = e.get("period", {})
        start_date = period.get("start", "")
        reason = e.get("reasonCode", [{}])[0].get("coding", [{}])[0].get("display", None)
        etype = e.get("type", [{}])[0].get("coding", [{}])[0].get("display", None)
        encounter_info_list.append(
            EncounterInfo(
                date=start_date,
                reason_display=reason,
                type_display=etype
            )
        )

    # Parse medications
    medication_info_list = []
    for m in medication_requests:
        status = m.get("status")
        if status == "active":
            med_code = m.get("medicationCodeableConcept", {}).get("coding", [{}])[0]
            med_name = med_code.get("display", "Unknown Medication")
            authored = m.get("authoredOn", None)
            dosage_instruction = m.get("dosageInstruction", [{}])[0].get("text", None)
            medication_info_list.append(
                MedicationInfo(
                    name=med_name,
                    start_date=authored,
                    instructions=dosage_instruction
                )
            )

    patient_info = PatientInfo(
        given_name=given_name,
        family_name=family_name,
        birth_date=birth_date,
        gender=gender,
        conditions=condition_info_list,
        recent_encounters=encounter_info_list,
        current_medications=medication_info_list
    )

    return patient_info


# In[93]:


# Example Usage
patient_info = parse_synthea_patient("data/almeta_buckridge.json")
patient_info.dict()


# ### Map Conditions to Encounters/Medications
# 
# We now use an LLM to dynamically transform the existing JSON into a new structured output (a "ConditionBundle") where we map each condition to its associated encounters/medications. We rely on the LLM's prior medical knowledge to do this transformation.
# 
# This transformation allows us to then consult the relevant guidelines for each condition.

# In[105]:


class ConditionBundle(BaseModel):
    condition: ConditionInfo
    encounters: List[EncounterInfo] = Field(default_factory=list)
    medications: List[MedicationInfo] = Field(default_factory=list)

class ConditionBundles(BaseModel):
    bundles: List[ConditionBundle]


# In[106]:


from llama_index.llms.openai import OpenAI
from llama_index.core.llms import LLM
from llama_index.core.prompts import ChatPromptTemplate

CONDITION_BUNDLE_PROMPT = """\
You are an assistant that takes a patient's summarized clinical data and associates each active condition with any relevant recent encounters and current medications.

**Steps to follow:**
1. Review the patient's demographics, conditions, recent encounters, and current medications.
2. For each condition in 'conditions':
   - Determine which of the 'recent_encounters' are relevant. An encounter is relevant if:
     - The 'reason_display' or 'type_display' of the encounter mentions or is closely related to the condition.
     - Consider synonyms or partial matches. For example, for "Childhood asthma (disorder)", any encounter mentioning "asthma" or "asthma follow-up" is relevant.
   - Determine which of the 'current_medications' are relevant. A medication is relevant if:
     - The medication 'name' or 'instructions' are clearly related to managing that condition. For example, inhalers or corticosteroids for asthma, topical creams for dermatitis.
     - Consider partial matches. For "Atopic dermatitis (disorder)", a medication used for allergic conditions or skin inflammations could be relevant.
3. Ignore patient demographics for relevance determination; they are just context.
4. Return the final output strictly as a JSON object following the schema (provided as a tool call). 
   Do not include extra commentary outside the JSON.

**Patient Data**:
{patient_info}
"""

async def create_condition_bundles(
    patient_data: PatientInfo, llm: Optional[LLM] = None
) -> ConditionEncounters:
    llm = llm or OpenAI(model="gpt-4o")

    # we will dump the entire patient info into an LLM and have it figure out the relevant encounters/medications
    # associated with each condition
    prompt = ChatPromptTemplate.from_messages([
        ("user", CONDITION_BUNDLE_PROMPT)
    ])
    condition_bundles = await llm.astructured_predict(
        ConditionBundles,
        prompt,
        patient_info=patient_data.json()
    )

    return condition_bundles


# Let's run a sample (we will plug this into a full workflow later)

# In[107]:


condition_bundles = await create_condition_bundles(patient_info)
condition_bundles.dict()


# ### Setup Index
# 
# We've setup the right extraction flow over the patient record. The next step is to setup an index that contains a set of relevant guidelines which we will match against each condition of the patient. This will help us generate a more useful and comprehensive case summary.
# 
# Here we use LlamaCloud: https://cloud.llamaindex.ai/. If you don't have access yet, you're always welcome to use our open-source VectorStoreIndex.

# We use the following guidelines as datapoints:
# 
# - ["Guidelines of care for the management of atopic dermatitis in adults with phototherapy and systemic therapies"](https://www.jaad.org/action/showPdf?pii=S0190-9622%2823%2902878-5) (from JAAD)
# - ["2020 Focused Updates to the Asthma Management Guidelines"](https://www.nhlbi.nih.gov/resources/2020-focused-updates-asthma-management-guidelines) (from NHLBI)
# 
# Download the PDFs, and either upload them to LlamaCloud or index them through `VectorStoreIndex.from_documents`

# In[108]:


from llama_index.indices.managed.llama_cloud import LlamaCloudIndex

index = LlamaCloudIndex(
  name="medical_guidelines_0", 
  project_name="llamacloud_demo",
  organization_id="cdcb3478-1348-492e-8aa0-25f47d1a3902",
  # api_key="llx-..."
)

retriever = index.as_retriever(similarity_top_k=3)


# ### Define Guideline Recommendation Schema
# 
# Given a condition (and associated encounters/medications), define an output schema that represents the matched guideline.
# 
# We need to make sure we ask the right questions in order to retrieve the relevant guidelines.

# In[109]:


from typing import List
from pydantic import BaseModel, Field

class GuidelineQueries(BaseModel):
    """Represents a set of recommended queries to retrieve guideline sections relevant to the patient's conditions."""
    queries: List[str] = Field(
        default_factory=list,
        description="A list of query strings that can be used to search a vector index of medical guidelines."
    )


# In[110]:


class GuidelineRecommendation(BaseModel):
    guideline_source: str = Field(..., description="The origin of the guideline (e.g., 'NHLBI Asthma Guidelines').")
    recommendation_summary: str = Field(..., description="A concise summary of the relevant recommendation.")
    reference_section: Optional[str] = Field(None, description="Specific section or reference in the guideline.")


# ### Define Final Output Schema
# 
# This is the schema for the final case summary. It contains the patient's basic demographic info, conditions, and also matched guideline recommendations.

# In[111]:


from typing import Optional, List
from pydantic import BaseModel, Field

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


# ## Setup Patient Case Summary Workflow
# 
# Let's define the following workflow to generate patient case summaries:
# 1. Extract out patient data including conditions, medications, encounters from the synthetically generated patient JSON (from Synthea)
# 2. Use an LLM to map each condition to relevant medications/encounters (defined as a "condition bundle") 
# 3. For each condition bundle, generate a set of search queries to match it against relevant medical guidelines in our index.
# 4. Generate final case summary.

# In[159]:


from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Context,
    Workflow,
    step,
)
from llama_index.core.llms import LLM
from typing import Optional, Tuple
from pydantic import BaseModel
from llama_index.core import SimpleDirectoryReader
from llama_index.core.schema import Document
from llama_index.core.agent import FunctionCallingAgentWorker
from llama_index.core.prompts import ChatPromptTemplate
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.retrievers import BaseRetriever
from pathlib import Path
import logging
import json
import os

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
        guideline_queries = await llm.astructured_predict(
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
        guideline_rec = await llm.astructured_predict(
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
        case_summary = await llm.astructured_predict(
            CaseSummary,
            prompt,
            demographic_info=demographic_info,
            condition_guideline_info=condition_guideline_str
        )

        return StopEvent(result={"case_summary": case_summary})


# In[160]:


from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-4o")
workflow = GuidelineRecommendationWorkflow(
    guideline_retriever=retriever,
    llm=llm,
    verbose=True,
    timeout=None,  # don't worry about timeout to make sure it completes
)


# #### Visualize the workflow

# In[161]:


from llama_index.utils.workflow import draw_all_possible_flows

draw_all_possible_flows(GuidelineRecommendationWorkflow, filename="guideline_rec_workflow.html")


# ## Run the Workflow
# 
# Let's run the full workflow and generate the output! 

# In[162]:


from IPython.display import clear_output

handler = workflow.run(patient_json_path="data/almeta_buckridge.json")
async for event in handler.stream_events():
    if isinstance(event, LogEvent):
        if event.delta:
            print(event.msg, end="")
        else:
            print(event.msg)

response_dict = await handler
print(str(response_dict["case_summary"]))


# In[164]:


print(str(response_dict["case_summary"].render()))


# In[ ]:




