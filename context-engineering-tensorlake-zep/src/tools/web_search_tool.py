import os
import json
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from firecrawl import Firecrawl

class WebSearchInput(BaseModel):
    """Input schema for web search tool"""
    query: str = Field(..., description="The search query for web search.")
    limit: int = Field(default=3, description="Maximum number of search results to return.")

class FirecrawlSearchTool(BaseTool):
    name: str = "firecrawl_web_search"
    description: str = "Search the web for recent information and developments on research topics"
    api_key: str = Field(..., description="Firecrawl API key")
    args_schema: Type[BaseModel] = WebSearchInput
    
    def _run(self, query: str, limit: int = 3) -> str:
        try:
            if not self.api_key:
                return json.dumps({
                    "status": "ERROR",
                    "source_used": "WEB",
                    "answer": "Web search unavailable - API key not configured.",
                    "citations": [],
                    "confidence": 0.0,
                    "error": "Missing API key"
                })

            # Initialize Firecrawl app and perform search
            app = Firecrawl(api_key=self.api_key)
            response = app.search(query, limit=limit)
            results_list = getattr(response, "web", None)

            if not isinstance(results_list, list) or not results_list:
                return json.dumps({
                    "status": "INSUFFICIENT_CONTEXT",
                    "source_used": "WEB",
                    "answer": "No relevant web search results found.",
                    "citations": [],
                    "confidence": 0.0,
                    "search_results": []
                })

            search_results = []
            citations = []
            for result in results_list:
                try:
                    title = getattr(result, "title", "No title") or "No title"
                    url = getattr(result, "url", "") or ""
                    content = getattr(result, "description", "") or ""
                    category = getattr(result, "category", None)
                    
                    # Truncate content for readability
                    snippet = content[:1000] + "..." if len(content) > 1000 else content
                    if not snippet:
                        snippet = "[no description available]"
                    
                    search_results.append({
                        "title": title,
                        "url": url,
                        "content": snippet,
                        "category": category
                    })
                    
                    citations.append({
                        "label": title,
                        "locator": url
                    })
                    
                except Exception as e:
                    continue

            if search_results:
                answer_parts = []
                for result in search_results:
                    answer_parts.append(
                        f"**{result['title']}**\n"
                        f"URL: {result['url']}\n"
                        f"Content: {result['content'][:500]}..."
                    )
                
                answer = "\n\n---\n\n".join(answer_parts)
                return json.dumps({
                    "status": "OK",
                    "source_used": "WEB",
                    "answer": answer,
                    "citations": citations,
                    "confidence": 0.97,
                    "search_results": search_results
                })
            else:
                return json.dumps({
                    "status": "INSUFFICIENT_CONTEXT",
                    "source_used": "WEB",
                    "answer": "No relevant web search results found.",
                    "citations": [],
                    "confidence": 0.0,
                    "search_results": []
                })
                
        except Exception as e:
            return json.dumps({
                "status": "ERROR",
                "source_used": "WEB",
                "answer": f"Web search unavailable due to technical issues: {str(e)}",
                "citations": [],
                "confidence": 0.0,
                "error": str(e)
            })