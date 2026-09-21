from typing import List, Optional, Tuple
from pydantic import BaseModel, Field
from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Context,
    Workflow,
    step,
)


# PATIENT INFO SCHEMA
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


# CONDITION BUNDLE SCHEMA
class ConditionBundle(BaseModel):
    condition: ConditionInfo
    encounters: List[EncounterInfo] = Field(default_factory=list)
    medications: List[MedicationInfo] = Field(default_factory=list)

class ConditionBundles(BaseModel):
    bundles: List[ConditionBundle]


#GUIDELINE RECOMMENDATION SCHEMA
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

# FINAL OUTPUT SCHEMA
class ConditionSummary(BaseModel):
    condition_display: str = Field(..., description="Human-readable name of the condition.")
    summary: str = Field(...,
                         description="A concise narrative summarizing the condition’s status, relevant encounters, medications, and guideline recommendations.")


class CaseSummary(BaseModel):
    patient_name: str = Field(..., description="The patient's name.")
    age: int = Field(..., description="The patient's age in years.")
    overall_assessment: str = Field(...,
                                    description="A high-level summary synthesizing all conditions, encounters, medications, and guideline recommendations.")
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

# EVENTS SCHEMA
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