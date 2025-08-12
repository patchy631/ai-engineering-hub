from pydantic import BaseModel
from typing import List

# Define data structures to capture documentation planning output
class DocItem(BaseModel):
    """Represents a documentation item"""
    title: str
    description: str
    prerequisites: str
    examples: List[str]
    goal: str

class DocPlan(BaseModel):
    """Documentation plan"""
    overview: str
    docs: List[DocItem]