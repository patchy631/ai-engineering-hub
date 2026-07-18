from typing import List, Optional
from pydantic import BaseModel, Field

class ClaimInfo(BaseModel):
    """
    Input Claim Information schema by the Claim Adjuster.
    Extracted Insurance claim information.
    """
    claim_number: str
    policy_number: str
    claimant_name: str
    date_of_loss: str
    loss_description: str
    estimated_repair_cost: float
    vehicle_details: Optional[str] = None

class PolicyQueries(BaseModel):
    """
    Policy Conditions and Policy Queries.
    Defining the schema to generate guideline queries and for storing recommendations.
    """
    queries: List[str] = Field(
        default_factory=list,
        description="A list of query strings to retrieve relevant policy sections."
    )

class PolicyRecommendation(BaseModel):
    """
    Guideline/Policy recommendation schema.
    Policy recommendation regarding a given claim.
    """
    covered: bool = Field(..., description="Whether the claim is covered by the policy")
    policy_section: str = Field(..., description="The policy section or clause that applies.")
    recommendation_summary: str = Field(..., description="A concise summary of coverage determination.")
    deductible: Optional[float] = Field(None, description="The applicable deductible amount.")
    settlement_amount: Optional[float] = Field(None, description="Recommended settlement payout.")

class ClaimDecision(BaseModel):
    """
    Final Claim Decision schema.
    Claim decision information for a given claim.
    """
    claim_number: str
    covered: bool
    deductible: float
    recommended_payout: float
    notes: Optional[str] = None