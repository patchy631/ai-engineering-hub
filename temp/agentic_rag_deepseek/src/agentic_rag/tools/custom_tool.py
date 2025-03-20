import os
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field, ConfigDict
from groundx import Document, GroundX
from dotenv import load_dotenv

load_dotenv()


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
        self.client = GroundX(
            api_key=os.getenv("GROUNDX_API_KEY")
        )  
        self.bucket_id = self._create_bucket()
        self.process_id = self._upload_document()
    
    def _upload_document(self):
        ingest = self.client.ingest(
                        documents=[
                            Document(
                            bucket_id=self.bucket_id,
                            file_name=os.path.basename(self.file_path),
                            file_path=self.file_path,
                            file_type="pdf",
                            search_data=dict(
                                key = "value",
                            ),
                            )
                        ]
                        )
        return ingest.ingest.process_id
    
    def _create_bucket(self):
        response = self.client.buckets.create(
            name="agentic_rag"
        )
        return response.bucket.bucket_id    

    def _run(self, query: str) -> str:
        # Check processing status
        status_response = self.client.documents.get_processing_status_by_id(
            process_id=self.process_id
        )
        
        # Check if processing is complete
        if status_response.ingest.status != "complete":
            return "Document is still being processed..."
            
        # If processing is complete, proceed with search
        search_response = self.client.search.content(
            id=self.bucket_id,
            query=query,
            n=10,
            verbosity=2
        )
        
        # Format the results with separators
        formatted_results = ""
        for result in search_response.search.results:
            formatted_results += f"{result.text}\n____\n"
        
        return formatted_results.rstrip('____\n')

# Test the implementation
def test_document_searcher():
    # Test file path
    pdf_path = "/Users/akshay/Eigen/ai-engineering-hub/agentic_rag_deepseek/knowledge/dspy.pdf"
    
    # Create instance
    searcher = DocumentSearchTool(file_path=pdf_path)
    
    # Test search
    result = searcher._run("What is the purpose of DSpy?")
    print("Search Results:", result)

if __name__ == "__main__":
    test_document_searcher()
