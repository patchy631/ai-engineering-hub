from flow import ResumeOptimizerFlow, ResumeOptimizerState
from pathlib import Path


async def optimize_resume_async(
    resume_path: str,
    job_url: str,
    output_dir: str = "output",
    tone: str = "neutral",
    must_keep_sections: list = None,
) -> ResumeOptimizerState:
    """Async helper function to run the resume optimization flow."""
    # Create flow instance
    flow = ResumeOptimizerFlow()

    # Set initial state
    flow.state.resume_path = resume_path
    flow.state.job_url = job_url
    flow.state.output_dir = output_dir
    flow.state.output_path = Path(output_dir) / "optimized_resume.txt"
    flow.state.tone = tone
    flow.state.must_keep_sections = must_keep_sections or []

    # Run flow asynchronously
    await flow.kickoff_async()

    return flow.state


if __name__ == "__main__":
    import asyncio

    asyncio.run(
        optimize_resume_async(
            resume_path="software-engineer-resume.docx",
            job_url="https://job-boards.greenhouse.io/deepmind/jobs/7236032",
        )
    )
