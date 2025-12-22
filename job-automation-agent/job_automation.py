import asyncio
import os
from typing import Any
import nest_asyncio
from stagehand import Stagehand, StagehandConfig

nest_asyncio.apply()


def stagehand_browser_automation(
    website_url: str, profile: dict[str, Any], resume_description: str
) -> str:
    """Used to perform job application tasks powered by Stagehand capabilities."""

    async def _execute_automation():
        stagehand = None

        try:
            config = StagehandConfig(
                env="LOCAL",
                model_name="openai/gpt-4.1",
                system_prompt="You are a helpful assistant that can use a web browser to help users fill out job application forms.",
                self_heal=True,
                model_client_options={"apiKey": os.getenv("MODEL_API_KEY")},
                verbose=2,  # 0 = errors only, 1 = info, 2 = debug
            )

            # Initialize - this creates a new session automatically.
            stagehand = Stagehand(config)
            await stagehand.init()

            # Navigate to the job application page
            await stagehand.page.goto(website_url)

            # Act to click on the 'Apply' button
            await stagehand.page.act(
                "Click on the 'Apply' button on the right corner of the page"
            )

            # Fill the form fields
            agent = stagehand.agent(
                provider="google",
                model="gemini-2.5-computer-use-preview-10-2025",
                instructions=f"""You are a helpful assistant that can use a web browser. 
                You are currently on a job application page {website_url} and you are filling out only the required (*) marked details on behalf of the user. 
                You are not allowed to fill out any other details than the required ones marked as asterisk (*).
                Do not ask follow up questions, the user will trust your judgement.""",
                options={"apiKey": os.getenv("GOOGLE_API_KEY")},
            )
            await agent.execute(
                instruction=f"""User comes to know about this job application from "LinkedIn", so select "LinkedIn" as the source of knowledge.
                You are filling out the form fields other than the resume/CV* upload field with the following information: {profile}. 
                For the 'Resume/CV*' upload field, use the 'Enter Manually' option.
                A text box will be provided upon clicking on the 'Enter Manually' option to you right below the button.
                Paste the following complete resume text there in the text box to fill out the resume/CV* upload field:
                {resume_description}""",
                max_steps=40,
                auto_screenshot=True,
            )

            # Submit the application
            await stagehand.page.act(
                "scroll down to the bottom of the page by using side scroll bar and click on the 'Submit application' button"
            )

            return "Job application successfully submitted"

        # If an error occurs, return the error message
        except Exception as error:
            return f"Error during job automation for {website_url}: {str(error)}"

        finally:
            # Always close the session to release resources (browser, connections, etc.)
            if stagehand:
                await stagehand.close()

    # Run async in a sync context - nest_asyncio allows this to work even if called from an existing event loop
    return asyncio.run(_execute_automation())
