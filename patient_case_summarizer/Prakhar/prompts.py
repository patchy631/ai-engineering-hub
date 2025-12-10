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
