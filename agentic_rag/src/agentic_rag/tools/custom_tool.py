import os
import requests
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field, ConfigDict, PrivateAttr
from markitdown import MarkItDown
from chonkie import SemanticChunker
from qdrant_client import QdrantClient

class DocumentSearchToolInput(BaseModel):
    """Input schema for DocumentSearchTool."""
    query: str = Field(..., description="Query to search the document.")

class DocumentSearchTool(BaseTool):
    name: str = "DocumentSearchTool"
    description: str = "Search the document for the given query."
    args_schema: Type[BaseModel] = DocumentSearchToolInput
    
    model_config = ConfigDict(extra="allow")
    def __init__(self, file_path: str):
        """Initialize the searcher with a PDF file path and set up the Qdrant collection."""
        super().__init__()
        self.file_path = file_path
        self.client = QdrantClient(":memory:")  # For small experiments
        self._process_document()

    def _extract_text(self) -> str:
        """Extract raw text from PDF using MarkItDown."""
        md = MarkItDown()
        result = md.convert(self.file_path)
        return result.text_content

    def _create_chunks(self, raw_text: str) -> list:
        """Create semantic chunks from raw text."""
        chunker = SemanticChunker(
            embedding_model="minishlab/potion-base-8M",
            threshold=0.5,
            chunk_size=512,
            min_sentences=1
        )
        return chunker.chunk(raw_text)

    def _process_document(self):
        """Process the document and add chunks to Qdrant collection."""
        raw_text = self._extract_text()
        chunks = self._create_chunks(raw_text)
        
        docs = [chunk.text for chunk in chunks]
        metadata = [{"source": os.path.basename(self.file_path)} for _ in range(len(chunks))]
        ids = list(range(len(chunks)))

        self.client.add(
            collection_name="demo_collection",
            documents=docs,
            metadata=metadata,
            ids=ids
        )

    def _run(self, query: str) -> list:
        """Search the document with a query string."""
        relevant_chunks = self.client.query(
            collection_name="demo_collection",
            query_text=query
        )
        docs = [chunk.document for chunk in relevant_chunks]
        separator = "\n___\n"
        return separator.join(docs)

class FireCrawlWebSearchToolInput(BaseModel):
    """Input schema for FireCrawlWebSearchTool."""
    query: str = Field(..., description="Query to search the web.")

class FireCrawlWebSearchTool(BaseTool):
    name: str = "WebSearchTool"
    description: str = "Search the open web for the given query."
    args_schema: Type[BaseModel] = FireCrawlWebSearchToolInput
    _api_key: str = PrivateAttr()

    def __init__(self):
        super().__init__()
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY environment variable is not set.")
        self._api_key = api_key

    def _run(self, query: str) -> str:
        """Search Firecrawl and return the scraped Markdown for each result."""
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "query": query,
            "limit": 5,
            "lang": "en",
            "country": "us",
            "scrapeOptions": {"formats": ["markdown"]}
        }
        try:
            response = requests.post(
                "https://api.firecrawl.dev/v1/search",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            results = response.json()
            if not results.get("success"):
                return "Failed to fetch web search results."
            return "\n___\n".join(
                result["markdown"] for result in results.get("data", [])
                if result.get("markdown")
            )
        except requests.exceptions.RequestException as e:
            return f"Failed to fetch web search results: {e}"

# Test the implementation
def test_document_searcher():
    # Test file path
    pdf_path = "/Users/akshaypachaar/Eigen/ai-engineering/agentic_rag/knowledge/dspy.pdf"
    
    # Create instance
    searcher = DocumentSearchTool(file_path=pdf_path)
    
    # Test search
    result = searcher._run("What is the purpose of DSpy?")
    print("Search Results:", result)

if __name__ == "__main__":
    test_document_searcher()
