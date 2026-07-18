import asyncio
from agent import wf  # Import the initialized workflow agent

class QueryProcessor:
    """Handles processing of user queries asynchronously."""

    async def get_response_async(self, message: str) -> str:
        """Runs the workflow and returns the response asynchronously."""
        return await wf.run(message=message)

    def get_response(self, message: str) -> str:
        """Synchronously fetches the response by running the async function inside an event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.get_response_async(message))
