from typing import List, Optional
from pydantic import BaseModel, Field

class ClaimInfo(BaseModel):
    """Extracted Insurance claim information."""
    claim_number: str
    policy_number: str
    claimant_name: str
    date_of_loss: str
    loss_description: str
    estimated_repair_cost: float
    vehicle_details: Optional[str] = None

class PolicyQueries(BaseModel):
    """Collection of queries to retrieve relevant policy sections."""
    queries: List[str] = Field(
        default_factory=list,
        description="A list of query strings to retrieve relevant policy sections."
    )

class PolicyRecommendation(BaseModel):
    """Policy recommendation regarding a given claim."""
    policy_section: str = Field(..., description="The policy section or clause that applies.")
    recommendation_summary: str = Field(..., description="A concise summary of coverage determination.")
    deductible: Optional[float] = Field(None, description="The applicable deductible amount.")
    settlement_amount: Optional[float] = Field(None, description="Recommended settlement payout.")

class ClaimDecision(BaseModel):
    """Final decision regarding an insurance claim."""
    claim_number: str = Field(..., description="The unique identifier for the claim.")
    covered: bool = Field(..., description="Whether the claim is covered by the policy.")
    deductible: float = Field(..., description="The deductible amount to be paid by the claimant.")
    recommended_payout: float = Field(..., description="The final amount recommended for payout.")
    notes: Optional[str] = Field(None, description="Additional notes regarding the decision.") 
