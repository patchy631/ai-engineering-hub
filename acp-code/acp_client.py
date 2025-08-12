import asyncio
from acp_sdk.client import Client

async def run_workflow() -> None:
    async with Client(base_url="http://localhost:8000") as drafter, \
        Client(base_url="http://localhost:8001") as verifier:
        topic = "Impact of climate change on agriculture in 2025."
        
        response1 = await drafter.run_sync(
            agent="research_drafter",
            input=topic
        )
        draft = response1.output[0].parts[0].content
        print(f"\nDraft Summary:\n{draft}")

        response2 = await verifier.run_sync(
            agent="research_verifier",
            input=f"Enhance the following research summary using the latest information available online providing a more accurate and updated version:\n{draft}"
        )
        final_summary = response2.output[0].parts[0].content
        print(f"\nVerified & Enriched Summary:\n{final_summary}")

if __name__ == "__main__":
    asyncio.run(run_workflow())