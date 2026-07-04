# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "huggingface-hub>=0.26.0",
#     "python-dotenv>=1.2.1",
# ]
# ///

"""
Submit evaluation jobs using the `hf jobs uv run` CLI.

This wrapper constructs the appropriate command to execute the local
`inspect_eval_uv.py` script on Hugging Face Jobs with the requested hardware.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from huggingface_hub import get_token
from dotenv import load_dotenv

load_dotenv()


SCRIPT_PATH = Path(__file__).with_name("inspect_eval_uv.py").resolve()


def create_eval_job(
    model_id: str,
    task: str,
    hardware: str = "cpu-basic",
    hf_token: Optional[str] = None,
    limit: Optional[int] = None,
) -> None:
    """
    Submit an evaluation job using the Hugging Face Jobs CLI.
    """
    token = hf_token or os.getenv("HF_TOKEN") or get_token()
    if not token:
        raise ValueError("HF_TOKEN is required. Set it in environment or pass as argument.")

    if not SCRIPT_PATH.exists():
        raise FileNotFoundError(f"Script not found at {SCRIPT_PATH}")

    print(f"Preparing evaluation job for {model_id} on task {task} (hardware: {hardware})")

    cmd = [
        "hf",
        "jobs",
        "uv",
        "run",
        str(SCRIPT_PATH),
        "--flavor",
        hardware,
        "--secrets",
        f"HF_TOKEN={token}",
        "--",
        "--model",
        model_id,
        "--task",
        task,
    ]

    if limit:
        cmd.extend(["--limit", str(limit)])

    print("Executing:", " ".join(cmd))

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        print("hf jobs command failed", file=sys.stderr)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Run inspect-ai evaluations on Hugging Face Jobs")
    parser.add_argument("--model", required=True, help="Model ID (e.g. Qwen/Qwen3-0.6B)")
    parser.add_argument("--task", required=True, help="Inspect task (e.g. mmlu, gsm8k)")
    parser.add_argument("--hardware", default="cpu-basic", help="Hardware flavor (e.g. t4-small, a10g-small)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of samples to evaluate")

    args = parser.parse_args()

    create_eval_job(
        model_id=args.model,
        task=args.task,
        hardware=args.hardware,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
