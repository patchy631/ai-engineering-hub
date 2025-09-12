import os
import json
from typing import Dict, Any, List, Optional
from openai import OpenAI

SYSTEM_PROMPT = """You are a research assistant that MUST ground answers in provided context.
Policy:
1) Use only the supplied CONTEXT and/or explicit SOURCE items.
2) If context is INSUFFICIENT to answer the QUESTION, return status=INSUFFICIENT_CONTEXT with what is missing.
3) If sufficient, answer concisely with citations (doc/page or URL) and a confidence score (0–1).
4) Never rely on parametric knowledge if it is not in the context.
5) Output MUST match the response schema exactly.
"""

RAG_TEMPLATE = (
    "CONTEXT:\n{context}\n"
    "---------------------\n"
    "QUESTION:\n{query}\n\n"
    "Task: Determine if the CONTEXT is sufficient to answer the QUESTION.\n"
    "- If sufficient: produce a grounded answer with citations and confidence.\n"
    "- If NOT sufficient: do NOT answer; return status=INSUFFICIENT_CONTEXT and list missing info.\n"
    "Fill the structured fields only.\n"
)

# Structured Output schema 
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["OK", "INSUFFICIENT_CONTEXT"]},
        "source_used": {"type": "string", "enum": ["MEMORY", "RAG", "WEB", "TOOL", "NONE"]},
        "answer": {"type": "string"},
        "citations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "label": {"type": "string"},
                    "locator": {"type": "string"}
                },
                "required": ["label", "locator"],
                "additionalProperties": False
            }
        },
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "missing": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["status", "source_used", "answer", "citations", "confidence", "missing"],
    "additionalProperties": False
}


class StructuredResponseGen:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        system_prompt: str = SYSTEM_PROMPT,
        rag_template: str = RAG_TEMPLATE,
        temperature: float = 0.2,
    ):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.system_prompt = system_prompt
        self.rag_template = rag_template
        self.temperature = temperature

    def generate(
        self,
        *,
        query: str,
        context_blocks: List[str],
        source_used: str = "RAG",
        schema: Dict[str, Any] = RESPONSE_SCHEMA,
    ) -> Dict[str, Any]:
        context = "\n\n".join(context_blocks).strip()
        user_prompt = self.rag_template.format(context=context, query=query)

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "research_briefing",
                    "schema": schema,
                    "strict": True  # hard schema adherence
                }
            },
        )

        try:
            output_text = response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Unexpected responses payload shape: {e}")

        try:
            data = json.loads(output_text)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Model did not return valid JSON: {e}\nRaw: {output_text[:400]}")

        data["source_used"] = source_used
        return data