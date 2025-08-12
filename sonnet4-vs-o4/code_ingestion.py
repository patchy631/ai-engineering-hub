from gitingest import ingest
from typing import Dict, Any

def ingest_github_repo(repo_url: str):
    try:
        # Use gitingest to process the repository
        summary, structure, content = ingest(repo_url)

        context = {
            "summary": summary,
            "structure": structure,
            "content": content
        }
        
        return context
        
    except Exception as e:
        raise Exception(f"Error ingesting repository: {str(e)}") 