#!/usr/bin/env python3
"""
Hackers Leaderboard - Gradio app for displaying engagement from hf-skills org.

Reads leaderboard data from the hf-skills/hackers-leaderboard dataset.
Run collect_points.py separately to update the dataset.

Usage:
    python app.py
"""

from __future__ import annotations

import json

import gradio as gr
import requests

TABLE_HEADERS = [
    "Rank",
    "Username",
    "Points",
    "💬 Discussions",
]

TABLE_DATATYPES = [
    "number",
    "markdown",
    "number",
]


DATASET_REPO = "hf-skills/hackers-leaderboard"
LEADERBOARD_URL = f"https://huggingface.co/datasets/{DATASET_REPO}/raw/main/data/leaderboard.jsonl"
METADATA_URL = f"https://huggingface.co/datasets/{DATASET_REPO}/raw/main/data/metadata.json"


def format_username(username: str) -> str:
    """Format username as a clickable link."""
    return f"[{username}](https://huggingface.co/{username})"


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
        for i, entry in enumerate(leaderboard, 1):
            rows.append(
                [
                    i,
                    format_username(entry["username"]),
                    entry["prs_opened"],
                ]
            )

        status = "\n".join(
            [
                f"**Data from:** [{DATASET_REPO}](https://huggingface.co/datasets/{DATASET_REPO})",
                f"**Last updated:** {metadata.get('generated_at', 'unknown')}",
                f"**Participants:** {metadata.get('total_participants', len(leaderboard))}",
                f"**Total points:** {metadata.get('total_points', sum(e['total_points'] for e in leaderboard))}",
            ]
        )

        return status, rows

    except Exception as e:
        return f"❌ Failed to load leaderboard: {e}", []


with gr.Blocks() as demo:
    gr.HTML(
        """
        <div class="subtitle">
            <img src="https://github.com/huggingface/skills/raw/main/assets/banner.png" alt="Humanity's Last Hackathon (of 2025)" width="100%">
        </div>
        <div class="leaderboard-title"><h1>🏆 Humanity's Last Hackathon Leaderboard</h1></div>
        """
    )

    leaderboard_table = gr.Dataframe(
        headers=TABLE_HEADERS,
        datatype=TABLE_DATATYPES,
        interactive=False,
        wrap=True,
    )

    status_box = gr.Markdown("Click refresh to load the leaderboard...")
    
    demo.load(
        refresh_handler,
        outputs=[status_box, leaderboard_table],
    )

    gr.Markdown(
        """
        ---
        
        **Links:**
        - [Join hf-skills](https://huggingface.co/organizations/hf-skills/share/KrqrmBxkETjvevFbfkXeezcyMbgMjjMaOp)
        - [Quest Instructions](https://github.com/huggingface/skills/tree/main/apps/quests)
        - [GitHub Repository](https://github.com/huggingface/skills)
        """
    )

if __name__ == "__main__":
    demo.launch()
