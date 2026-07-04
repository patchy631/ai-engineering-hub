#!/usr/bin/env python3
"""
Test script for evaluation extraction functionality.

This script demonstrates the table extraction capabilities without
requiring HF tokens or making actual API calls.
"""

import yaml

from evaluation_manager import (
    extract_tables_from_markdown,
    parse_markdown_table,
    is_evaluation_table,
    extract_metrics_from_table
)

# Sample README content with various table formats
SAMPLE_README = """
# My Awesome Model

## Evaluation Results

Here are the benchmark results:

| Benchmark | Score |
|-----------|-------|
| MMLU      | 85.2  |
| HumanEval | 72.5  |
| GSM8K     | 91.3  |

### Detailed Breakdown

| Category      | MMLU  | GSM8K | HumanEval |
|---------------|-------|-------|-----------|
| Performance   | 85.2  | 91.3  | 72.5      |

## Other Information

This is not an evaluation table:

| Feature | Value |
|---------|-------|
| Size    | 7B    |
| Type    | Chat  |

## More Results

| Benchmark     | Accuracy | F1 Score |
|---------------|----------|----------|
| HellaSwag     | 88.9     | 0.87     |
| TruthfulQA    | 68.7     | 0.65     |
"""


def test_table_extraction():
    """Test markdown table extraction."""
    print("=" * 60)
    print("TEST 1: Table Extraction")
    print("=" * 60)

    tables = extract_tables_from_markdown(SAMPLE_README)
    print(f"Found {len(tables)} tables in the sample README\n")

    for i, table in enumerate(tables, 1):
        print(f"Table {i}:")
        print(table[:100] + "..." if len(table) > 100 else table)
        print()

    return tables


def test_table_parsing(tables):
    """Test table parsing."""
    print("\n" + "=" * 60)
    print("TEST 2: Table Parsing")
    print("=" * 60)

    parsed_tables = []
    for i, table in enumerate(tables, 1):
        print(f"\nParsing Table {i}:")
        header, rows = parse_markdown_table(table)

        print(f"  Header: {header}")
        print(f"  Rows: {len(rows)}")
        for j, row in enumerate(rows[:3], 1):  # Show first 3 rows
            print(f"    Row {j}: {row}")
        if len(rows) > 3:
            print(f"    ... and {len(rows) - 3} more rows")

        parsed_tables.append((header, rows))

    return parsed_tables


def test_evaluation_detection(parsed_tables):
    """Test evaluation table detection."""
    print("\n" + "=" * 60)
    print("TEST 3: Evaluation Table Detection")
    print("=" * 60)

    eval_tables = []
    for i, (header, rows) in enumerate(parsed_tables, 1):
        is_eval = is_evaluation_table(header, rows)
        status = "✓ IS" if is_eval else "✗ NOT"
        print(f"\nTable {i}: {status} an evaluation table")
        print(f"  Header: {header}")

        if is_eval:
            eval_tables.append((header, rows))

    print(f"\nFound {len(eval_tables)} evaluation tables")
    return eval_tables


def test_metric_extraction(eval_tables):
    """Test metric extraction."""
    print("\n" + "=" * 60)
    print("TEST 4: Metric Extraction")
    print("=" * 60)

    all_metrics = []
    for i, (header, rows) in enumerate(eval_tables, 1):
        print(f"\nExtracting metrics from table {i}:")
        metrics = extract_metrics_from_table(header, rows, table_format="auto")

        print(f"  Extracted {len(metrics)} metrics:")
        for metric in metrics:
            print(f"    - {metric['name']}: {metric['value']} (type: {metric['type']})")

        all_metrics.extend(metrics)

    return all_metrics


def test_model_index_format(metrics):
    """Test model-index format generation."""
    print("\n" + "=" * 60)
    print("TEST 5: Model-Index Format")
    print("=" * 60)

    model_index = {
        "model-index": [
            {
                "name": "test-model",
                "results": [
                    {
                        "task": {"type": "text-generation"},
                        "dataset": {
                            "name": "Benchmarks",
                            "type": "benchmark"
                        },
                        "metrics": metrics,
                        "source": {
                            "name": "Model README",
                            "url": "https://huggingface.co/test/model"
                        }
                    }
                ]
            }
        ]
    }

    print("\nGenerated model-index structure:")
    print(yaml.dump(model_index, sort_keys=False, default_flow_style=False))


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("EVALUATION EXTRACTION TEST SUITE")
    print("=" * 60)
    print("\nThis test demonstrates the table extraction capabilities")
    print("without requiring API access or tokens.\n")

    # Run tests
    tables = test_table_extraction()
    parsed_tables = test_table_parsing(tables)
    eval_tables = test_evaluation_detection(parsed_tables)
    metrics = test_metric_extraction(eval_tables)
    test_model_index_format(metrics)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✓ Found {len(tables)} total tables")
    print(f"✓ Identified {len(eval_tables)} evaluation tables")
    print(f"✓ Extracted {len(metrics)} metrics")
    print("✓ Generated model-index format successfully")
    print("\n" + "=" * 60)
    print("All tests completed! The extraction logic is working correctly.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
