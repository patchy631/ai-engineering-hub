import json
import logging
import os
from typing import Any, Dict, List, Literal, Optional

from crewai import Agent, Crew, LLM, Task
from crewai.flow.flow import Flow, listen, start
from crewai_tools import MCPServerAdapter
from dotenv import load_dotenv
from mcp import StdioServerParameters
from pydantic import BaseModel, Field, HttpUrl

load_dotenv()


# ---------- Pydantic Schemas ----------
Platform = Literal["instagram", "linkedin", "youtube", "x", "web"]


class URLBuckets(BaseModel):
    instagram: List[str] = Field(default_factory=list)
    linkedin: List[str] = Field(default_factory=list)
    youtube: List[str] = Field(default_factory=list)
    x: List[str] = Field(default_factory=list)
    web: List[str] = Field(default_factory=list)


class SpecialistOutput(BaseModel):
    platform: Platform
    url: str
    summary: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ---------- Flow State ----------
class DeepResearchFlowState(BaseModel):
    query: str = ""
    final_response: Optional[str] = None


# ---------- MCP Server Configurations ----------
def server_params() -> StdioServerParameters:
    token = os.getenv("BRIGHT_DATA_API_TOKEN")
    if not token:
        raise RuntimeError("BRIGHT_DATA_API_TOKEN is not set")
    return StdioServerParameters(
        command="npx",
        args=["@brightdata/mcp"],
        env={"API_TOKEN": token, "PRO_MODE": "true"},
    )


# ---------- Flow Definition ----------
class DeepResearchFlow(Flow[DeepResearchFlowState]):
    search_llm: Any = LLM(model="openai/gpt-4o", temperature=0.0)
    specialist_llm: Any = LLM(model="openai/o3-mini", temperature=0.1)
    response_llm: Any = LLM(model="ollama/gpt-oss", temperature=0.3)

    @start()
    def start_flow(self) -> Dict[str, Any]:
        """Start the flow by setting the query in the state."""
        # Entry: state.query already populated by caller
        return {"query": self.state.query}

    @listen(start_flow)
    def collect_urls(self) -> Dict[str, Any]:
        """Search web for user query and return URLBuckets object."""
        try:
            with MCPServerAdapter(server_params()) as mcp_tools:
                search_agent = Agent(
                    role="Multiplatform Web Discovery Specialist",
                    goal=(
                        "Your objective is to identify and return a well-organized JSON object containing only public, directly relevant links for a given user query. "
                        "The links should be grouped by platform: Instagram, LinkedIn, YouTube, X (formerly Twitter), and the open web."
                    ),
                    backstory=(
                        "You are an expert web researcher skilled in using advanced search operators and platform-specific techniques. "
                        "You rigorously verify that every link is public, accessible, and highly relevant to the query. "
                        "You never include duplicates or irrelevant results, and you never fabricate information. "
                        "If no suitable links are found for a platform, you return an empty list for that platform. "
                        "Your output is always precise, clean, and strictly follows the required schema."
                    ),
                    tools=[mcp_tools["search_engine"]],
                    llm=self.search_llm,
                )

                search_task = Task(
                    description=f"""
You are collecting public URLs for this query: "{self.state.query}".

Return ONLY a JSON object matching the URLBuckets schema with EXACT keys:
["instagram","linkedin","youtube","x","web"], each a list of HTTPS URLs.

Classification rules (strict):
- instagram:       instagram.com/*
- linkedin:        linkedin.com/*
- youtube:         youtube.com/*
- x:               x.com/* or twitter.com/*
- web:             only web pages that opens to an article or blog post (exclude the above domains and landing pages)

Quality + validity:
- No duplicates within or across lists.
- Cap each list at 3 URLs, ordered by likely usefulness.

If a platform yields nothing, return an empty list [] for that key.
Output must be pure JSON, no code fences, no commentary.

Example shape (not a template):
{{"instagram":[], "linkedin":[], "youtube":[], "x":[], "web":[]}}
""",
                    agent=search_agent,
                    output_pydantic=URLBuckets,  # Enforces the schema
                    expected_output="Strict JSON for URLBuckets. No extra text or formatting.",
                )

                crew = Crew(agents=[search_agent], tasks=[search_task], verbose=True)
                out: URLBuckets = crew.kickoff()
                return {"urls_buckets": out.model_dump(mode="raw")}

        except Exception as e:
            logging.exception("collect_urls failed")
            empty = URLBuckets().model_dump(mode="raw")
            return {"urls_buckets": empty, "error": f"{e}"}

    @listen(collect_urls)
    def dispatch_to_specialists(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Fan-out to platform specialists. Each platform is processed independently."""
        results: List[SpecialistOutput] = []

        # Helper to process a single platform bucket
        def _process_platform(
            platform: Platform, urls: List[HttpUrl]
        ) -> List[SpecialistOutput]:
            # Check if no URLs are provided
            if not urls:
                # Skip the function if no URLs are provided
                return []

            with MCPServerAdapter(server_params()) as mcp_tools:
                tools_map: Dict[str, List[Any]] = {
                    "instagram": [mcp_tools["web_data_instagram_posts"]],
                    "linkedin": [mcp_tools["web_data_linkedin_posts"]],
                    "youtube": [mcp_tools["web_data_youtube_videos"]],
                    "x": [mcp_tools["web_data_x_posts"]],
                    "web": [mcp_tools["scrape_as_markdown"]],
                }

                specialist_research_agent = Agent(
                    role=f"{platform.capitalize()} Specialist Research Agent",
                    goal=(
                        f"You are a {platform.capitalize()} deep content analysis/research specialist. "
                        f"Given one or more public {platform} URLs, your task is to extract high-signal facts, "
                        "insights, and key information from the content. "
                        "For each URL, return a strictly valid object (no extra attributes, no commentary) matching the output schema."
                    ),
                    backstory=(
                        "You operate with deep-research rigor and platform expertise. "
                        "Never speculate or infer beyond what is directly available. "
                        "Prioritize accuracy, clarity, and completeness in your extraction, and always adhere to the output schema."
                    ),
                    tools=tools_map[platform],
                    llm=self.specialist_llm,
                )

                # One task per URL to keep outputs atomic and typed
                specialist_research_task = Task(
                    description=f"""
Process this {platform} URL: {urls}

Requirements:
- Use the provided tools to fetch content only.
- Summarize in bullet points ~500-750 words total (avoid fluff).
- Do not fabricate fields; leave unknowns out.

Output:
- Return ONLY valid JSON matching SpecialistOutput schema:
  {{ "platform": "{platform}", "url": "<canonical_url>", "summary": "<summary>", "metadata": {{...}} }}
""",
                    agent=specialist_research_agent,
                    output_pydantic=SpecialistOutput,
                    expected_output="Strict JSON for SpecialistOutput; no prose, no code fences.",
                )

                crew = Crew(
                    agents=[specialist_research_agent],
                    tasks=[specialist_research_task],
                    verbose=True,
                )
                platform_output: List[SpecialistOutput] = crew.kickoff()
                return platform_output

        # Process each platform bucket with clear failure isolation
        url_buckets_dict = (
            json.loads(inputs["urls_buckets"]["raw"])
            if isinstance(inputs["urls_buckets"]["raw"], str)
            else inputs["urls_buckets"]["raw"]
        )

        for platform, bucket in url_buckets_dict.items():
            try:
                platform_output = _process_platform(platform, bucket)
                results.append(platform_output)
            except Exception as e:
                logging.exception(f"{platform} specialist failed")
                results.append(
                    SpecialistOutput(
                        platform=platform,
                        url="https://invalid.local",
                        summary=f"Error: {type(e).__name__}",
                        metadata={"detail": str(e)},
                    )
                )

        # Flatten the results list and filter out empty results
        flattened_results = []
        for result in results:
            if isinstance(result, list):
                flattened_results.extend(result)
            elif result:  # Non-empty result
                flattened_results.append(result)

        return {"specialist_results": flattened_results}

    @listen(dispatch_to_specialists)
    def synthesize_response(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Final deep research response synthesis."""
        response_agent = Agent(
            role="Deep Research Synthesis Specialist",
            goal=(
                "Synthesize comprehensive research findings into a clear, engaging, and informative response "
                "that answers the user's query with depth and accuracy. Present findings in a structured, "
                "easy-to-read format similar to ChatGPT's deep research mode."
            ),
            backstory=(
                "You are an expert research analyst with deep expertise in synthesizing complex information "
                "from multiple sources. You excel at creating comprehensive, well-structured responses that "
                "provide users with actionable insights while maintaining clarity and engagement."
            ),
            llm=self.response_llm,
        )

        response_task = Task(
            description=f"""
Original Query: "{self.state.query}"

Research Context:
{inputs["specialist_results"]}

Your Task:
Create a comprehensive, well-structured markdown response that:

1. **Directly answers the user's query** with clear, actionable insights
2. **Synthesizes findings** from all available sources into coherent themes
3. **Provides specific details** with supporting evidence from sources
4. **Uses clear headings** and bullet points for easy scanning
5. **Includes source links** where applicable for credibility
6. **Highlights key takeaways** and important implications
7. **Maintains an engaging tone** while being informative

Structure your response with:
- Executive Summary (2-3 key points)
- Detailed Findings (organized by topic/theme)
- Key Insights & Implications
- Sources & References

Make it comprehensive yet readable, similar to high-quality research reports or ChatGPT's or Gemini's deep research mode.
""",
            expected_output="Comprehensive markdown response with clear structure, detailed findings, and source references.",
            agent=response_agent,
            markdown=True,
        )

        crew = Crew(agents=[response_agent], tasks=[response_task], verbose=True)
        final_md: str = crew.kickoff()
        self.state.final_response = str(final_md)
        return {"result": self.state.final_response}


# Usage example
async def main():
    flow = DeepResearchFlow()
    flow.state.query = "What is the latest update on iphone 17 launch?"
    result = await flow.kickoff_async()

    print(f"\n{'='*50}")
    print(f"FINAL RESULT")
    print(f"{'='*50}")
    print(result["result"])


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
