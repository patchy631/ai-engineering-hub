import nest_asyncio
nest_asyncio.apply()

from documentation_flow import CreateDocumentationFlow

def run_doc_flow(repo_url: str) -> list[str]:
    flow = CreateDocumentationFlow()
    result = flow.kickoff(inputs={"project_url": repo_url})
    return result

if __name__ == "__main__":
    repo_url = input("Enter the GitHub repository: ")
    run_doc_flow(repo_url)