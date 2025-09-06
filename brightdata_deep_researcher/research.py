from flow import DeepResearchFlow


async def run_deep_research(prompt):
    """Run the deep research flow and return the result."""
    try:
        flow = DeepResearchFlow()
        flow.state.query = prompt
        result = await flow.kickoff_async()
        return result["result"]
    except Exception as e:
        return f"An error occurred: {str(e)}"
