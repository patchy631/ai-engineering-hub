#!/usr/bin/env python3
"""
Evals Leaderboard - Gradio app for displaying model evaluation scores.

Reads leaderboard data from the hf-skills/evals-leaderboard dataset.
Run collect_evals.py separately to update the dataset.

Usage:
    python app.py
"""

from __future__ import annotations

import json

import gradio as gr
import requests

TABLE_HEADERS = [
    "Model",
    "Benchmark",
    "Score",
    "Source",
]

TABLE_DATATYPES = [
    "markdown",
    "text",
    "number",
    "markdown",
]


DATASET_REPO = "hf-skills/evals-leaderboard"
LEADERBOARD_URL = f"https://huggingface.co/datasets/{DATASET_REPO}/raw/main/data/leaderboard.jsonl"
METADATA_URL = f"https://huggingface.co/datasets/{DATASET_REPO}/raw/main/data/metadata.json"


def format_model_link(model_id: str) -> str:
    """Format model ID as a clickable link."""
    return f"[{model_id}](https://huggingface.co/{model_id})"


def format_source_link(source_type: str, contributor: str, source_url: str) -> str:
    """Format source as a clickable link."""
    return f"{source_type} by [{contributor}]({source_url})"


def fetch_leaderboard() -> tuple[list[dict], dict]:
    """Fetch leaderboard data from the HF dataset."""
    # Fetch leaderboard JSONL
    resp = requests.get(LEADERBOARD_URL, timeout=30)
    resp.raise_for_status()
    leaderboard = [json.loads(line) for line in resp.text.strip().split("\n") if line]

    # Fetch metadata
    resp = requests.get(METADATA_URL, timeout=30)
    resp.raise_for_status()
    metadata = resp.json()

    return leaderboard, metadata


def refresh_handler() -> tuple[str, list[list]]:
    """Refresh the leaderboard data from the dataset."""
    try:
        leaderboard, metadata = fetch_leaderboard()

        # Build table rows
        rows = []
        for entry in leaderboard:
            rows.append(
                [
                    format_model_link(entry["model_id"]),
                    entry["benchmark"],
                    entry["score"],
                    format_source_link(
                        entry["source_type"],
                        entry["contributor"],
                        entry["source_url"],
                    ),
                ]
            )

        status = "\n".join(
            [
                f"**Data from:** [{DATASET_REPO}](https://huggingface.co/datasets/{DATASET_REPO})",
                f"**Last updated:** {metadata.get('generated_at', 'unknown')}",
                f"**Models with scores:** {metadata.get('models_with_scores', 'unknown')}",
                f"**Total entries:** {metadata.get('total_entries', len(leaderboard))}",
            ]
        )

        return status, rows

    except Exception as e:
        return f"❌ Failed to load leaderboard: {e}", []


with gr.Blocks() as demo:
    gr.Markdown(
        """
        # 📊 HF Evaluation Leaderboard
        
        Shows MMLU, BigCodeBench, and ARC MC scores pulled from model-index
        metadata or their pull requests for trending text-generation models.
        """
    )

    status_box = gr.Markdown("Loading leaderboard...")

    leaderboard_table = gr.Dataframe(
        headers=TABLE_HEADERS,
        datatype=TABLE_DATATYPES,
        interactive=False,
        wrap=True,
    )

    demo.load(
        refresh_handler,
        outputs=[status_box, leaderboard_table],
    )

    gr.Markdown(
        f"""
        ---
        
        **Links:**
        - [Dataset: {DATASET_REPO}](https://huggingface.co/datasets/{DATASET_REPO})
        - [GitHub Repository](https://github.com/huggingface/skills)
        """
    )


if __name__ == "__main__":
    demo.launch()
