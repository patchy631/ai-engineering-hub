import re
import os
import stat
import yaml
from crewai import LLM
from crewai.tasks import TaskOutput

# Load YAML configurations
def load_yaml_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

# Initialize LLM
def load_llm():
    llm = LLM(
        model="ollama/deepseek-r1:7b",
        base_url="http://localhost:11434"
    )
    return llm

# Check for mermaid syntax
def check_mermaid_syntax(task_output: TaskOutput):
    text = task_output.raw
    mermaid_blocks = re.findall(r'```mermaid\n(.*?)\n```', text, re.DOTALL)
    # Find all mermaid code blocks in the text
    for block in mermaid_blocks:
        diagram_text = block.strip()
        lines = diagram_text.split('\n')
        corrected_lines = []
        for line in lines:
            corrected_line = re.sub(r'\|.*?\|>', lambda match: match.group(0).replace('|>', '|'), line)
            corrected_lines.append(corrected_line)
        text = text.replace(block, "\n".join(corrected_lines))
    task_output.raw = text
    return (True, task_output)

# Force remove readonly files (for .git files)
def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)