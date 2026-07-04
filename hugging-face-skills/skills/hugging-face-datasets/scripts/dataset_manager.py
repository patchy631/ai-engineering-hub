#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "huggingface_hub>=0.20.0",
# ]
# ///
"""
Hugging Face Dataset Manager

Enhanced dataset creation and management tool designed to work alongside
the HF MCP server. Provides dataset creation, configuration, and content
management capabilities optimized for conversational AI training data.

Version: 2.0.0

Usage:
    uv run dataset_manager.py init --repo_id username/dataset-name
    uv run dataset_manager.py quick_setup --repo_id username/dataset-name --template chat
    uv run dataset_manager.py add_rows --repo_id username/dataset-name --rows_json '[{"messages": [...]}]'
    uv run dataset_manager.py stats --repo_id username/dataset-name
    uv run dataset_manager.py list_templates
"""

import os
import json
import time
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
from huggingface_hub import HfApi, create_repo
from huggingface_hub.utils import HfHubHTTPError

# Configuration
HF_TOKEN = os.environ.get("HF_TOKEN")
EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def init_dataset(repo_id, token=None, private=True):
    """
    Initialize a new dataset repository on Hugging Face Hub.
    """
    api = HfApi(token=token)
    try:
        create_repo(repo_id, repo_type="dataset", private=private, token=token)
        print(f"Created dataset repository: {repo_id}")
    except HfHubHTTPError as e:
        if "409" in str(e):
            print(f"Repository {repo_id} already exists.")
        else:
            raise e

    # Create a basic README.md with metadata if it doesn't exist
    readme_content = f"""---
license: mit
---

# {repo_id.split("/")[-1]}

This dataset was created using the Claude Dataset Skill.
"""
    try:
        api.upload_file(
            path_or_fileobj=readme_content.encode("utf-8"),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="dataset",
            commit_message="Initialize dataset README",
        )
    except Exception as e:
        print(f"Note: README might already exist or failed to update: {e}")


def define_config(repo_id, system_prompt=None, token=None):
    """
    Define a configuration for the dataset, including a system prompt.
    This saves a config.json file to the repository.
    """
    api = HfApi(token=token)

    config_data = {"dataset_config": {"version": "1.0", "created_at": time.time()}}

    if system_prompt:
        config_data["system_prompt"] = system_prompt

    # Upload config.json
    api.upload_file(
        path_or_fileobj=json.dumps(config_data, indent=2).encode("utf-8"),
        path_in_repo="config.json",
        repo_id=repo_id,
        repo_type="dataset",
        commit_message="Update dataset configuration",
    )
    print(f"Configuration updated for {repo_id}")


def load_dataset_template(template_name: str) -> Dict[str, Any]:
    """Load dataset template configuration from templates directory."""
    template_path = EXAMPLES_DIR.parent / "templates" / f"{template_name}.json"
    if not template_path.exists():
        available_templates = [f.stem for f in (EXAMPLES_DIR.parent / "templates").glob("*.json")]
        print(f"❌ Template '{template_name}' not found.")
        print(f"Available templates: {', '.join(available_templates)}")
        return {}

    with open(template_path) as f:
        return json.load(f)


def validate_by_template(rows: List[Dict[str, Any]], template: Dict[str, Any]) -> bool:
    """Validate data according to template schema."""
    if not template:
        return False

    schema = template.get("validation_schema", {})
    required_fields = set(schema.get("required_fields", []))
    recommended_fields = set(schema.get("recommended_fields", []))
    field_types = schema.get("field_types", {})

    for i, row in enumerate(rows):
        # Check required fields
        if not all(field in row for field in required_fields):
            missing = required_fields - set(row.keys())
            print(f"Row {i}: Missing required fields: {missing}")
            return False

        # Validate field types
        for field, expected_type in field_types.items():
            if field in row:
                if not _validate_field_type(row[field], expected_type, f"Row {i}, field '{field}'"):
                    return False

        # Template-specific validation
        if template["type"] == "chat":
            if not _validate_chat_format(row, i):
                return False
        elif template["type"] == "classification":
            if not _validate_classification_format(row, i):
                return False
        elif template["type"] == "tabular":
            if not _validate_tabular_format(row, i):
                return False

        # Warn about missing recommended fields
        missing_recommended = recommended_fields - set(row.keys())
        if missing_recommended:
            print(f"Row {i}: Recommended to include: {missing_recommended}")

    print(f"✓ Validated {len(rows)} examples for {template['type']} dataset")
    return True


def _validate_field_type(value: Any, expected_type: str, context: str) -> bool:
    """Validate individual field type."""
    if expected_type.startswith("enum:"):
        valid_values = expected_type[5:].split(",")
        if value not in valid_values:
            print(f"{context}: Invalid value '{value}'. Must be one of: {valid_values}")
            return False
    elif expected_type == "array" and not isinstance(value, list):
        print(f"{context}: Expected array, got {type(value).__name__}")
        return False
    elif expected_type == "object" and not isinstance(value, dict):
        print(f"{context}: Expected object, got {type(value).__name__}")
        return False
    elif expected_type == "string" and not isinstance(value, str):
        print(f"{context}: Expected string, got {type(value).__name__}")
        return False
    elif expected_type == "number" and not isinstance(value, (int, float)):
        print(f"{context}: Expected number, got {type(value).__name__}")
        return False

    return True


def _validate_chat_format(row: Dict[str, Any], row_index: int) -> bool:
    """Validate chat-specific format."""
    messages = row.get("messages", [])
    if not isinstance(messages, list) or len(messages) == 0:
        print(f"Row {row_index}: 'messages' must be a non-empty list")
        return False

    valid_roles = {"user", "assistant", "tool", "system"}
    for j, msg in enumerate(messages):
        if not isinstance(msg, dict):
            print(f"Row {row_index}, message {j}: Must be an object")
            return False
        if "role" not in msg or msg["role"] not in valid_roles:
            print(f"Row {row_index}, message {j}: Invalid role. Use: {valid_roles}")
            return False
        if "content" not in msg:
            print(f"Row {row_index}, message {j}: Missing 'content' field")
            return False

    return True


def _validate_classification_format(row: Dict[str, Any], row_index: int) -> bool:
    """Validate classification-specific format."""
    if "text" not in row:
        print(f"Row {row_index}: Missing 'text' field")
        return False
    if "label" not in row:
        print(f"Row {row_index}: Missing 'label' field")
        return False

    return True


def _validate_tabular_format(row: Dict[str, Any], row_index: int) -> bool:
    """Validate tabular-specific format."""
    if "data" not in row:
        print(f"Row {row_index}: Missing 'data' field")
        return False
    if "columns" not in row:
        print(f"Row {row_index}: Missing 'columns' field")
        return False

    data = row["data"]
    columns = row["columns"]

    if not isinstance(data, list):
        print(f"Row {row_index}: 'data' must be an array")
        return False
    if not isinstance(columns, list):
        print(f"Row {row_index}: 'columns' must be an array")
        return False

    return True


def validate_training_data(rows: List[Dict[str, Any]], template_name: str = "chat") -> bool:
    """
    Validate training data structure according to template.
    Supports multiple dataset types with appropriate validation.
    """
    template = load_dataset_template(template_name)
    if not template:
        print(f"❌ Could not load template '{template_name}', falling back to basic validation")
        return _basic_validation(rows)

    return validate_by_template(rows, template)


def _basic_validation(rows: List[Dict[str, Any]]) -> bool:
    """Basic validation when no template is available."""
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            print(f"Row {i}: Must be a dictionary/object")
            return False
    print(f"✓ Basic validation passed for {len(rows)} rows")
    return True


def add_rows(
    repo_id: str,
    rows: List[Dict[str, Any]],
    split: str = "train",
    validate: bool = True,
    template: str = "chat",
    token: Optional[str] = None,
) -> None:
    """
    Stream updates to the dataset by uploading a new chunk of rows.
    Enhanced with validation for multiple dataset types.

    Args:
        repo_id: Repository identifier (username/dataset-name)
        rows: List of training examples
        split: Dataset split name (train, test, validation)
        validate: Whether to validate data structure before upload
        template: Dataset template type (chat, classification, qa, completion, tabular, custom)
        token: HuggingFace API token
    """
    api = HfApi(token=token)

    if not rows:
        print("No rows to add.")
        return

    # Validate training data structure
    if validate and not validate_training_data(rows, template):
        print("❌ Validation failed. Use --no-validate to skip validation.")
        return

    # Create a newline-delimited JSON string
    jsonl_content = "\n".join(json.dumps(row) for row in rows)

    # Generate a unique filename for this chunk
    timestamp = int(time.time() * 1000)
    filename = f"data/{split}-{timestamp}.jsonl"

    try:
        api.upload_file(
            path_or_fileobj=jsonl_content.encode("utf-8"),
            path_in_repo=filename,
            repo_id=repo_id,
            repo_type="dataset",
            commit_message=f"Add {len(rows)} rows to {split} split",
        )
        print(f"✅ Added {len(rows)} rows to {repo_id} (split: {split})")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return


def load_template(template_name: str = "system_prompt_template.txt") -> str:
    """Load a template file from the examples directory."""
    template_path = EXAMPLES_DIR / template_name
    if template_path.exists():
        return template_path.read_text()
    else:
        print(f"⚠️ Template {template_name} not found at {template_path}")
        return ""


def quick_setup(repo_id: str, template_type: str = "chat", token: Optional[str] = None) -> None:
    """
    Quick setup for different dataset types using templates.

    Args:
        repo_id: Repository identifier
        template_type: Dataset template (chat, classification, qa, completion, tabular, custom)
        token: HuggingFace API token
    """
    print(f"🚀 Quick setup for {repo_id} with '{template_type}' template...")

    # Load template configuration
    template_config = load_dataset_template(template_type)
    if not template_config:
        print(f"❌ Could not load template '{template_type}'. Setup cancelled.")
        return

    # Initialize repository
    init_dataset(repo_id, token=token, private=True)

    # Configure with template system prompt
    system_prompt = template_config.get("system_prompt", "")
    if system_prompt:
        define_config(repo_id, system_prompt=system_prompt, token=token)

    # Add template examples
    examples = template_config.get("examples", [])
    if examples:
        add_rows(repo_id, examples, template=template_type, token=token)
        print(f"✅ Added {len(examples)} example(s) from template")

    print(f"✅ Quick setup complete for {repo_id}")
    print(f"📊 Dataset type: {template_config.get('description', 'No description')}")

    # Show next steps
    print(f"\n📋 Next steps:")
    print(
        f"1. Add more data: python scripts/dataset_manager.py add_rows --repo_id {repo_id} --template {template_type} --rows_json 'your_data.json'"
    )
    print(f"2. View stats: python scripts/dataset_manager.py stats --repo_id {repo_id}")
    print(f"3. Explore at: https://huggingface.co/datasets/{repo_id}")


def show_stats(repo_id: str, token: Optional[str] = None) -> None:
    """Display statistics about the dataset."""
    api = HfApi(token=token)

    try:
        # Get repository info
        repo_info = api.repo_info(repo_id, repo_type="dataset")
        print(f"\n📊 Dataset Stats: {repo_id}")
        print(f"Created: {repo_info.created_at}")
        print(f"Updated: {repo_info.last_modified}")
        print(f"Private: {repo_info.private}")

        # List files
        files = api.list_repo_files(repo_id, repo_type="dataset")
        data_files = [f for f in files if f.startswith("data/")]
        print(f"Data files: {len(data_files)}")

        if "config.json" in files:
            print("✅ Configuration present")
        else:
            print("⚠️ No configuration found")

    except Exception as e:
        print(f"❌ Failed to get stats: {e}")


def list_available_templates() -> None:
    """List all available dataset templates with descriptions."""
    templates_dir = EXAMPLES_DIR.parent / "templates"

    if not templates_dir.exists():
        print("❌ Templates directory not found")
        return

    print("\n📋 Available Dataset Templates:")
    print("=" * 50)

    for template_file in templates_dir.glob("*.json"):
        try:
            with open(template_file) as f:
                template = json.load(f)

            name = template_file.stem
            desc = template.get("description", "No description available")
            template_type = template.get("type", name)

            print(f"\n🏷️  {name}")
            print(f"   Type: {template_type}")
            print(f"   Description: {desc}")

            # Show required fields
            schema = template.get("validation_schema", {})
            required = schema.get("required_fields", [])
            if required:
                print(f"   Required fields: {', '.join(required)}")

        except Exception as e:
            print(f"❌ Error loading template {template_file.name}: {e}")

    print(
        f"\n💡 Usage: python scripts/dataset_manager.py quick_setup --repo_id your-username/dataset-name --template TEMPLATE_NAME"
    )
    print(f"📚 Example templates directory: {templates_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hugging Face Dataset Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new dataset")
    init_parser.add_argument("--repo_id", required=True, help="Repository ID (user/repo_name)")
    init_parser.add_argument("--private", action="store_true", help="Make repository private")

    # Config command
    config_parser = subparsers.add_parser("config", help="Setup dataset config")
    config_parser.add_argument("--repo_id", required=True, help="Repository ID")
    config_parser.add_argument("--system_prompt", help="System prompt to store in config")

    # Add rows command
    add_parser = subparsers.add_parser("add_rows", help="Add rows to the dataset")
    add_parser.add_argument("--repo_id", required=True, help="Repository ID")
    add_parser.add_argument("--split", default="train", help="Dataset split (e.g., train, test)")
    add_parser.add_argument(
        "--template",
        default="chat",
        choices=[
            "chat",
            "classification",
            "qa",
            "completion",
            "tabular",
            "custom",
        ],
        help="Dataset template type for validation",
    )
    add_parser.add_argument(
        "--rows_json",
        required=True,
        help="JSON string containing a list of rows",
    )
    add_parser.add_argument(
        "--no-validate",
        dest="validate",
        action="store_false",
        help="Skip data validation",
    )

    # Quick setup command
    setup_parser = subparsers.add_parser("quick_setup", help="Quick setup with template")
    setup_parser.add_argument("--repo_id", required=True, help="Repository ID")
    setup_parser.add_argument(
        "--template",
        default="chat",
        choices=[
            "chat",
            "classification",
            "qa",
            "completion",
            "tabular",
            "custom",
        ],
        help="Dataset template type",
    )

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show dataset statistics")
    stats_parser.add_argument("--repo_id", required=True, help="Repository ID")

    # List templates command
    templates_parser = subparsers.add_parser("list_templates", help="List available dataset templates")

    args = parser.parse_args()

    token = HF_TOKEN
    if not token:
        print("Warning: HF_TOKEN environment variable not set.")

    if args.command == "init":
        init_dataset(args.repo_id, token=token, private=args.private)
    elif args.command == "config":
        define_config(args.repo_id, system_prompt=args.system_prompt, token=token)
    elif args.command == "add_rows":
        try:
            rows = json.loads(args.rows_json)
            if not isinstance(rows, list):
                raise ValueError("rows_json must be a JSON list of objects")
            add_rows(
                args.repo_id,
                rows,
                split=args.split,
                template=args.template,
                validate=args.validate,
                token=token,
            )
        except json.JSONDecodeError:
            print("Error: Invalid JSON provided for --rows_json")
    elif args.command == "quick_setup":
        quick_setup(args.repo_id, template_type=args.template, token=token)
    elif args.command == "stats":
        show_stats(args.repo_id, token=token)
    elif args.command == "list_templates":
        list_available_templates()
