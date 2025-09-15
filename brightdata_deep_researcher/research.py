from flow import DeepResearchFlow
from typing import Dict, Any


async def run_deep_research(prompt):
    """Run the deep research flow and return the result."""
    try:
        flow = DeepResearchFlow()
        flow.state.query = prompt
        payload: Dict[str, Any] = await flow.kickoff_async()
        return str(payload.get("result", "No result returned"))
    except Exception as e:
        return f"An error occurred: {e}"
