from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from firecrawl import FirecrawlApp
from config.settings import settings
import os

class FirecrawlSearchInput(BaseModel):
    """Input schema for Firecrawl web search tool"""
    query: str = Field(..., description="The search query to look up on the web.")
    limit: int = Field(..., description="Maximum number of results to fetch.")

class FirecrawlSearchTool(BaseTool):
    name: str = "Firecrawl Web Search"
    description: str = (
        "Search the web using Firecrawl and return a concise list of results "
        "(title, URL, and short description snippet)."
    )
    args_schema: Type[BaseModel] = FirecrawlSearchInput

    def _run(self, query: str, limit: int = 3) -> str:
        api_key = settings.firecrawl_api_key or os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            return "Web search unavailable - API not configured."

        try:
            app = FirecrawlApp(api_key=api_key)
            response = app.search(query, limit=limit)
            results_list = getattr(response, "data", None)

            if not isinstance(results_list, list) or not results_list:
                return "No relevant web search results found."

            search_contents= []
            for result in results_list:
                if not isinstance(result, dict):
                    continue
                url = result.get("url", "No URL")
                title = result.get("title", "No title")
                description = (result.get("description") or "").strip()
                snippet = description[:1000] if description else "[no description available]"
                search_contents.append(f"Title: {title}\nURL: {url}\nContent: {snippet}")

            return "\n\n---\n\n".join(search_contents) if search_contents else "No relevant web search results found."
        except Exception as e:
            return f"Web search unavailable due to technical issues: {e}"


