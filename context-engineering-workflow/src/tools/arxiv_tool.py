import json
import requests
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class ArxivAPIInput(BaseModel):
    """Input schema for ArXiv API tool"""
    query: str = Field(..., description="The research query to search for papers.")
    search_field: str = Field(default="all", description="Field to search in: 'all', 'title', 'author', 'abstract', 'category'")
    category: Optional[str] = Field(default=None, description="ArXiv category filter (e.g., 'cs.AI', 'stat.ML', 'physics')")
    author: Optional[str] = Field(default=None, description="Author name to filter by")
    max_results: int = Field(default=5, description="Maximum number of papers to return (1-50)")


class ArxivTool(BaseTool):
    name: str = "arxiv_search"
    description: str = "Search ArXiv for academic papers related to your research query. Can filter by category, author, and search specific fields."
    args_schema: Type[BaseModel] = ArxivAPIInput
    
    def _run(self, query: str, search_field: str = "all", category: Optional[str] = None, 
             author: Optional[str] = None, max_results: int = 5) -> str:
        try:
            # Build ArXiv query
            search_query = self._build_arxiv_query(query, search_field, category, author)
            
            # ArXiv API endpoint
            base_url = "http://export.arxiv.org/api/query"
            params = {
                "search_query": search_query,
                "start": 0,
                "max_results": max_results,
                "sortBy": "relevance",
                "sortOrder": "descending"
            }
            
            # Make API request
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse XML response
            papers = self._parse_arxiv_response(response.text)
            
            if not papers:
                return json.dumps({
                    "status": "INSUFFICIENT_CONTEXT",
                    "source_used": "ARXIV",
                    "answer": f"No papers found for query: '{query}'",
                    "citations": [],
                    "confidence": 0.0,
                    "search_parameters": {
                        "query": query,
                        "search_field": search_field,
                        "category": category,
                        "author": author,
                        "max_results": max_results
                    }
                })

            answer_parts = []
            citations = []
            for i, paper in enumerate(papers):
                answer_parts.append(
                    f"**{i+1}. {paper['title']}**\n"
                    f"Authors: {paper['authors']}\n"
                    f"Category: {paper['category']}\n"
                    f"Published: {paper['published']}\n"
                    f"Abstract: {paper['abstract'][:300]}...\n"
                    f"URL: {paper['url']}"
                )
                
                citations.append({
                    "label": f"{paper['title']} ({paper['published']})",
                    "locator": paper['url']
                })
            
            answer = f"Found {len(papers)} relevant papers:\n\n" + "\n\n---\n\n".join(answer_parts)
            
            return json.dumps({
                "status": "OK",
                "source_used": "ARXIV",
                "answer": answer,
                "citations": citations,
                "confidence": 0.92,
                "search_parameters": {
                    "query": query,
                    "search_field": search_field,
                    "category": category,
                    "author": author,
                    "max_results": max_results
                },
                "papers_found": len(papers)
            })
            
        except Exception as e:
            return json.dumps({
                "status": "ERROR",
                "source_used": "ARXIV",
                "answer": f"ArXiv search failed: {str(e)}",
                "citations": [],
                "confidence": 0.0,
                "error": str(e)
            })
    
    def _build_arxiv_query(self, query: str, search_field: str, category: Optional[str], author: Optional[str]) -> str:
        parts = []
        if search_field == "title":
            parts.append(f'ti:"{query}"')
        elif search_field == "author":
            parts.append(f'au:"{query}"')
        elif search_field == "abstract":
            parts.append(f'abs:"{query}"')
        elif search_field == "category":
            parts.append(f'cat:"{query}"')
        else:  # search_field == "all"
            parts.append(f'all:"{query}"')
        
        if category:
            parts.append(f'cat:{category}')
        if author:
            parts.append(f'au:"{author}"')
        
        return " AND ".join(parts)
    
    def _parse_arxiv_response(self, xml_content: str) -> List[Dict[str, Any]]:
        try:
            root = ET.fromstring(xml_content)
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            papers = []
            entries = root.findall('atom:entry', namespaces)
            for entry in entries:
                title = entry.find('atom:title', namespaces)
                title_text = title.text.strip().replace('\n', ' ') if title is not None else "No title"
                
                authors = []
                author_elements = entry.findall('atom:author', namespaces)
                for author in author_elements:
                    name = author.find('atom:name', namespaces)
                    if name is not None:
                        authors.append(name.text)
                authors_text = ", ".join(authors) if authors else "Unknown authors"
                
                summary = entry.find('atom:summary', namespaces)
                abstract = summary.text.strip().replace('\n', ' ') if summary is not None else "No abstract"
                
                link = entry.find('atom:id', namespaces)
                url = link.text if link is not None else ""
                
                published = entry.find('atom:published', namespaces)
                pub_date = published.text[:10] if published is not None else "Unknown date"
                
                category_elem = entry.find('arxiv:primary_category', namespaces)
                if category_elem is None:
                    category_elem = entry.find('atom:category', namespaces)
                category = category_elem.get('term') if category_elem is not None else "Unknown category"
                
                papers.append({
                    "title": title_text,
                    "authors": authors_text,
                    "abstract": abstract,
                    "url": url,
                    "published": pub_date,
                    "category": category
                })
            
            return papers
            
        except ET.ParseError as e:
            raise Exception(f"Failed to parse ArXiv XML response: {e}")
        except Exception as e:
            raise Exception(f"Error processing ArXiv response: {e}")
