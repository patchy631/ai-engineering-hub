---
name: grpo-finetune
description: >
  Fine-tune a model with GRPO on Fireworks-managed GPUs from a plain-English
  task description and a dataset. Use this skill whenever the user wants to
  fine-tune, RL-tune, or GRPO-train a model on their own data — or says things
  like "train a model to extract/classify/score X", "fine-tune on this dataset",
  "set up a GRPO run", or describes a task plus a dataset plus a notion of what
  a good output looks like. Trigger even when the user does not name GRPO or
  Fireworks explicitly.
---

# GRPO Fine-Tune Skill

Keys (`FIREWORKS_API_KEY`, `FIREWORKS_ACCOUNT_ID`, `OPENROUTER_API_KEY`) are
loaded from `.env` in the current directory. No extra setup needed if the
notebook already ran.

## What you do when this skill triggers

### 1. Understand the task
Read the user's description. Sample 3-5 rows from their dataset (`head` the
`.jsonl`) to see the prompt format and whether rows carry a gold answer field.

### 2. Write reward.py

Use this exact reward — schema-only, same as the notebook. Do not add value
matching, ground_truth comparison, or field-level scoring. Do not modify it.

```python
import json
from jsonschema import validate, ValidationError

SCHEMA = {
    "type": "object",
    "required": ["vendor", "date", "amount", "currency"],
    "properties": {
        "vendor":   {"type": "string"},
        "date":     {"type": "string"},
        "amount":   {"type": "number"},
        "currency": {"type": "string"},
    },
    "additionalProperties": False,
}

def score(completion: str, row=None) -> float:
    try:
        parsed = json.loads(completion.strip())
    except (json.JSONDecodeError, ValueError):
        return 0.0
    try:
        validate(instance=parsed, schema=SCHEMA)
        return 1.0
    except ValidationError:
        return 0.5

SELF_TESTS = [
    ('{"vendor": "Acme", "date": "2024-01-15", "amount": 1250.0, "currency": "USD"}', None, 1.0),
    ('{"vendor": "Acme", "date": "2024-01-15"}', None, 0.5),
    ("not json", None, 0.0),
]
```

The score contract is: 1.0 = valid JSON with correct schema, 0.5 = valid JSON
wrong shape, 0.0 = not JSON. This is the only reward logic needed.

### 3. Show it and offer the edit
Show the user `reward.py` and say: this is what training will optimize for —
edit it if your notion of "good" differs. Wait for their go-ahead.

### 4. Validate
```bash
$PYTHON agent-skill/grpo-finetune/generate_reward.py --validate reward.py
```
Must print `PASS` before proceeding.

### 5. Run the pipeline
```bash
$PYTHON agent-skill/grpo-finetune/run_pipeline.py \
    --train <path-to-train.jsonl> \
    --eval  <path-to-eval.jsonl> \
    --task  <short-task-name> \
    --output-id <model-id>
```

Run this in the background immediately. Relay each checkpoint to the user as it
lands — print it directly in your response, do not wait to batch them:

- `>>> Dataset ready  ·  200 prompts`
- `>>> Training started on Fireworks GPUs`
- `>>> Training complete  ·  model deployed to ...`
- `>>> Fine-tuned model  ·  X% accuracy`

The pipeline automatically runs the agent demo on sample invoices at the end.

**Important:** training takes 30-60+ minutes. Use a timeout of at least 7200
seconds. Do not use the default 10 minute timeout.
