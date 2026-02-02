# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "huggingface-hub>=0.26.0",
#     "python-dotenv>=1.2.1",
# ]
# ///

"""
Submit vLLM-based evaluation jobs using the `hf jobs uv run` CLI.

This wrapper constructs the appropriate command to execute vLLM evaluation scripts
(lighteval or inspect-ai) on Hugging Face Jobs with GPU hardware.

Unlike run_eval_job.py (which uses inference providers/APIs), this script runs
models directly on the job's GPU using vLLM or HuggingFace Transformers.

Usage:
    python run_vllm_eval_job.py \\
        --model meta-llama/Llama-3.2-1B \\
        --task mmlu \\
        --framework lighteval \\
        --hardware a10g-small
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from huggingface_hub import get_token
from dotenv import load_dotenv

load_dotenv()

# Script paths for different evaluation frameworks
SCRIPT_DIR = Path(__file__).parent.resolve()
LIGHTEVAL_SCRIPT = SCRIPT_DIR / "lighteval_vllm_uv.py"
INSPECT_SCRIPT = SCRIPT_DIR / "inspect_vllm_uv.py"

# Hardware flavor recommendations for different model sizes
HARDWARE_RECOMMENDATIONS = {
    "small": "t4-small",       # < 3B parameters
    "medium": "a10g-small",    # 3B - 13B parameters
    "large": "a10g-large",     # 13B - 34B parameters
    "xlarge": "a100-large",    # 34B+ parameters
}


def estimate_hardware(model_id: str) -> str:
    """
    Estimate appropriate hardware based on model ID naming conventions.
    
    Returns a hardware flavor recommendation.
    """
    model_lower = model_id.lower()
    
    # Check for explicit size indicators in model name
    if any(x in model_lower for x in ["70b", "72b", "65b"]):
        return "a100-large"
    elif any(x in model_lower for x in ["34b", "33b", "32b", "30b"]):
        return "a10g-large"
    elif any(x in model_lower for x in ["13b", "14b", "7b", "8b"]):
        return "a10g-small"
    elif any(x in model_lower for x in ["3b", "2b", "1b", "0.5b", "small", "mini"]):
        return "t4-small"
    
    # Default to medium hardware
    return "a10g-small"


def create_lighteval_job(
    model_id: str,
    tasks: str,
    hardware: str,
    hf_token: Optional[str] = None,
    max_samples: Optional[int] = None,
    backend: str = "vllm",
    batch_size: int = 1,
    tensor_parallel_size: int = 1,
    trust_remote_code: bool = False,
    use_chat_template: bool = False,
) -> None:
    """
    Submit a lighteval evaluation job on HuggingFace Jobs.
    """
    token = hf_token or os.getenv("HF_TOKEN") or get_token()
    if not token:
        raise ValueError("HF_TOKEN is required. Set it in environment or pass as argument.")

    if not LIGHTEVAL_SCRIPT.exists():
        raise FileNotFoundError(f"Script not found at {LIGHTEVAL_SCRIPT}")

    print(f"Preparing lighteval job for {model_id}")
    print(f"  Tasks: {tasks}")
    print(f"  Backend: {backend}")
    print(f"  Hardware: {hardware}")

    cmd = [
        "hf", "jobs", "uv", "run",
        str(LIGHTEVAL_SCRIPT),
        "--flavor", hardware,
        "--secrets", f"HF_TOKEN={token}",
        "--",
        "--model", model_id,
        "--tasks", tasks,
        "--backend", backend,
        "--batch-size", str(batch_size),
        "--tensor-parallel-size", str(tensor_parallel_size),
    ]

    if max_samples:
        cmd.extend(["--max-samples", str(max_samples)])

    if trust_remote_code:
        cmd.append("--trust-remote-code")

    if use_chat_template:
        cmd.append("--use-chat-template")

    print(f"\nExecuting: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        print("hf jobs command failed", file=sys.stderr)
        raise


def create_inspect_job(
    model_id: str,
    task: str,
    hardware: str,
    hf_token: Optional[str] = None,
    limit: Optional[int] = None,
    backend: str = "vllm",
    tensor_parallel_size: int = 1,
    trust_remote_code: bool = False,
) -> None:
    """
    Submit an inspect-ai evaluation job on HuggingFace Jobs.
    """
    token = hf_token or os.getenv("HF_TOKEN") or get_token()
    if not token:
        raise ValueError("HF_TOKEN is required. Set it in environment or pass as argument.")

    if not INSPECT_SCRIPT.exists():
        raise FileNotFoundError(f"Script not found at {INSPECT_SCRIPT}")

    print(f"Preparing inspect-ai job for {model_id}")
    print(f"  Task: {task}")
    print(f"  Backend: {backend}")
    print(f"  Hardware: {hardware}")

    cmd = [
        "hf", "jobs", "uv", "run",
        str(INSPECT_SCRIPT),
        "--flavor", hardware,
        "--secrets", f"HF_TOKEN={token}",
        "--",
        "--model", model_id,
        "--task", task,
        "--backend", backend,
        "--tensor-parallel-size", str(tensor_parallel_size),
    ]

    if limit:
        cmd.extend(["--limit", str(limit)])

    if trust_remote_code:
        cmd.append("--trust-remote-code")

    print(f"\nExecuting: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        print("hf jobs command failed", file=sys.stderr)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Submit vLLM-based evaluation jobs to HuggingFace Jobs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run lighteval with vLLM on A10G GPU
  python run_vllm_eval_job.py \\
      --model meta-llama/Llama-3.2-1B \\
      --task "leaderboard|mmlu|5" \\
      --framework lighteval \\
      --hardware a10g-small

  # Run inspect-ai on larger model with multi-GPU
  python run_vllm_eval_job.py \\
      --model meta-llama/Llama-3.2-70B \\
      --task mmlu \\
      --framework inspect \\
      --hardware a100-large \\
      --tensor-parallel-size 4

  # Auto-detect hardware based on model size
  python run_vllm_eval_job.py \\
      --model meta-llama/Llama-3.2-1B \\
      --task mmlu \\
      --framework inspect

  # Run with HF Transformers backend (instead of vLLM)
  python run_vllm_eval_job.py \\
      --model microsoft/phi-2 \\
      --task mmlu \\
      --framework inspect \\
      --backend hf

Hardware flavors:
  - t4-small: T4 GPU, good for models < 3B
  - a10g-small: A10G GPU, good for models 3B-13B
  - a10g-large: A10G GPU, good for models 13B-34B
  - a100-large: A100 GPU, good for models 34B+

Frameworks:
  - lighteval: HuggingFace's lighteval library
  - inspect: UK AI Safety's inspect-ai library

Task formats:
  - lighteval: "suite|task|num_fewshot" (e.g., "leaderboard|mmlu|5")
  - inspect: task name (e.g., "mmlu", "gsm8k")
        """,
    )

    parser.add_argument(
        "--model",
        required=True,
        help="HuggingFace model ID (e.g., meta-llama/Llama-3.2-1B)",
    )
    parser.add_argument(
        "--task",
        required=True,
        help="Evaluation task (format depends on framework)",
    )
    parser.add_argument(
        "--framework",
        choices=["lighteval", "inspect"],
        default="lighteval",
        help="Evaluation framework to use (default: lighteval)",
    )
    parser.add_argument(
        "--hardware",
        default=None,
        help="Hardware flavor (auto-detected if not specified)",
    )
    parser.add_argument(
        "--backend",
        choices=["vllm", "hf", "accelerate"],
        default="vllm",
        help="Model backend (default: vllm)",
    )
    parser.add_argument(
        "--limit",
        "--max-samples",
        type=int,
        default=None,
        dest="limit",
        help="Limit number of samples to evaluate",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help="Batch size for evaluation (lighteval only)",
    )
    parser.add_argument(
        "--tensor-parallel-size",
        type=int,
        default=1,
        help="Number of GPUs for tensor parallelism",
    )
    parser.add_argument(
        "--trust-remote-code",
        action="store_true",
        help="Allow executing remote code from model repository",
    )
    parser.add_argument(
        "--use-chat-template",
        action="store_true",
        help="Apply chat template (lighteval only)",
    )

    args = parser.parse_args()

    # Auto-detect hardware if not specified
    hardware = args.hardware or estimate_hardware(args.model)
    print(f"Using hardware: {hardware}")

    # Map backend names between frameworks
    backend = args.backend
    if args.framework == "lighteval" and backend == "hf":
        backend = "accelerate"  # lighteval uses "accelerate" for HF backend

    if args.framework == "lighteval":
        create_lighteval_job(
            model_id=args.model,
            tasks=args.task,
            hardware=hardware,
            max_samples=args.limit,
            backend=backend,
            batch_size=args.batch_size,
            tensor_parallel_size=args.tensor_parallel_size,
            trust_remote_code=args.trust_remote_code,
            use_chat_template=args.use_chat_template,
        )
    else:
        create_inspect_job(
            model_id=args.model,
            task=args.task,
            hardware=hardware,
            limit=args.limit,
            backend=backend if backend != "accelerate" else "hf",
            tensor_parallel_size=args.tensor_parallel_size,
            trust_remote_code=args.trust_remote_code,
        )


if __name__ == "__main__":
    main()

