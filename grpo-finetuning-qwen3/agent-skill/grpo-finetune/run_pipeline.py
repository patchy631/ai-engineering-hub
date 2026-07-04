"""GRPO fine-tuning pipeline.

Runs: validate reward -> upload dataset -> GRPO training -> post-training eval -> sample inference.

Keys are loaded from .env in the current directory.
Reward is loaded from ./reward.py by default, or pass --reward <path>.

Usage:
    python run_pipeline.py \
        --train ./train_prompts.jsonl \
        --eval  ./eval_prompts.jsonl \
        --task  invoice-extraction \
        --output-id invoice-extractor-v1
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from generate_reward import load_reward, validate_reward

BASE_MODEL        = "accounts/fireworks/models/qwen3-8b"
TRAINING_SHAPE_ID = "accounts/fireworks/trainingShapes/qwen3-8b-128k"
TOKENIZER_MODEL   = "Qwen/Qwen3-8B"


def banner(title):
    print(f"\n{'=' * 52}\n{title}\n{'=' * 52}", flush=True)


def checkpoint(msg):
    print(f"\n>>> {msg}\n", flush=True)


def make_client():
    from openai import OpenAI
    return OpenAI(api_key=os.environ["FIREWORKS_API_KEY"],
                  base_url="https://api.fireworks.ai/inference/v1")


def run_eval(client, model_id, eval_file, score_fn):
    data = [json.loads(l) for l in open(eval_file)]
    scores = []
    for i, entry in enumerate(data):
        msgs = [m for m in entry["messages"] if m["role"] != "assistant"]
        msgs = [{**m, "content": m["content"] + " /no-think"} if m["role"] == "system" else m
                for m in msgs]
        row = entry.get("row") or entry.get("meta")
        try:
            resp = client.chat.completions.create(model=model_id, messages=msgs,
                                                  temperature=0.0, max_tokens=512)
            content = resp.choices[0].message.content
            if "</think>" in content:
                content = content.split("</think>")[-1].strip()
            s = score_fn(content, row)
        except Exception as e:
            print(f"  error on prompt {i}: {e}", flush=True)
            s = 0.0
        scores.append(s)
        if (i + 1) % 10 == 0:
            acc = sum(1 for x in scores if x == 1.0) / len(scores)
            print(f"  {i+1}/{len(data)}  {acc:.1%}", flush=True)
    accuracy = sum(1 for x in scores if x == 1.0) / len(scores)
    return accuracy


def main():
    load_dotenv()

    ap = argparse.ArgumentParser()
    ap.add_argument("--train",     required=True,            help="training .jsonl")
    ap.add_argument("--eval",      required=True,            help="eval .jsonl")
    ap.add_argument("--task",      default="grpo-task",      help="short task name")
    ap.add_argument("--output-id", default="grpo-task-v1",   help="output model/deployment id")
    ap.add_argument("--reward",    default="./reward.py",    help="reward function")
    ap.add_argument("--invoices",  default="./invoices.txt", help="sample invoices for demo")
    args = ap.parse_args()

    t0 = time.time()

    banner(f"GRPO FINE-TUNE  ·  {args.task}")
    print(f"train:  {args.train}\neval:   {args.eval}\noutput: {args.output_id}", flush=True)

    # 0. validate reward
    banner("STEP 0 · validate reward")
    if validate_reward(args.reward) != 0:
        print("\nFix reward.py and re-run.", flush=True)
        return 1
    score_fn = load_reward(args.reward).score

    account_id = os.environ["FIREWORKS_ACCOUNT_ID"]
    deployment  = f"accounts/{account_id}/deployments/{args.output_id}"
    dataset_id  = f"{args.task}-dataset"

    # 1. upload dataset
    banner("STEP 1 · upload dataset")
    from fireworks import Fireworks
    fw = Fireworks(api_key=os.environ["FIREWORKS_API_KEY"])
    train_path = Path(args.train)
    row_count = sum(1 for _ in open(train_path))
    try:
        ds = fw.datasets.get(dataset_id=dataset_id)
        if ds.state == "READY":
            checkpoint(f"Dataset ready  ·  {row_count} prompts")
        else:
            print("Waiting for dataset", end="", flush=True)
            while True:
                ds = fw.datasets.get(dataset_id=dataset_id)
                if ds.state == "READY":
                    print()
                    break
                print(".", end="", flush=True)
                time.sleep(3)
            checkpoint(f"Dataset ready  ·  {row_count} prompts")
    except Exception:
        print(f"Uploading {row_count} prompts...", flush=True)
        fw.datasets.create(dataset_id=dataset_id, dataset={"exampleCount": str(row_count)})
        fw.datasets.upload(dataset_id=dataset_id, file=train_path)
        print("Waiting for dataset", end="", flush=True)
        while True:
            ds = fw.datasets.get(dataset_id=dataset_id)
            if ds.state == "READY":
                print()
                break
            print(".", end="", flush=True)
            time.sleep(3)
        checkpoint(f"Dataset ready  ·  {row_count} prompts")

    # 2. GRPO training
    banner("STEP 2 · GRPO training")
    import nest_asyncio
    nest_asyncio.apply()
    import asyncio
    asyncio.run = lambda coro, **kw: asyncio.get_event_loop().run_until_complete(coro)
    sys.path.insert(0, "./cookbook/training")
    import training.recipes.rl_loop as rl_loop
    from training.recipes.rl_loop import Config, main as rl_main
    from training.utils import DeployConfig, InfraConfig, WeightSyncConfig

    rl_loop.reward_fn = lambda completion, row: score_fn(completion, row)

    cfg = Config(
        log_path=f"./{args.task}-logs",
        base_model=BASE_MODEL,
        dataset=args.train,
        max_rows=200, epochs=1, completions_per_prompt=4,
        max_completion_tokens=256, temperature=1.0, max_seq_len=4096,
        policy_loss="grpo",
        output_model_id=args.output_id,
        infra=InfraConfig(training_shape_id=TRAINING_SHAPE_ID),
        deployment=DeployConfig(deployment_id=args.output_id, tokenizer_model=TOKENIZER_MODEL),
        weight_sync=WeightSyncConfig(weight_sync_interval=1, dcp_save_interval=50),
    )
    checkpoint("Training started on Fireworks GPUs")
    rl_main(cfg)
    checkpoint(f"Training complete  ·  model deployed to {deployment}")

    # 3. post-training eval
    banner("STEP 3 · eval")
    finetuned = run_eval(make_client(), deployment, args.eval, score_fn)
    checkpoint(f"Fine-tuned model  ·  {finetuned:.1%} accuracy")

    # summary
    banner("RESULTS")
    print(f"  accuracy   {finetuned:.1%}", flush=True)
    print(f"  model      {deployment}", flush=True)
    print(f"  elapsed    {time.time() - t0:.0f}s", flush=True)

    # 4. sample inference
    invoices_path = Path(args.invoices)
    if invoices_path.exists():
        banner("STEP 4 · sample inference")
        print("Running the fine-tuned model on sample invoices...\n", flush=True)
        time.sleep(1)
        subprocess.run([sys.executable,
                        "agent-skill/grpo-finetune/agent_demo.py",
                        str(invoices_path),
                        "--deployment", deployment])
    else:
        print(f"\nNo invoices file found at {invoices_path} — skipping demo.", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
