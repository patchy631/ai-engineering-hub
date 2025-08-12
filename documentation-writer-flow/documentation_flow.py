import subprocess
from shutil import rmtree
from typing import List
from pathlib import Path
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start
from utils import remove_readonly
from crew import initialize_planning_crew, initialize_documentation_crew

class DocumentationState(BaseModel):
    """
    State for the documentation flow
    """
    project_url: str = ""
    repo_path: Path = "workdir"
    docs: List[str] = []

class CreateDocumentationFlow(Flow[DocumentationState]):
    # Clone the repository, initial step
    @start()
    def clone_repo(self):
        print(f"# Cloning repository: {self.state.project_url}\n")
        # Extract repo name from URL
        repo_name = self.state.project_url.split("/")[-1]
        self.state.repo_path = f"{self.state.repo_path}/{repo_name}"

        # Check if directory exists
        if Path(self.state.repo_path).exists():
            print(f"# Repository directory already exists at {self.state.repo_path}\n")
            # subprocess.run(["rm", "-rf", self.state.repo_path])
            rmtree(self.state.repo_path, onexc=remove_readonly)
            print("# Removed existing directory\n")

        # Clone the repository
        subprocess.run(["git", "clone", self.state.project_url, self.state.repo_path], check=True)
        return self.state

    @listen(clone_repo)
    def plan_docs(self):
        print(f"# Planning documentation for: {self.state.repo_path}\n")
        planning_crew = initialize_planning_crew()
        result = planning_crew.kickoff(inputs={'repo_path': self.state.repo_path})
        print(f"# Planned docs for {self.state.repo_path}:")
        for doc in result.pydantic.docs:
            print(f"    - {doc.title}")
        return result

    @listen(plan_docs)
    def save_plan(self, plan):
        docs_dir = Path("docs")
        if docs_dir.exists():
            rmtree(docs_dir, onexc=remove_readonly)
        docs_dir.mkdir(exist_ok=True)
        with open(docs_dir / "plan.json", "w") as f:
            f.write(plan.raw)

    @listen(plan_docs)
    def create_docs(self, plan):
        for doc in plan.pydantic.docs:
            print(f"\n# Creating documentation for: {doc.title}")
            documentation_crew = initialize_documentation_crew()
            result = documentation_crew.kickoff(inputs={
                'repo_path': self.state.repo_path,
                'title': doc.title,
                'overview': plan.pydantic.overview,
                'description': doc.description,
                'prerequisites': doc.prerequisites,
                'examples': '\n'.join(doc.examples),
                'goal': doc.goal
            })

            # Save documentation to file in docs folder
            docs_dir = Path("docs")
            docs_dir.mkdir(exist_ok=True)
            title = doc.title.lower().replace(" ", "_") + ".mdx"
            self.state.docs.append(str(docs_dir / title))
            with open(docs_dir / title, "w") as f:
                f.write(result.raw)
        print(f"\n# Documentation created for: {self.state.repo_path}")
        return self.state.docs