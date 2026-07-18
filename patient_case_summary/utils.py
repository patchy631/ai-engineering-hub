import json
from datetime import datetime
from typing import List, Optional
from llama_index.core.llms import LLM
from llama_index.llms.openai import OpenAI
from llama_index.core.prompts import ChatPromptTemplate
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex

import asyncio
import nest_asyncio
nest_asyncio.apply()

from data_model import *

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



async def create_condition_bundles(
    patient_data: PatientInfo, llm: Optional[LLM] = None
) -> ConditionBundles:
    llm = llm or OpenAI(model="gpt-4-turbo")
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

