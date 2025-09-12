import json
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from src.memory import ZepMemoryLayer


class MemoryInput(BaseModel):
    """Input schema for memory search tool"""
    query: str = Field(..., description="The search query for memory retrieval.")

class MemoryTool(BaseTool):
    name: str = "memory_search"
    description: str = "Retrieve relevant information from conversation history and user preferences"
    memory_layer: ZepMemoryLayer = Field(..., description="Zep memory layer instance")
    args_schema: Type[BaseModel] = MemoryInput
    
    def _run(self, query: str) -> str:
        try:
            context = self.memory_layer.get_context_block()
            if context:
                result = {
                    "status": "OK",
                    "source_used": "MEMORY",
                    "answer": f"Retrieved relevant context from previous conversations: {context}",
                    "citations": [{"label": "Conversation History", "locator": "zep:memory"}],
                    "confidence": 0.98,
                    "context": context
                }
            else:
                result = {
                    "status": "INSUFFICIENT_CONTEXT",
                    "source_used": "MEMORY",
                    "answer": "No relevant conversation history found",
                    "citations": [],
                    "confidence": 0.0,
                    "context": ""
                }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return json.dumps({
                "status": "ERROR",
                "source_used": "MEMORY",
                "answer": f"Memory retrieval failed: {str(e)}",
                "citations": [],
                "confidence": 0.0,
                "context": ""
            })
