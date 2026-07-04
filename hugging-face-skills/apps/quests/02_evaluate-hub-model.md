# Week 1: Evaluate a Hub Model

📣 TASK: Add evaluation results to model cards across the Hub. Together, we're building a distributed leaderboard of open source model performance.

>[!NOTE]
> Bonus XP for contributing to the leaderboard application. Open a PR [on the hub](https://huggingface.co/spaces/hf-skills/distributed-leaderboard/discussions) or [on GitHub](https://github.com/huggingface/skills/blob/main/apps/evals-leaderboard/app.py) to get your (bonus) XP.

## Why This Matters

Model cards without evaluation data are hard to compare. By adding structured eval results to metadata, we make models easier to compare and review. Your contributions power leaderboards and help the community find the best models for their needs. Also, by doing this in a distributed way, we can share our evaluation results with the community.

## Goals

- Add eval scores to the 100 trending models on the Hub
- Include AIME 2025, BigBenchHard, LiveCodeBench, MMLU, ARC on trending models.
- It is ok to include a subset of the benchmarks available for the model.
- Build a leaderboard application that shows the evaluation results for the trending models.

## XP Tiers

Taking part is simple. We need to get model authors to show evaluation results in their model cards. This is a clean up job!

| Tier            | XP    | Description                                                   | What Counts                                  |
|-----------------|-------|---------------------------------------------------------------|-----------------------------------------------|
| 🐢 Contributor  | 1 XP  | Extract evaluation results from one benchmark and update its model card. | Any PR on the repo with evaluation data.      |
| 🐕 Evaluator    | 5 XP  | Import scores from third-party benchmarks like Artificial Analysis. | Undefined benchmark scores and merged PRs.    |
| 🦁 Advanced     | 20 XP| Run your own evaluation with inspect-ai and publish results.   | Original eval run and merged PR.              |
| 🐉 Bonus        | 20 XP| Contribute to the leaderboard application.                      | Any Merged PR on the hub or GitHub.                  |
| 🤢 Slop         | -20 XP  | Opening none useful PRs.                  | Duplicate PRs, Incorrect Eval Scores, Incorrect Benchmark Scores          |

> [!WARNING]
> This hackathon is about advancing the state of open source AI. We want useful PRs that help everyone out, not just metrics. 

## The Skill

Use `hf-evaluation/` for this quest. Key capabilities:

- Extract evaluation tables from existing README content posted by model authors.
- Import benchmark scores from [Artificial Analysis](https://artificial.com/).
- Run your own evals with [inspect-ai](https://github.com/UKGovernmentBEIS/inspect_ai) on [HF Jobs](https://huggingface.co/docs/huggingface_hub/en/guides/jobs).
- Update model-index metadata in the model card.

>[!NOTE]
> Take a look at the [SKILL.md](https://github.com/huggingface/skills/blob/main/hf-evaluation/SKILL.md) for more details.

### Extract Evaluation Tables from README

1. Pick a Hub model without evaluation data from *trending models* on the hub
2. Use the skill to extract or add a benchmark score
3. Create a PR (or push directly if you own the model)

The agent will use this script to extract evaluation tables from the model's README.

```bash
python hf-evaluation/scripts/evaluation_manager.py extract-readme \
  --repo-id "model-author/model-name" --dry-run
```

### Import Scores from Artificial Analysis

1. Find a model with benchmark data on external sites
2. Use `import-aa` to fetch scores from Artificial Analysis API
3. Create a PR with properly attributed evaluation data

The agent will use this script to fetch scores from Artificial Analysis API and add them to the model card.

```bash
python hf-evaluation/scripts/evaluation_manager.py import-aa \
  --creator-slug "anthropic" --model-name "claude-sonnet-4" \
  --repo-id "target/model" --create-pr
```

### Run your own evaluation with inspect-ai and publish results.

1. Choose an eval task (MMLU, GSM8K, HumanEval, etc.)
2. Run the evaluation on HF Jobs infrastructure
3. Update the model card with your results and methodology

The agent will use this script to run the evaluation on HF Jobs infrastructure and update the model card with the results.

```bash
HF_TOKEN=$HF_TOKEN hf jobs uv run hf-evaluation/scripts/inspect_eval_uv.py \
  --flavor a10g-small --secret HF_TOKEN=$HF_TOKEN \
  -- --model "meta-llama/Llama-2-7b-hf" --task "mmlu"
```

## Tips

- Always use `--dry-run` first to preview changes before pushing
- Check for transposed tables where models are rows and benchmarks are columns
- Be careful with PRs for models you don't own — most maintainers appreciate eval contributions but be respectful.
- Manually validate the extracted scores and close PRs if needed.

## Resources

- [SKILL.md](../../skills/hugging-face-evaluation/SKILL.md) — Full skill documentation
- [Example Usage](../../skills/hugging-face-evaluation/examples/USAGE_EXAMPLES.md) — Worked examples
- [Metric Mapping](../../skills/hugging-face-evaluation/examples/metric_mapping.json) — Standard metric types

