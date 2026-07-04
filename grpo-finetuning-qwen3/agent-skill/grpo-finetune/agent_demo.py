"""
agent_demo.py
-------------
Runs the fine-tuned invoice extraction model on sample invoices.

Usage:
    python agent_demo.py invoices.txt
    python agent_demo.py invoices.txt --deployment accounts/myaccount/deployments/invoice-extractor-v1
"""

import argparse
import json
import os
import re
import sys
import time

from dotenv import load_dotenv
from openai import OpenAI

REQUIRED_FIELDS = {"vendor", "date", "amount", "currency"}

GREEN  = "\033[32m"
RED    = "\033[31m"
CYAN   = "\033[36m"
GRAY   = "\033[90m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
ORANGE = "\033[38;5;214m"
YELLOW = "\033[38;5;226m"

DIVIDER     = f"{GRAY}{'─' * 72}{RESET}"
DIVIDER_MID = f"{GRAY}{'╌' * 72}{RESET}"

BOX_INNER = 66


def vlen(s):
    return len(re.sub(r'\033\[[0-9;]*m', '', s))


def box_line(content):
    pad = BOX_INNER - vlen(content)
    return f"  {ORANGE}║{RESET}{content}{' ' * pad}{ORANGE}║{RESET}"


def print_banner(deployment):
    lines = [
        f"  {ORANGE}╔{'═' * BOX_INNER}╗{RESET}",
        box_line(f"   {BOLD}grpo-extract{RESET}  {GRAY}·{RESET}  {YELLOW}skill v1.0{RESET}"),
        box_line(f""),
        box_line(f"   {GRAY}Model    {RESET} {CYAN}Qwen3-8B fine-tuned via GRPO{RESET}"),
        box_line(f"   {GRAY}Provider {RESET} {CYAN}Fireworks AI{RESET}"),
        box_line(f"   {GRAY}Endpoint {RESET} {CYAN}{deployment}{RESET}"),
        box_line(f"   {GRAY}Schema   {RESET} {CYAN}vendor  ·  date  ·  amount  ·  currency{RESET}"),
        f"  {ORANGE}╚{'═' * BOX_INNER}╝{RESET}",
    ]
    print()
    for line in lines:
        print(line)
        time.sleep(0.06)
    print()


def extract(client, deployment, invoice_text):
    messages = [
        {"role": "system", "content": "Extract the following fields from this invoice: vendor, date, amount, currency. /no-think"},
        {"role": "user",   "content": f"{invoice_text}\n\nReturn valid JSON only."},
    ]
    resp = client.chat.completions.create(
        model=deployment,
        messages=messages,
        temperature=0.0,
        max_tokens=512,
    )
    content = resp.choices[0].message.content
    if "</think>" in content:
        content = content.split("</think>")[-1].strip()
    content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
    return json.loads(content)


def validate(result: dict) -> bool:
    return all(result.get(f) not in (None, "", 0) for f in REQUIRED_FIELDS)


def run_agent(filepath: str, deployment: str):
    load_dotenv()
    client = OpenAI(
        api_key=os.environ["FIREWORKS_API_KEY"],
        base_url="https://api.fireworks.ai/inference/v1",
    )

    print_banner(deployment)
    print(DIVIDER)

    with open(filepath) as f:
        raw_docs = [line.strip() for line in f if line.strip()]

    total  = len(raw_docs)
    passed = 0

    for i, doc in enumerate(raw_docs, 1):
        print(f"\n{GRAY}#{i} of {total}{RESET}")
        print(f"{CYAN}{doc}{RESET}")
        print(DIVIDER_MID)

        t0 = time.time()
        try:
            result  = extract(client, deployment, doc)
            elapsed = round(time.time() - t0, 2)
            valid   = validate(result)
            if valid:
                passed += 1

            for field in REQUIRED_FIELDS:
                val = result.get(field, "—")
                print(f"  {GRAY}{field:<10}{RESET}  {val}")

            print()
            if valid:
                print(f"  {GREEN}✓  Schema valid{RESET}    {GRAY}{elapsed}s{RESET}")
            else:
                print(f"  {RED}✗  Schema mismatch{RESET}  {GRAY}{elapsed}s{RESET}")

        except Exception as e:
            print(f"  {RED}✗  Error: {e}{RESET}")

        print(DIVIDER)

    pct = round(passed / total * 100)
    print(f"\n  {BOLD}Results{RESET}   {GREEN}{passed}/{total} valid{RESET}   Schema match: {GREEN}{pct}%{RESET}\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("invoices",     help="path to invoices.txt")
    ap.add_argument("--deployment", default="accounts/<account-id>/deployments/invoice-extractor-v1",
                                    help="deployed model endpoint")
    args = ap.parse_args()
    run_agent(args.invoices, args.deployment)
