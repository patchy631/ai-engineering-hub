# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "huggingface-hub>=1.1.4",
#     "markdown-it-py>=3.0.0",
#     "python-dotenv>=1.2.1",
#     "pyyaml>=6.0.3",
#     "requests>=2.32.5",
# ]
# ///

"""
Manage evaluation results in Hugging Face model cards.

This script provides two methods:
1. Extract evaluation tables from model README files
2. Import evaluation scores from Artificial Analysis API

Both methods update the model-index metadata in model cards.
"""

import argparse
import os
import re
from textwrap import dedent
from typing import Any, Dict, List, Optional, Tuple


def load_env() -> None:
    """Load .env if python-dotenv is available; keep help usable without it."""
    try:
        import dotenv  # type: ignore
    except ModuleNotFoundError:
        return
    dotenv.load_dotenv()


def require_markdown_it():
    try:
        from markdown_it import MarkdownIt  # type: ignore
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "markdown-it-py is required for table parsing. "
            "Install with `uv add markdown-it-py` or `pip install markdown-it-py`."
        ) from exc
    return MarkdownIt


def require_model_card():
    try:
        from huggingface_hub import ModelCard  # type: ignore
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "huggingface-hub is required for model card operations. "
            "Install with `uv add huggingface_hub` or `pip install huggingface-hub`."
        ) from exc
    return ModelCard


def require_requests():
    try:
        import requests  # type: ignore
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "requests is required for Artificial Analysis import. "
            "Install with `uv add requests` or `pip install requests`."
        ) from exc
    return requests


def require_yaml():
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "PyYAML is required for YAML output. "
            "Install with `uv add pyyaml` or `pip install pyyaml`."
        ) from exc
    return yaml


# ============================================================================
# Method 1: Extract Evaluations from README
# ============================================================================


def extract_tables_from_markdown(markdown_content: str) -> List[str]:
    """Extract all markdown tables from content."""
    # Pattern to match markdown tables
    table_pattern = r"(\|[^\n]+\|(?:\r?\n\|[^\n]+\|)+)"
    tables = re.findall(table_pattern, markdown_content)
    return tables


def parse_markdown_table(table_str: str) -> Tuple[List[str], List[List[str]]]:
    """
    Parse a markdown table string into headers and rows.

    Returns:
        Tuple of (headers, data_rows)
    """
    lines = [line.strip() for line in table_str.strip().split("\n")]

    # Remove separator line (the one with dashes)
    lines = [line for line in lines if not re.match(r"^\|[\s\-:]+\|$", line)]

    if len(lines) < 2:
        return [], []

    # Parse header
    header = [cell.strip() for cell in lines[0].split("|")[1:-1]]

    # Parse data rows
    data_rows = []
    for line in lines[1:]:
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if cells:
            data_rows.append(cells)

    return header, data_rows


def is_evaluation_table(header: List[str], rows: List[List[str]]) -> bool:
    """Determine if a table contains evaluation results."""
    if not header or not rows:
        return False

    # Check if first column looks like benchmark names
    benchmark_keywords = [
        "benchmark", "task", "dataset", "eval", "test", "metric",
        "mmlu", "humaneval", "gsm", "hellaswag", "arc", "winogrande",
        "truthfulqa", "boolq", "piqa", "siqa"
    ]

    first_col = header[0].lower()
    has_benchmark_header = any(keyword in first_col for keyword in benchmark_keywords)

    # Check if there are numeric values in the table
    has_numeric_values = False
    for row in rows:
        for cell in row:
            try:
                float(cell.replace("%", "").replace(",", ""))
                has_numeric_values = True
                break
            except ValueError:
                continue
        if has_numeric_values:
            break

    return has_benchmark_header or has_numeric_values


def normalize_model_name(name: str) -> tuple[set[str], str]:
    """
    Normalize a model name for matching.

    Args:
        name: Model name to normalize

    Returns:
        Tuple of (token_set, normalized_string)
    """
    # Remove markdown formatting
    cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', name)  # Remove markdown links
    cleaned = re.sub(r'\*\*([^\*]+)\*\*', r'\1', cleaned)  # Remove bold
    cleaned = cleaned.strip()

    # Normalize and tokenize
    normalized = cleaned.lower().replace("-", " ").replace("_", " ")
    tokens = set(normalized.split())

    return tokens, normalized


def find_main_model_column(header: List[str], model_name: str) -> Optional[int]:
    """
    Identify the column index that corresponds to the main model.

    Only returns a column if there's an exact normalized match with the model name.
    This prevents extracting scores from training checkpoints or similar models.

    Args:
        header: Table column headers
        model_name: Model name from repo_id (e.g., "OLMo-3-32B-Think")

    Returns:
        Column index of the main model, or None if no exact match found
    """
    if not header or not model_name:
        return None

    # Normalize model name and extract tokens
    model_tokens, _ = normalize_model_name(model_name)

    # Find exact matches only
    for i, col_name in enumerate(header):
        if not col_name:
            continue

        # Skip first column (benchmark names)
        if i == 0:
            continue

        col_tokens, _ = normalize_model_name(col_name)

        # Check for exact token match
        if model_tokens == col_tokens:
            return i

    # No exact match found
    return None


def find_main_model_row(
    rows: List[List[str]], model_name: str
) -> tuple[Optional[int], List[str]]:
    """
    Identify the row index that corresponds to the main model in a transposed table.

    In transposed tables, each row represents a different model, with the first
    column containing the model name.

    Args:
        rows: Table data rows
        model_name: Model name from repo_id (e.g., "OLMo-3-32B")

    Returns:
        Tuple of (row_index, available_models)
        - row_index: Index of the main model, or None if no exact match found
        - available_models: List of all model names found in the table
    """
    if not rows or not model_name:
        return None, []

    model_tokens, _ = normalize_model_name(model_name)
    available_models = []

    for i, row in enumerate(rows):
        if not row or not row[0]:
            continue

        row_name = row[0].strip()

        # Skip separator/header rows
        if not row_name or row_name.startswith('---'):
            continue

        row_tokens, _ = normalize_model_name(row_name)

        # Collect all non-empty model names
        if row_tokens:
            available_models.append(row_name)

        # Check for exact token match
        if model_tokens == row_tokens:
            return i, available_models

    return None, available_models


def is_transposed_table(header: List[str], rows: List[List[str]]) -> bool:
    """
    Determine if a table is transposed (models as rows, benchmarks as columns).

    A table is considered transposed if:
    - The first column contains model-like names (not benchmark names)
    - Most other columns contain numeric values
    - Header row contains benchmark-like names

    Args:
        header: Table column headers
        rows: Table data rows

    Returns:
        True if table appears to be transposed, False otherwise
    """
    if not header or not rows or len(header) < 3:
        return False

    # Check if first column header suggests model names
    first_col = header[0].lower()
    model_indicators = ["model", "system", "llm", "name"]
    has_model_header = any(indicator in first_col for indicator in model_indicators)

    # Check if remaining headers look like benchmarks
    benchmark_keywords = [
        "mmlu", "humaneval", "gsm", "hellaswag", "arc", "winogrande",
        "eval", "score", "benchmark", "test", "math", "code", "mbpp",
        "truthfulqa", "boolq", "piqa", "siqa", "drop", "squad"
    ]

    benchmark_header_count = 0
    for col_name in header[1:]:
        col_lower = col_name.lower()
        if any(keyword in col_lower for keyword in benchmark_keywords):
            benchmark_header_count += 1

    has_benchmark_headers = benchmark_header_count >= 2

    # Check if data rows have numeric values in most columns (except first)
    numeric_count = 0
    total_cells = 0

    for row in rows[:5]:  # Check first 5 rows
        for cell in row[1:]:  # Skip first column
            total_cells += 1
            try:
                float(cell.replace("%", "").replace(",", "").strip())
                numeric_count += 1
            except (ValueError, AttributeError):
                continue

    has_numeric_data = total_cells > 0 and (numeric_count / total_cells) > 0.5

    return (has_model_header or has_benchmark_headers) and has_numeric_data


def extract_metrics_from_table(
    header: List[str],
    rows: List[List[str]],
    table_format: str = "auto",
    model_name: Optional[str] = None,
    model_column_index: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Extract metrics from parsed table data.

    Args:
        header: Table column headers
        rows: Table data rows
        table_format: "rows" (benchmarks as rows), "columns" (benchmarks as columns),
                     "transposed" (models as rows, benchmarks as columns), or "auto"
        model_name: Optional model name to identify the correct column/row

    Returns:
        List of metric dictionaries with name, type, and value
    """
    metrics = []

    if table_format == "auto":
        # First check if it's a transposed table (models as rows)
        if is_transposed_table(header, rows):
            table_format = "transposed"
        else:
            # Check if first column header is empty/generic (indicates benchmarks in rows)
            first_header = header[0].lower().strip() if header else ""
            is_first_col_benchmarks = not first_header or first_header in ["", "benchmark", "task", "dataset", "metric", "eval"]

            if is_first_col_benchmarks:
                table_format = "rows"
            else:
                # Heuristic: if first row has mostly numeric values, benchmarks are columns
                try:
                    numeric_count = sum(
                        1 for cell in rows[0] if cell and
                        re.match(r"^\d+\.?\d*%?$", cell.replace(",", "").strip())
                    )
                    table_format = "columns" if numeric_count > len(rows[0]) / 2 else "rows"
                except (IndexError, ValueError):
                    table_format = "rows"

    if table_format == "rows":
        # Benchmarks are in rows, scores in columns
        # Try to identify the main model column if model_name is provided
        target_column = model_column_index
        if target_column is None and model_name:
            target_column = find_main_model_column(header, model_name)

        for row in rows:
            if not row:
                continue

            benchmark_name = row[0].strip()
            if not benchmark_name:
                continue

            # If we identified a specific column, use it; otherwise use first numeric value
            if target_column is not None and target_column < len(row):
                try:
                    value_str = row[target_column].replace("%", "").replace(",", "").strip()
                    if value_str:
                        value = float(value_str)
                        metrics.append({
                            "name": benchmark_name,
                            "type": benchmark_name.lower().replace(" ", "_"),
                            "value": value
                        })
                except (ValueError, IndexError):
                    pass
            else:
                # Extract numeric values from remaining columns (original behavior)
                for i, cell in enumerate(row[1:], start=1):
                    try:
                        # Remove common suffixes and convert to float
                        value_str = cell.replace("%", "").replace(",", "").strip()
                        if not value_str:
                            continue

                        value = float(value_str)

                        # Determine metric name
                        metric_name = benchmark_name
                        if len(header) > i and header[i].lower() not in ["score", "value", "result"]:
                            metric_name = f"{benchmark_name} ({header[i]})"

                        metrics.append({
                            "name": metric_name,
                            "type": benchmark_name.lower().replace(" ", "_"),
                            "value": value
                        })
                        break  # Only take first numeric value per row
                    except (ValueError, IndexError):
                        continue

    elif table_format == "transposed":
        # Models are in rows (first column), benchmarks are in columns (header)
        # Find the row that matches the target model
        if not model_name:
            print("Warning: model_name required for transposed table format")
            return metrics

        target_row_idx, available_models = find_main_model_row(rows, model_name)

        if target_row_idx is None:
            print(f"\n⚠ Could not find model '{model_name}' in transposed table")
            if available_models:
                print("\nAvailable models in table:")
                for i, model in enumerate(available_models, 1):
                    print(f"  {i}. {model}")
                print("\nPlease select the correct model name from the list above.")
                print("You can specify it using the --model-name-override flag:")
                print(f'  --model-name-override "{available_models[0]}"')
            return metrics

        target_row = rows[target_row_idx]

        # Extract metrics from each column (skip first column which is model name)
        for i in range(1, len(header)):
            benchmark_name = header[i].strip()
            if not benchmark_name or i >= len(target_row):
                continue

            try:
                value_str = target_row[i].replace("%", "").replace(",", "").strip()
                if not value_str:
                    continue

                value = float(value_str)

                metrics.append({
                    "name": benchmark_name,
                    "type": benchmark_name.lower().replace(" ", "_").replace("-", "_"),
                    "value": value
                })
            except (ValueError, AttributeError):
                continue

    else:  # table_format == "columns"
        # Benchmarks are in columns
        if not rows:
            return metrics

        # Use first data row for values
        data_row = rows[0]

        for i, benchmark_name in enumerate(header):
            if not benchmark_name or i >= len(data_row):
                continue

            try:
                value_str = data_row[i].replace("%", "").replace(",", "").strip()
                if not value_str:
                    continue

                value = float(value_str)

                metrics.append({
                    "name": benchmark_name,
                    "type": benchmark_name.lower().replace(" ", "_"),
                    "value": value
                })
            except ValueError:
                continue

    return metrics


def extract_evaluations_from_readme(
    repo_id: str,
    task_type: str = "text-generation",
    dataset_name: str = "Benchmarks",
    dataset_type: str = "benchmark",
    model_name_override: Optional[str] = None,
    table_index: Optional[int] = None,
    model_column_index: Optional[int] = None
) -> Optional[List[Dict[str, Any]]]:
    """
    Extract evaluation results from a model's README.

    Args:
        repo_id: Hugging Face model repository ID
        task_type: Task type for model-index (e.g., "text-generation")
        dataset_name: Name for the benchmark dataset
        dataset_type: Type identifier for the dataset
        model_name_override: Override model name for matching (column header for comparison tables)
        table_index: 1-indexed table number from inspect-tables output

    Returns:
        Model-index formatted results or None if no evaluations found
    """
    try:
        load_env()
        ModelCard = require_model_card()
        hf_token = os.getenv("HF_TOKEN")
        card = ModelCard.load(repo_id, token=hf_token)
        readme_content = card.content

        if not readme_content:
            print(f"No README content found for {repo_id}")
            return None

        # Extract model name from repo_id or use override
        if model_name_override:
            model_name = model_name_override
            print(f"Using model name override: '{model_name}'")
        else:
            model_name = repo_id.split("/")[-1] if "/" in repo_id else repo_id

        # Use markdown-it parser for accurate table extraction
        all_tables = extract_tables_with_parser(readme_content)

        if not all_tables:
            print(f"No tables found in README for {repo_id}")
            return None

        # If table_index specified, use that specific table
        if table_index is not None:
            if table_index < 1 or table_index > len(all_tables):
                print(f"Invalid table index {table_index}. Found {len(all_tables)} tables.")
                print("Run inspect-tables to see available tables.")
                return None
            tables_to_process = [all_tables[table_index - 1]]
        else:
            # Filter to evaluation tables only
            eval_tables = []
            for table in all_tables:
                header = table.get("headers", [])
                rows = table.get("rows", [])
                if is_evaluation_table(header, rows):
                    eval_tables.append(table)

            if len(eval_tables) > 1:
                print(f"\n⚠ Found {len(eval_tables)} evaluation tables.")
                print("Run inspect-tables first, then use --table to select one:")
                print(f'  uv run scripts/evaluation_manager.py inspect-tables --repo-id "{repo_id}"')
                return None
            elif len(eval_tables) == 0:
                print(f"No evaluation tables found in README for {repo_id}")
                return None

            tables_to_process = eval_tables

        # Extract metrics from selected table(s)
        all_metrics = []
        for table in tables_to_process:
            header = table.get("headers", [])
            rows = table.get("rows", [])
            metrics = extract_metrics_from_table(
                header,
                rows,
                model_name=model_name,
                model_column_index=model_column_index
            )
            all_metrics.extend(metrics)

        if not all_metrics:
            print(f"No metrics extracted from table")
            return None

        # Build model-index structure
        display_name = repo_id.split("/")[-1] if "/" in repo_id else repo_id

        results = [{
            "task": {"type": task_type},
            "dataset": {
                "name": dataset_name,
                "type": dataset_type
            },
            "metrics": all_metrics,
            "source": {
                "name": "Model README",
                "url": f"https://huggingface.co/{repo_id}"
            }
        }]

        return results

    except Exception as e:
        print(f"Error extracting evaluations from README: {e}")
        return None


# ============================================================================
# Table Inspection (using markdown-it-py for accurate parsing)
# ============================================================================


def extract_tables_with_parser(markdown_content: str) -> List[Dict[str, Any]]:
    """
    Extract tables from markdown using markdown-it-py parser.
    Uses GFM (GitHub Flavored Markdown) which includes table support.
    """
    MarkdownIt = require_markdown_it()
    # Disable linkify to avoid optional dependency errors; not needed for table parsing.
    md = MarkdownIt("gfm-like", {"linkify": False})
    tokens = md.parse(markdown_content)

    tables = []
    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token.type == "table_open":
            table_data = {"headers": [], "rows": []}
            current_row = []
            in_header = False

            i += 1
            while i < len(tokens) and tokens[i].type != "table_close":
                t = tokens[i]
                if t.type == "thead_open":
                    in_header = True
                elif t.type == "thead_close":
                    in_header = False
                elif t.type == "tr_open":
                    current_row = []
                elif t.type == "tr_close":
                    if in_header:
                        table_data["headers"] = current_row
                    else:
                        table_data["rows"].append(current_row)
                    current_row = []
                elif t.type == "inline":
                    current_row.append(t.content.strip())
                i += 1

            if table_data["headers"] or table_data["rows"]:
                tables.append(table_data)

        i += 1

    return tables


def detect_table_format(table: Dict[str, Any], repo_id: str) -> Dict[str, Any]:
    """Analyze a table to detect its format and identify model columns."""
    headers = table.get("headers", [])
    rows = table.get("rows", [])

    if not headers or not rows:
        return {"format": "unknown", "columns": headers, "model_columns": [], "row_count": 0, "sample_rows": []}

    first_header = headers[0].lower() if headers else ""
    is_first_col_benchmarks = not first_header or first_header in ["", "benchmark", "task", "dataset", "metric", "eval"]

    # Check for numeric columns
    numeric_columns = []
    for col_idx in range(1, len(headers)):
        numeric_count = 0
        for row in rows[:5]:
            if col_idx < len(row):
                try:
                    val = re.sub(r'\s*\([^)]*\)', '', row[col_idx])
                    float(val.replace("%", "").replace(",", "").strip())
                    numeric_count += 1
                except (ValueError, AttributeError):
                    pass
        if numeric_count > len(rows[:5]) / 2:
            numeric_columns.append(col_idx)

    # Determine format
    if is_first_col_benchmarks and len(numeric_columns) > 1:
        format_type = "comparison"
    elif is_first_col_benchmarks and len(numeric_columns) == 1:
        format_type = "simple"
    elif len(numeric_columns) > len(headers) / 2:
        format_type = "transposed"
    else:
        format_type = "unknown"

    # Find model columns
    model_columns = []
    model_name = repo_id.split("/")[-1] if "/" in repo_id else repo_id
    model_tokens, _ = normalize_model_name(model_name)

    for idx, header in enumerate(headers):
        if idx == 0 and is_first_col_benchmarks:
            continue
        if header:
            header_tokens, _ = normalize_model_name(header)
            is_match = model_tokens == header_tokens
            is_partial = model_tokens.issubset(header_tokens) or header_tokens.issubset(model_tokens)
            model_columns.append({
                "index": idx,
                "header": header,
                "is_exact_match": is_match,
                "is_partial_match": is_partial and not is_match
            })

    return {
        "format": format_type,
        "columns": headers,
        "model_columns": model_columns,
        "row_count": len(rows),
        "sample_rows": [row[0] for row in rows[:5] if row]
    }


def inspect_tables(repo_id: str) -> None:
    """Inspect and display all evaluation tables in a model's README."""
    try:
        load_env()
        ModelCard = require_model_card()
        hf_token = os.getenv("HF_TOKEN")
        card = ModelCard.load(repo_id, token=hf_token)
        readme_content = card.content

        if not readme_content:
            print(f"No README content found for {repo_id}")
            return

        tables = extract_tables_with_parser(readme_content)

        if not tables:
            print(f"No tables found in README for {repo_id}")
            return

        print(f"\n{'='*70}")
        print(f"Tables found in README for: {repo_id}")
        print(f"{'='*70}")

        eval_table_count = 0
        for table in tables:
            analysis = detect_table_format(table, repo_id)

            if analysis["format"] == "unknown" and not analysis.get("sample_rows"):
                continue

            eval_table_count += 1
            print(f"\n## Table {eval_table_count}")
            print(f"   Format: {analysis['format']}")
            print(f"   Rows: {analysis['row_count']}")

            print(f"\n   Columns ({len(analysis['columns'])}):")
            for col_info in analysis.get("model_columns", []):
                idx = col_info["index"]
                header = col_info["header"]
                if col_info["is_exact_match"]:
                    print(f"      [{idx}] {header}  ✓ EXACT MATCH")
                elif col_info["is_partial_match"]:
                    print(f"      [{idx}] {header}  ~ partial match")
                else:
                    print(f"      [{idx}] {header}")

            if analysis.get("sample_rows"):
                print(f"\n   Sample rows (first column):")
                for row_val in analysis["sample_rows"][:5]:
                    print(f"      - {row_val}")

        if eval_table_count == 0:
            print("\nNo evaluation tables detected.")
        else:
            print("\nSuggested next step:")
            print(f'  uv run scripts/evaluation_manager.py extract-readme --repo-id "{repo_id}" --table <table-number> [--model-column-index <column-index>]')

        print(f"\n{'='*70}\n")

    except Exception as e:
        print(f"Error inspecting tables: {e}")


# ============================================================================
# Pull Request Management
# ============================================================================


def get_open_prs(repo_id: str) -> List[Dict[str, Any]]:
    """
    Fetch open pull requests for a Hugging Face model repository.

    Args:
        repo_id: Hugging Face model repository ID (e.g., "allenai/Olmo-3-32B-Think")

    Returns:
        List of open PR dictionaries with num, title, author, and createdAt
    """
    requests = require_requests()
    url = f"https://huggingface.co/api/models/{repo_id}/discussions"

    try:
        response = requests.get(url, timeout=30, allow_redirects=True)
        response.raise_for_status()

        data = response.json()
        discussions = data.get("discussions", [])

        open_prs = [
            {
                "num": d["num"],
                "title": d["title"],
                "author": d["author"]["name"],
                "createdAt": d.get("createdAt", "unknown"),
            }
            for d in discussions
            if d.get("status") == "open" and d.get("isPullRequest")
        ]

        return open_prs

    except requests.RequestException as e:
        print(f"Error fetching PRs from Hugging Face: {e}")
        return []


def list_open_prs(repo_id: str) -> None:
    """Display open pull requests for a model repository."""
    prs = get_open_prs(repo_id)

    print(f"\n{'='*70}")
    print(f"Open Pull Requests for: {repo_id}")
    print(f"{'='*70}")

    if not prs:
        print("\nNo open pull requests found.")
    else:
        print(f"\nFound {len(prs)} open PR(s):\n")
        for pr in prs:
            print(f"  PR #{pr['num']} - {pr['title']}")
            print(f"     Author: {pr['author']}")
            print(f"     Created: {pr['createdAt']}")
            print(f"     URL: https://huggingface.co/{repo_id}/discussions/{pr['num']}")
            print()

    print(f"{'='*70}\n")


# ============================================================================
# Method 2: Import from Artificial Analysis
# ============================================================================


def get_aa_model_data(creator_slug: str, model_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetch model evaluation data from Artificial Analysis API.

    Args:
        creator_slug: Creator identifier (e.g., "anthropic", "openai")
        model_name: Model slug/identifier

    Returns:
        Model data dictionary or None if not found
    """
    load_env()
    AA_API_KEY = os.getenv("AA_API_KEY")
    if not AA_API_KEY:
        raise ValueError("AA_API_KEY environment variable is not set")

    url = "https://artificialanalysis.ai/api/v2/data/llms/models"
    headers = {"x-api-key": AA_API_KEY}

    requests = require_requests()

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json().get("data", [])

        for model in data:
            creator = model.get("model_creator", {})
            if creator.get("slug") == creator_slug and model.get("slug") == model_name:
                return model

        print(f"Model {creator_slug}/{model_name} not found in Artificial Analysis")
        return None

    except requests.RequestException as e:
        print(f"Error fetching data from Artificial Analysis: {e}")
        return None


def aa_data_to_model_index(
    model_data: Dict[str, Any],
    dataset_name: str = "Artificial Analysis Benchmarks",
    dataset_type: str = "artificial_analysis",
    task_type: str = "evaluation"
) -> List[Dict[str, Any]]:
    """
    Convert Artificial Analysis model data to model-index format.

    Args:
        model_data: Raw model data from AA API
        dataset_name: Dataset name for model-index
        dataset_type: Dataset type identifier
        task_type: Task type for model-index

    Returns:
        Model-index formatted results
    """
    model_name = model_data.get("name", model_data.get("slug", "unknown-model"))
    evaluations = model_data.get("evaluations", {})

    if not evaluations:
        print(f"No evaluations found for model {model_name}")
        return []

    metrics = []
    for key, value in evaluations.items():
        if value is not None:
            metrics.append({
                "name": key.replace("_", " ").title(),
                "type": key,
                "value": value
            })

    results = [{
        "task": {"type": task_type},
        "dataset": {
            "name": dataset_name,
            "type": dataset_type
        },
        "metrics": metrics,
        "source": {
            "name": "Artificial Analysis API",
            "url": "https://artificialanalysis.ai"
        }
    }]

    return results


def import_aa_evaluations(
    creator_slug: str,
    model_name: str,
    repo_id: str
) -> Optional[List[Dict[str, Any]]]:
    """
    Import evaluation results from Artificial Analysis for a model.

    Args:
        creator_slug: Creator identifier in AA
        model_name: Model identifier in AA
        repo_id: Hugging Face repository ID to update

    Returns:
        Model-index formatted results or None if import fails
    """
    model_data = get_aa_model_data(creator_slug, model_name)

    if not model_data:
        return None

    results = aa_data_to_model_index(model_data)
    return results


# ============================================================================
# Model Card Update Functions
# ============================================================================


def update_model_card_with_evaluations(
    repo_id: str,
    results: List[Dict[str, Any]],
    create_pr: bool = False,
    commit_message: Optional[str] = None
) -> bool:
    """
    Update a model card with evaluation results.

    Args:
        repo_id: Hugging Face repository ID
        results: Model-index formatted results
        create_pr: Whether to create a PR instead of direct push
        commit_message: Custom commit message

    Returns:
        True if successful, False otherwise
    """
    try:
        load_env()
        ModelCard = require_model_card()
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise ValueError("HF_TOKEN environment variable is not set")

        # Load existing card
        card = ModelCard.load(repo_id, token=hf_token)

        # Get model name
        model_name = repo_id.split("/")[-1] if "/" in repo_id else repo_id

        # Create or update model-index
        model_index = [{
            "name": model_name,
            "results": results
        }]

        # Merge with existing model-index if present
        if "model-index" in card.data:
            existing = card.data["model-index"]
            if isinstance(existing, list) and existing:
                # Keep existing name if present
                if "name" in existing[0]:
                    model_index[0]["name"] = existing[0]["name"]

                # Merge results
                existing_results = existing[0].get("results", [])
                model_index[0]["results"].extend(existing_results)

        card.data["model-index"] = model_index

        # Prepare commit message
        if not commit_message:
            commit_message = f"Add evaluation results to {model_name}"

        commit_description = (
            "This commit adds structured evaluation results to the model card. "
            "The results are formatted using the model-index specification and "
            "will be displayed in the model card's evaluation widget."
        )

        # Push update
        card.push_to_hub(
            repo_id,
            token=hf_token,
            commit_message=commit_message,
            commit_description=commit_description,
            create_pr=create_pr
        )

        action = "Pull request created" if create_pr else "Model card updated"
        print(f"✓ {action} successfully for {repo_id}")
        return True

    except Exception as e:
        print(f"Error updating model card: {e}")
        return False


def show_evaluations(repo_id: str) -> None:
    """Display current evaluations in a model card."""
    try:
        load_env()
        ModelCard = require_model_card()
        hf_token = os.getenv("HF_TOKEN")
        card = ModelCard.load(repo_id, token=hf_token)

        if "model-index" not in card.data:
            print(f"No model-index found in {repo_id}")
            return

        model_index = card.data["model-index"]

        print(f"\nEvaluations for {repo_id}:")
        print("=" * 60)

        for model_entry in model_index:
            model_name = model_entry.get("name", "Unknown")
            print(f"\nModel: {model_name}")

            results = model_entry.get("results", [])
            for i, result in enumerate(results, 1):
                print(f"\n  Result Set {i}:")

                task = result.get("task", {})
                print(f"    Task: {task.get('type', 'unknown')}")

                dataset = result.get("dataset", {})
                print(f"    Dataset: {dataset.get('name', 'unknown')}")

                metrics = result.get("metrics", [])
                print(f"    Metrics ({len(metrics)}):")
                for metric in metrics:
                    name = metric.get("name", "Unknown")
                    value = metric.get("value", "N/A")
                    print(f"      - {name}: {value}")

                source = result.get("source", {})
                if source:
                    print(f"    Source: {source.get('name', 'Unknown')}")

        print("\n" + "=" * 60)

    except Exception as e:
        print(f"Error showing evaluations: {e}")


def validate_model_index(repo_id: str) -> bool:
    """Validate model-index format in a model card."""
    try:
        load_env()
        ModelCard = require_model_card()
        hf_token = os.getenv("HF_TOKEN")
        card = ModelCard.load(repo_id, token=hf_token)

        if "model-index" not in card.data:
            print(f"✗ No model-index found in {repo_id}")
            return False

        model_index = card.data["model-index"]

        if not isinstance(model_index, list):
            print("✗ model-index must be a list")
            return False

        for i, entry in enumerate(model_index):
            if "name" not in entry:
                print(f"✗ Entry {i} missing 'name' field")
                return False

            if "results" not in entry:
                print(f"✗ Entry {i} missing 'results' field")
                return False

            for j, result in enumerate(entry["results"]):
                if "task" not in result:
                    print(f"✗ Result {j} in entry {i} missing 'task' field")
                    return False

                if "dataset" not in result:
                    print(f"✗ Result {j} in entry {i} missing 'dataset' field")
                    return False

                if "metrics" not in result:
                    print(f"✗ Result {j} in entry {i} missing 'metrics' field")
                    return False

        print(f"✓ Model-index format is valid for {repo_id}")
        return True

    except Exception as e:
        print(f"Error validating model-index: {e}")
        return False


# ============================================================================
# CLI Interface
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Manage evaluation results in Hugging Face model cards.\n\n"
            "Use standard Python or `uv run scripts/evaluation_manager.py ...` "
            "to auto-resolve dependencies from the PEP 723 header."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=dedent(
            """\
            Typical workflows:
              - Inspect tables first:
                  uv run scripts/evaluation_manager.py inspect-tables --repo-id <model>
              - Extract from README (prints YAML by default):
                  uv run scripts/evaluation_manager.py extract-readme --repo-id <model> --table N
              - Apply changes:
                  uv run scripts/evaluation_manager.py extract-readme --repo-id <model> --table N --apply
              - Import from Artificial Analysis:
                  AA_API_KEY=... uv run scripts/evaluation_manager.py import-aa --creator-slug org --model-name slug --repo-id <model>

            Tips:
              - YAML is printed by default; use --apply or --create-pr to write changes.
              - Set HF_TOKEN (and AA_API_KEY for import-aa); .env is loaded automatically if python-dotenv is installed.
              - When multiple tables exist, run inspect-tables then select with --table N.
              - To apply changes (push or PR), rerun extract-readme with --apply or --create-pr.
            """
        ),
    )
    parser.add_argument("--version", action="version", version="evaluation_manager 1.2.0")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Extract from README command
    extract_parser = subparsers.add_parser(
        "extract-readme",
        help="Extract evaluation tables from model README",
        formatter_class=argparse.RawTextHelpFormatter,
        description="Parse README tables into model-index YAML. Default behavior prints YAML; use --apply/--create-pr to write changes.",
        epilog=dedent(
            """\
            Examples:
              uv run scripts/evaluation_manager.py extract-readme --repo-id username/model
              uv run scripts/evaluation_manager.py extract-readme --repo-id username/model --table 2 --model-column-index 3
              uv run scripts/evaluation_manager.py extract-readme --repo-id username/model --table 2 --model-name-override \"**Model 7B**\"  # exact header text
              uv run scripts/evaluation_manager.py extract-readme --repo-id username/model --table 2 --create-pr

            Apply changes:
              - Default: prints YAML to stdout (no writes).
              - Add --apply to push directly, or --create-pr to open a PR.
            Model selection:
              - Preferred: --model-column-index <header index shown by inspect-tables>
              - If using --model-name-override, copy the column header text exactly.
            """
        ),
    )
    extract_parser.add_argument("--repo-id", type=str, required=True, help="HF repository ID")
    extract_parser.add_argument("--table", type=int, help="Table number (1-indexed, from inspect-tables output)")
    extract_parser.add_argument("--model-column-index", type=int, help="Preferred: column index from inspect-tables output (exact selection)")
    extract_parser.add_argument("--model-name-override", type=str, help="Exact column header/model name for comparison/transpose tables (when index is not used)")
    extract_parser.add_argument("--task-type", type=str, default="text-generation", help="Sets model-index task.type (e.g., text-generation, summarization)")
    extract_parser.add_argument("--dataset-name", type=str, default="Benchmarks", help="Dataset name")
    extract_parser.add_argument("--dataset-type", type=str, default="benchmark", help="Dataset type")
    extract_parser.add_argument("--create-pr", action="store_true", help="Create PR instead of direct push")
    extract_parser.add_argument("--apply", action="store_true", help="Apply changes (default is to print YAML only)")
    extract_parser.add_argument("--dry-run", action="store_true", help="Preview YAML without updating (default)")

    # Import from AA command
    aa_parser = subparsers.add_parser(
        "import-aa",
        help="Import evaluation scores from Artificial Analysis",
        formatter_class=argparse.RawTextHelpFormatter,
        description="Fetch scores from Artificial Analysis API and write them into model-index.",
        epilog=dedent(
            """\
            Examples:
              AA_API_KEY=... uv run scripts/evaluation_manager.py import-aa --creator-slug anthropic --model-name claude-sonnet-4 --repo-id username/model
              uv run scripts/evaluation_manager.py import-aa --creator-slug openai --model-name gpt-4o --repo-id username/model --create-pr

            Requires: AA_API_KEY in env (or .env if python-dotenv installed).
            """
        ),
    )
    aa_parser.add_argument("--creator-slug", type=str, required=True, help="AA creator slug")
    aa_parser.add_argument("--model-name", type=str, required=True, help="AA model name")
    aa_parser.add_argument("--repo-id", type=str, required=True, help="HF repository ID")
    aa_parser.add_argument("--create-pr", action="store_true", help="Create PR instead of direct push")

    # Show evaluations command
    show_parser = subparsers.add_parser(
        "show",
        help="Display current evaluations in model card",
        formatter_class=argparse.RawTextHelpFormatter,
        description="Print model-index content from the model card (requires HF_TOKEN for private repos).",
    )
    show_parser.add_argument("--repo-id", type=str, required=True, help="HF repository ID")

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate model-index format",
        formatter_class=argparse.RawTextHelpFormatter,
        description="Schema sanity check for model-index section of the card.",
    )
    validate_parser.add_argument("--repo-id", type=str, required=True, help="HF repository ID")

    # Inspect tables command
    inspect_parser = subparsers.add_parser(
        "inspect-tables",
        help="Inspect tables in README → outputs suggested extract-readme command",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Workflow:
  1. inspect-tables     → see table structure, columns, and table numbers
  2. extract-readme     → run with --table N (from step 1); YAML prints by default
  3. apply changes      → rerun extract-readme with --apply or --create-pr

Reminder:
  - Preferred: use --model-column-index <index>. If needed, use --model-name-override with the exact column header text.
"""
    )
    inspect_parser.add_argument("--repo-id", type=str, required=True, help="HF repository ID")

    # Get PRs command
    prs_parser = subparsers.add_parser(
        "get-prs",
        help="List open pull requests for a model repository",
        formatter_class=argparse.RawTextHelpFormatter,
        description="Check for existing open PRs before creating new ones to avoid duplicates.",
        epilog=dedent(
            """\
            Examples:
              uv run scripts/evaluation_manager.py get-prs --repo-id "allenai/Olmo-3-32B-Think"

            IMPORTANT: Always run this before using --create-pr to avoid duplicate PRs.
            """
        ),
    )
    prs_parser.add_argument("--repo-id", type=str, required=True, help="HF repository ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        # Execute command
        if args.command == "extract-readme":
            results = extract_evaluations_from_readme(
                repo_id=args.repo_id,
                task_type=args.task_type,
                dataset_name=args.dataset_name,
                dataset_type=args.dataset_type,
                model_name_override=args.model_name_override,
                table_index=args.table,
                model_column_index=args.model_column_index
            )

            if not results:
                print("No evaluations extracted")
                return

            apply_changes = args.apply or args.create_pr

            # Default behavior: print YAML (dry-run)
            yaml = require_yaml()
            print("\nExtracted evaluations (YAML):")
            print(
                yaml.dump(
                    {"model-index": [{"name": args.repo_id.split('/')[-1], "results": results}]},
                    sort_keys=False
                )
            )

            if apply_changes:
                if args.model_name_override and args.model_column_index is not None:
                    print("Note: --model-column-index takes precedence over --model-name-override.")
                update_model_card_with_evaluations(
                    repo_id=args.repo_id,
                    results=results,
                    create_pr=args.create_pr,
                    commit_message="Extract evaluation results from README"
                )

        elif args.command == "import-aa":
            results = import_aa_evaluations(
                creator_slug=args.creator_slug,
                model_name=args.model_name,
                repo_id=args.repo_id
            )

            if not results:
                print("No evaluations imported")
                return

            update_model_card_with_evaluations(
                repo_id=args.repo_id,
                results=results,
                create_pr=args.create_pr,
                commit_message=f"Add Artificial Analysis evaluations for {args.model_name}"
            )

        elif args.command == "show":
            show_evaluations(args.repo_id)

        elif args.command == "validate":
            validate_model_index(args.repo_id)

        elif args.command == "inspect-tables":
            inspect_tables(args.repo_id)

        elif args.command == "get-prs":
            list_open_prs(args.repo_id)
    except ModuleNotFoundError as exc:
        # Surface dependency hints cleanly when user only needs help output
        print(exc)
    except Exception as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
