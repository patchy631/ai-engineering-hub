import os
from stagehand import Stagehand, StagehandConfig

import nest_asyncio
import asyncio

# Allow nested loops in async (for environments like Jupyter or already-running loops)
nest_asyncio.apply()


def browser_automation(task_description: str, website_url: str) -> str:
    """Performs automated browser tasks using AI agent capabilities."""

    async def _execute_automation():
        stagehand = None

        try:
            config = StagehandConfig(
                env="LOCAL",
                model_name="gpt-4o",
                self_heal=True,
                system_prompt="You are a browser automation assistant that helps users navigate websites effectively.",
                model_client_options={"apiKey": os.getenv("MODEL_API_KEY")},
                verbose=1,
            )

            stagehand = Stagehand(config)
            await stagehand.init()

            agent = stagehand.agent(
                model="computer-use-preview",
                provider="openai",
                instructions="You are a helpful web navigation assistant that helps users find information. Do not ask follow-up questions.",
                options={"apiKey": os.getenv("MODEL_API_KEY")},
            )

            await stagehand.page.goto(website_url)

            agent_result = await agent.execute(
                instruction=task_description,
                max_steps=20,
                auto_screenshot=True,
            )

            result_message = (
                agent_result.message or "No specific result message was provided."
            )
            return f"Browser Automation Tool result:\n{result_message}"

        finally:
            if stagehand:
                await stagehand.close()

    # Run async in a sync context
    return asyncio.run(_execute_automation())