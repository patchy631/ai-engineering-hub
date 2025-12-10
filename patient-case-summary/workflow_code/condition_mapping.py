from typing import Optional
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import LLM
from llama_index.core.prompts import ChatPromptTemplate
from .data_models import PatientInfo, ConditionBundles

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
) -> ConditionBundles:
    """
    Create condition bundles by mapping each condition to relevant encounters and medications.
    
    Args:
        patient_data: Structured patient information
        llm: Language model to use for mapping (defaults to GPT-4o-mini)
        
    Returns:
        ConditionBundles object containing mappings for each condition
    """
    # Use gpt-4o-mini which is faster and more reliable for this task
    llm = llm or OpenAI(model="gpt-4o-mini", timeout=120)  # Increased timeout

    # we will dump the entire patient info into an LLM and have it figure out the relevant encounters/medications
    # associated with each condition
    prompt = ChatPromptTemplate.from_messages([
        ("user", CONDITION_BUNDLE_PROMPT)
    ])
    
    try:
        # Use model_dump_json() instead of json() for Pydantic v2 compatibility
        condition_bundles = await llm.astructured_predict(
            ConditionBundles,
            prompt,
            patient_info=patient_data.model_dump_json()
        )
        return condition_bundles
    except Exception as e:
        # Fallback to a simpler approach if the LLM call fails
        from .data_models import ConditionBundle
        
        # Create a basic mapping where each condition is mapped to all encounters and medications
        bundles = []
        for condition in patient_data.conditions:
            bundle = ConditionBundle(
                condition=condition,
                encounters=patient_data.recent_encounters,
                medications=patient_data.current_medications
            )
            bundles.append(bundle)
        
        return ConditionBundles(bundles=bundles) 