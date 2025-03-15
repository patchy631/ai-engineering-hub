from llama_index.llms.openai import OpenAI
from llama_index.core.llms import LLM
from llama_index.core.prompts import ChatPromptTemplate
from .models import PatientInfo, ConditionBundles

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
    patient_data: PatientInfo, llm: LLM = None
) -> ConditionBundles:
    llm = llm or OpenAI(model="gpt-4o-mini")

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