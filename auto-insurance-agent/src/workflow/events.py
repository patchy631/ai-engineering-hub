from llama_index.core.workflow import Event
from ..models.schemas import ClaimInfo, PolicyQueries, PolicyRecommendation, ClaimDecision

class ClaimInfoEvent(Event):
    """Event containing extracted insurance claim information."""
    claim_info: ClaimInfo

class PolicyQueryEvent(Event):
    """Event containing queries to retrieve relevant policy sections."""
    queries: PolicyQueries

class PolicyMatchedEvent(Event):
    """Event containing the matched policy text from retrieval."""
    policy_text: str

class RecommendationEvent(Event):
    """Event containing the policy recommendation for a claim."""
    recommendation: PolicyRecommendation

class DecisionEvent(Event):
    """Event containing the final decision for a claim."""
    decision: ClaimDecision

class LogEvent(Event):
    """Event for logging messages during workflow execution."""
    msg: str
    delta: bool = False 
