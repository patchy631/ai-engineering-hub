from typing import List, Optional
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_index.core.retrievers import BaseRetriever
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import LLM
from llama_index.core.prompts import ChatPromptTemplate
from .data_models import GuidelineQueries, GuidelineRecommendation, ConditionBundle, PatientInfo

def setup_guideline_retriever(
    name: str = "medical_guidelines_0",
    project_name: str = "llamacloud_demo",
    organization_id: str = "cdcb3478-1348-492e-8aa0-25f47d1a3902",
    api_key: Optional[str] = None,
    similarity_top_k: int = 3
) -> BaseRetriever:
    """
    Set up a retriever for medical guidelines.
    
    Args:
        name: Name of the LlamaCloud index
        project_name: Name of the LlamaCloud project
        organization_id: Organization ID for LlamaCloud
        api_key: LlamaCloud API key (optional)
        similarity_top_k: Number of top results to retrieve
        
    Returns:
        Configured retriever for medical guidelines
    """
    index_kwargs = {
        "name": name,
        "project_name": project_name,
        "organization_id": organization_id,
    }
    
    if api_key:
        index_kwargs["api_key"] = api_key
        
    index = LlamaCloudIndex(**index_kwargs)
    retriever = index.as_retriever(similarity_top_k=similarity_top_k)
    
    return retriever

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

async def generate_guideline_queries(
    patient_info: PatientInfo,
    condition_bundle: ConditionBundle,
    llm: Optional[LLM] = None
) -> GuidelineQueries:
    """
    Generate queries to retrieve relevant guideline sections for a condition.
    
    Args:
        patient_info: Patient demographic information
        condition_bundle: Condition with associated encounters and medications
        llm: Language model to use (defaults to GPT-4o)
        
    Returns:
        GuidelineQueries object containing search queries
    """
    llm = llm or OpenAI(model="gpt-4o")
    
    prompt = ChatPromptTemplate.from_messages([
        ("user", GUIDELINE_QUERIES_PROMPT)
    ])
    
    guideline_queries = await llm.astructured_predict(
        GuidelineQueries,
        prompt,
        patient_info=patient_info.demographic_str,
        condition_info=condition_bundle.json()
    )
    
    return guideline_queries

async def generate_guideline_recommendation(
    patient_info: PatientInfo,
    condition_bundle: ConditionBundle,
    guideline_text: str,
    llm: Optional[LLM] = None
) -> GuidelineRecommendation:
    """
    Generate a guideline recommendation based on retrieved guideline text.
    
    Args:
        patient_info: Patient demographic information
        condition_bundle: Condition with associated encounters and medications
        guideline_text: Retrieved guideline text
        llm: Language model to use (defaults to GPT-4o)
        
    Returns:
        GuidelineRecommendation object
    """
    llm = llm or OpenAI(model="gpt-4o")
    
    prompt = ChatPromptTemplate.from_messages([
        ("user", GUIDELINE_RECOMMENDATION_PROMPT)
    ])
    
    guideline_rec = await llm.astructured_predict(
        GuidelineRecommendation,
        prompt,
        patient_condition_text=condition_bundle.json(),
        guideline_text=guideline_text
    )
    
    return guideline_rec 