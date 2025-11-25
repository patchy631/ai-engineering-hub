import os
import json
from typing import Iterable, List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

from tensorlake.documentai import (
    DocumentAI,
    ParsingOptions,
    ChunkingStrategy,
    TableOutputMode,
    TableParsingFormat,
    StructuredExtractionOptions
)

TENSORLAKE_API_KEY = os.getenv("TENSORLAKE_API_KEY")

RESEARCH_PAPER_SCHEMA = {
    "type": "object",
    "properties": {
        "paper": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "authors": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "abstract": {"type": "string"},
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "key_findings": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "sections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "heading": {"type": "string"},
                            "summary": {"type": "string"}
                        },
                        "required": ["heading", "summary"]
                    }
                }
            },
            "required": ["title", "authors", "abstract", "sections"]
        }
    },
    "required": ["paper"]
}

class TensorLakeClient:
    def __init__(self, api_key: Optional[str] = None):
        self.doc_ai = DocumentAI(api_key=api_key or TENSORLAKE_API_KEY)
    
    def list_uploaded_files(self):
        try:
            files_page = self.doc_ai.files()
            print(f"TensorLake files found: {len(files_page.items)}")
            for file_info in files_page.items:
                print(f"  - {file_info.name} (ID: {file_info.id}, Size: {file_info.file_size} bytes, Type: {file_info.mime_type})")
            return files_page.items
        except Exception as e:
            print(f"Error listing TensorLake files: {e}")
            return []
    
    def verify_file_uploaded(self, file_id: str) -> bool:
        try:
            files = self.list_uploaded_files()
            file_ids = [f.id for f in files]
            exists = file_id in file_ids
            print(f"File ID {file_id} {'exists' if exists else 'NOT FOUND'} in TensorLake")
            return exists
        except Exception as e:
            print(f"Error verifying file {file_id}: {e}")
            return False

    def upload(self, paths: Iterable[str]) -> List[str]:
        print("Files before upload:")
        files_before = self.list_uploaded_files()
        
        file_ids = []
        for path in paths:
            if not os.path.exists(path):
                raise Exception(f"File does not exist: {path}")
            
            file_size = os.path.getsize(path)
            if file_size == 0:
                raise Exception(f"File is empty: {path} (0 bytes)")
            
            print(f"\nUploading file: {path} ({file_size} bytes)")
            
            try:
                fid = self.doc_ai.upload(path=path)
                print(f"Upload successful, file_id: {fid}")
                file_ids.append(fid)
            except Exception as upload_error:
                print(f"Upload failed for {path}: {upload_error}")
                raise
        
        print("\nFiles after upload:")
        files_after = self.list_uploaded_files()
        
        new_files = [f for f in files_after if f not in files_before]
        if new_files:
            print(f"{len(new_files)} new file(s) uploaded:")
            for file_info in new_files:
                print(f"  - {file_info.name} (ID: {file_info.id})")
        else:
            print("No new files detected in TensorLake after upload")
            
        return file_ids

    def parse_structured(
        self,
        file_id: str,
        json_schema: Dict[str, Any],
        *,
        page_range = None,
        labels = None,
        chunking_strategy = ChunkingStrategy.SECTION,
        table_mode = TableOutputMode.MARKDOWN,
        table_format = TableParsingFormat.TSR,
    ) -> str:
        
        print(f"Using chunking strategy: {chunking_strategy}")
        print(f"Using table mode: {table_mode}")
        print(f"Schema name: research_paper")
        
        structured_extraction_options = StructuredExtractionOptions(
            schema_name="research_paper",
            json_schema=json_schema,
            provide_citations=True
        )

        parsing_options = ParsingOptions(
            chunking_strategy=chunking_strategy,
            table_output_mode=table_mode,
            table_parsing_format=table_format,
        )

        if not self.verify_file_uploaded(file_id):
            raise Exception(f"File ID {file_id} not found in TensorLake. Cannot proceed with parsing.")
        
        print(f"Initiating parsing for file_id: {file_id}")
        try:
            parse_id = self.doc_ai.parse(
                file_id,
                page_range=page_range,
                parsing_options=parsing_options,
                structured_extraction_options=structured_extraction_options,
                labels=labels or {}
            )
            print(f"Parsing initiated, parse_id: {parse_id}")
            return parse_id
        except Exception as parse_error:
            print(f"Parsing initiation failed: {parse_error}")
            raise

    def get_result(self, parse_id: str) -> Dict[str, Any]:
        print(f"Waiting for completion of parse_id: {parse_id}")
        result = self.doc_ai.wait_for_completion(parse_id)
        print(f"Parsing completed for parse_id: {parse_id}")
        
        if result:
            if hasattr(result, 'chunks'):
                chunks = result.chunks
                chunk_count = len(chunks) if chunks else 0
                print(f"Number of chunks found: {chunk_count}")
                if chunk_count > 0:
                    print(f"First chunk preview: {chunks[0].content[:100] if hasattr(chunks[0], 'content') else 'No content'}...")
            else:
                print("Result has no 'chunks' attribute")
        else:
            print("Result is None or empty")
            
        return result
        


if __name__ == "__main__":
    client = TensorLakeClient()

    # Upload local documents
    file_ids = client.upload([
        "data/attention-is-all-you-need-Paper.pdf",
    ])

    # Parse each with schema (and produce RAG chunks)
    parse_ids = []
    for fid in file_ids:
        pid = client.parse_structured(
            file_id=fid,
            json_schema=RESEARCH_PAPER_SCHEMA,
            page_range=None,  # parse all pages
        )
        parse_ids.append(pid)

    # Retrieve the parsed result (markdown chunks + schema JSON)
    results = [client.get_result(pid) for pid in parse_ids]

    # collect RAG chunks + structured paper metadata
    rag_chunks, extracted_data = [], []
    for res in results:
        # markdown chunks for retrieval
        for chunk in res.chunks:
            rag_chunks.append({
                "page": chunk.page_number,
                "text": chunk.content,
            })
        # structured extraction schema
        serializable_data = res.model_dump()
        extracted_data.append(serializable_data)
