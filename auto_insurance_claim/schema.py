
import nest_asyncio
nest_asyncio.apply()
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date

class ClaimInfo(BaseModel):
    """Extracted Insurance claim information."""
    claim_number: str
    policy_number: str
    claimant_name: str
    date_of_loss: date
    loss_description: str
    estimated_repair_cost: float
    vehicle_details: Optional[str] = None

# Generates guidelines for queries and for storing recommendations
class PolicyQueries(BaseModel):
    queries: List[str] = Field(
    default_factory=list,
    description="A list of query strings to retrieve relevant policy sections."
)
    
# Produces a structured recommendation on claim coverage
class PolicyRecommendation(BaseModel):
    """Policy recommendation regarding a given claim."""
    policy_section: str = Field(..., description="The policy section or clause that applies.")
    recommendation_summary: str = Field(..., description="A concise summary of coverage determination.")
    # Explicitly set the schema type to "number" for optional float fields
    deductible: Optional[float] = Field(
        None, 
        description="The applicable deductible amount.",
        json_schema_extra={"type": "number"}
    )
    settlement_amount: Optional[float] = Field(
        None, 
        description="Recommended settlement payout.",
        json_schema_extra={"type": "number"}
    )
    
# Generates claim decision
class ClaimDecision(BaseModel):
    claim_number: str
    covered: bool
    deductible: float
    recommended_payout: float
    notes: Optional[str] = None

