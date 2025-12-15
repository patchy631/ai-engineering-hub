import json
from .models import ClaimInfo

def parse_claim_from_text(json_text: str) -> ClaimInfo:
    """
    Parse the input JSON text into a ClaimInfo object.
    """
    data = json.loads(json_text)
    return ClaimInfo(**data)

def load_prompt(file_path: str) -> str:
    """
    Reads a prompt file from disk.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()