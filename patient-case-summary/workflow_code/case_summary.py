from typing import List, Tuple
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import LLM
from llama_index.core.prompts import ChatPromptTemplate
from .data_models import PatientInfo, ConditionBundle, GuidelineRecommendation, CaseSummary

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
    """
    Generate a formatted string combining condition and guideline information.
    
    Args:
        bundle: Condition bundle with associated encounters and medications
        rec: Guideline recommendation for the condition
        
    Returns:
        Formatted string with condition and guideline information
    """
    return f"""\
**Condition Info**:
{bundle.json()}

**Recommendation**:
{rec.json()}
"""

async def generate_case_summary(
    patient_info: PatientInfo,
    condition_guideline_info: List[Tuple[ConditionBundle, GuidelineRecommendation]],
    llm: LLM = None
) -> CaseSummary:
    """
    Generate a comprehensive case summary for a patient.
    
    Args:
        patient_info: Patient demographic information
        condition_guideline_info: List of condition bundles and their guideline recommendations
        llm: Language model to use (defaults to GPT-4o)
        
    Returns:
        CaseSummary object containing the complete case summary
    """
    llm = llm or OpenAI(model="gpt-4o")
    
    demographic_info = patient_info.demographic_str
    
    condition_guideline_strs = []
    for condition_bundle, guideline_rec in condition_guideline_info:
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
    
    return case_summary 