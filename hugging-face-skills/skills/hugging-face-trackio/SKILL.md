---
name: hugging-face-trackio
description: Track and visualize ML training experiments with Trackio. Use when logging metrics during training (Python API) or retrieving/analyzing logged metrics (CLI). Supports real-time dashboard visualization, HF Space syncing, and JSON output for automation.
---

# Trackio - Experiment Tracking for ML Training

Trackio is an experiment tracking library for logging and visualizing ML training metrics. It syncs to Hugging Face Spaces for real-time monitoring dashboards.

## Two Interfaces

| Task | Interface | Reference |
|------|-----------|-----------|
| **Logging metrics** during training | Python API | [references/logging_metrics.md](references/logging_metrics.md) |
| **Retrieving metrics** after/during training | CLI | [references/retrieving_metrics.md](references/retrieving_metrics.md) |

## When to Use Each

### Python API → Logging

Use `import trackio` in your training scripts to log metrics:

- Initialize tracking with `trackio.init()`
- Log metrics with `trackio.log()` or use TRL's `report_to="trackio"`
- Finalize with `trackio.finish()`

**Key concept**: For remote/cloud training, pass `space_id` — metrics sync to a Space dashboard so they persist after the instance terminates.

→ See [references/logging_metrics.md](references/logging_metrics.md) for setup, TRL integration, and configuration options.

### CLI → Retrieving

Use the `trackio` command to query logged metrics:

- `trackio list projects/runs/metrics` — discover what's available
- `trackio get project/run/metric` — retrieve summaries and values
- `trackio show` — launch the dashboard
- `trackio sync` — sync to HF Space

**Key concept**: Add `--json` for programmatic output suitable for automation and LLM agents.

→ See [references/retrieving_metrics.md](references/retrieving_metrics.md) for all commands, workflows, and JSON output formats.

## Minimal Logging Setup

```python
import trackio

trackio.init(project="my-project", space_id="username/trackio")
trackio.log({"loss": 0.1, "accuracy": 0.9})
trackio.log({"loss": 0.09, "accuracy": 0.91})
trackio.finish()
```

### Minimal Retrieval

```bash
trackio list projects --json
trackio get metric --project my-project --run my-run --metric loss --json
```
