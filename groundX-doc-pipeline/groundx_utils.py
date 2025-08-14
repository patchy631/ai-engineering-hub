import os
import tempfile
import time
import requests
from pathlib import Path
from typing import Any, Dict, Optional

import streamlit as st
from groundx import GroundX, Document
from dotenv import load_dotenv

# Load environment configuration
load_dotenv()
API_KEY: Optional[str] = os.getenv("GROUNDX_API_KEY")

# Ground X API Utility Functions
@st.cache_resource(show_spinner=False)
def create_client() -> GroundX:
    """Initialize and return a Ground X API client instance"""
    if not API_KEY:
        raise ValueError("No `GROUNDX_API_KEY` found in secrets, .env, or environment.")
    return GroundX(api_key=API_KEY)

@st.cache_resource(show_spinner=False)
def ensure_bucket(_gx: GroundX, name: str = "gx_demo") -> str:
    """Ensure storage bucket exists and return its identifier"""
    buckets_response = _gx.buckets.list()
    if buckets_response.buckets:
        for bucket in buckets_response.buckets:
            if bucket.name == name:
                return bucket.bucket_id
    
    create_response = _gx.buckets.create(name=name)
    return create_response.bucket.bucket_id

def ingest_document(gx: GroundX, bucket_id: str, path: Path, mime: str) -> str:
    """Upload and process document in Ground X, return processing identifier"""
    bucket_id_int = int(bucket_id) if isinstance(bucket_id, str) else bucket_id
    
    ingest = gx.ingest(
        documents=[
            Document(
                bucket_id=bucket_id_int,
                file_name=path.name,
                file_path=str(path),
                file_type=mime.split("/")[-1],
            )
        ]
    )
    return ingest.ingest.process_id

def poll_until_complete(gx: GroundX, process_id: str, timeout: int = 600) -> None:
    """Monitor document processing status until completion"""
    start_time = time.time()
    status_text = st.empty()
    progress_bar = st.progress(0)

    while True:
        status = gx.documents.get_processing_status_by_id(process_id=process_id).ingest
        
        progress_value = 0
        if hasattr(status, 'percent') and status.percent is not None:
            try:
                progress_value = int(status.percent)
            except (ValueError, TypeError):
                progress_value = 0
        elif hasattr(status, 'progress') and status.progress is not None:
            try:
                if hasattr(status.progress, 'percent'):
                    progress_value = int(status.progress.percent)
                elif hasattr(status.progress, 'value'):
                    progress_value = int(status.progress.value)
                elif hasattr(status.progress, 'percentage'):
                    progress_value = int(status.progress.percentage)
                else:
                    progress_value = int(status.progress)
            except (ValueError, TypeError, AttributeError):
                progress_value = 0
        elif hasattr(status, 'percentage') and status.percentage is not None:
            try:
                progress_value = int(status.percentage)
            except (ValueError, TypeError):
                progress_value = 0
        
        progress_bar.progress(progress_value)
        
        status_display = f"**{status.status.capitalize()}**"
        if progress_value > 0:
            status_display += f" – {progress_value}%"
        status_text.write(status_display)

        if status.status in {"complete", "error", "cancelled"}:
            break
        if time.time() - start_time > timeout:
            raise TimeoutError("Ground X ingest timed out.")
        time.sleep(3)

    if status.status != "complete":
        raise RuntimeError(f"Ingest finished with status: {status.status!r}")

def fetch_xray_json(gx: GroundX, bucket_id: str) -> Dict[str, Any]:
    """Retrieve X-Ray analysis data for documents in storage bucket"""
    documents = gx.documents.lookup(id=bucket_id).documents
    if not documents:
        raise RuntimeError("No documents found in bucket after ingest.")
    
    document = documents[0]
    if hasattr(document, 'xray_url') and document.xray_url:
        response = requests.get(document.xray_url)
        response.raise_for_status()
        return response.json()
    else:
        raise RuntimeError("No X-Ray URL available for this document")

def check_file_exists(gx: GroundX, bucket_id: str, file_name: str) -> Optional[str]:
    """Verify document existence in bucket and return document identifier"""
    documents = gx.documents.lookup(id=bucket_id).documents
    for doc in documents:
        if doc.file_name == file_name:
            return doc.document_id
    return None

def get_xray_for_existing_document(gx: GroundX, document_id: str, bucket_id: str) -> Dict[str, Any]:
    """Retrieve X-Ray analysis data for existing document"""
    # Get the document to access its xray_url
    documents = gx.documents.lookup(id=bucket_id).documents
    for doc in documents:
        if doc.document_id == document_id:
            if hasattr(doc, 'xray_url') and doc.xray_url:
                response = requests.get(doc.xray_url)
                response.raise_for_status()
                return response.json()
            else:
                raise RuntimeError("No X-Ray URL available for this document")
    
    raise RuntimeError(f"Document with ID {document_id} not found")

def process_document(gx: GroundX, bucket_id: str, file_to_process: Any, file_path: str) -> tuple[Dict[str, Any], bool]:
    """Process document through Ground X pipeline and return analysis data
    
    Args:
        gx: Ground X client instance
        bucket_id: Storage bucket identifier
        file_to_process: File object with name and type attributes
        file_path: Path to the file on disk
        
    Returns:
        Tuple of (xray_data, used_existing_file)
    """
    existing_doc_id = check_file_exists(gx, bucket_id, file_to_process.name)
    
    if existing_doc_id:
        # Retrieve analysis for existing document
        return get_xray_for_existing_document(gx, existing_doc_id, bucket_id), True
    else:
        # Process new document through ingestion pipeline
        process_id = ingest_document(gx, bucket_id, Path(file_path), file_to_process.type)
        poll_until_complete(gx, process_id)
        return fetch_xray_json(gx, bucket_id), False
