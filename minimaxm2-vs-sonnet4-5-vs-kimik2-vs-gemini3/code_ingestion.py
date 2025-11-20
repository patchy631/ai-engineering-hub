from gitingest import ingest


def ingest_github_repo(repo_url: str) -> dict[str, str]:
    # Validate GitHub URL format
    if not repo_url or not isinstance(repo_url, str):
        raise ValueError("Repository URL must be a non-empty string")
    
    if not repo_url.startswith(("https://github.com/", "http://github.com/")):
        raise ValueError("URL must be a valid GitHub repository URL")

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
        raise Exception(f"Error ingesting repository: {str(e)}") from e
