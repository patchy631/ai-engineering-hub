from pathlib import Path
from typing import Any, Dict

import yaml


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """Load YAML configuration file."""
    config_file = Path(__file__).parent / config_path
    with open(config_file, encoding="utf-8") as f:
        return yaml.safe_load(f)
