# Usage Examples

This document provides practical examples for both methods of adding evaluations to HuggingFace model cards.

## Table of Contents
1. [Setup](#setup)
2. [Method 1: Extract from README](#method-1-extract-from-readme)
3. [Method 2: Import from Artificial Analysis](#method-2-import-from-artificial-analysis)
4. [Standalone vs Integrated](#standalone-vs-integrated)
5. [Common Workflows](#common-workflows)

## Setup

### Initial Configuration

```bash
# Navigate to skill directory
cd hf_evaluation_skill

# Install dependencies
uv add huggingface_hub python-dotenv pyyaml requests

# Configure environment variables
cp examples/.env.example .env
# Edit .env with your tokens
```

Your `.env` file should contain:
```env
HF_TOKEN=hf_your_write_token_here
AA_API_KEY=aa_your_api_key_here  # Optional for AA imports
```

### Verify Installation

```bash
cd scripts
python3 test_extraction.py
```

## Method 1: Extract from README

Extract evaluation tables from your model's existing README.

### Basic Extraction

```bash
# Preview what will be extracted (dry run)
python3 scripts/evaluation_manager.py extract-readme \
  --repo-id "meta-llama/Llama-3.3-70B-Instruct" \
  --dry-run
```

### Apply Extraction to Your Model

```bash
# Extract and update model card directly
python3 scripts/evaluation_manager.py extract-readme \
  --repo-id "your-username/your-model-7b"
```

### Custom Task and Dataset Names

```bash
python3 scripts/evaluation_manager.py extract-readme \
  --repo-id "your-username/your-model-7b" \
  --task-type "text-generation" \
  --dataset-name "Standard Benchmarks" \
  --dataset-type "llm_benchmarks"
```

### Create Pull Request (for models you don't own)

```bash
python3 scripts/evaluation_manager.py extract-readme \
  --repo-id "organization/community-model" \
  --create-pr
```

### Example README Format

Your model README should contain tables like:

```markdown
## Evaluation Results

| Benchmark     | Score |
|---------------|-------|
| MMLU          | 85.2  |
| HumanEval     | 72.5  |
| GSM8K         | 91.3  |
| HellaSwag     | 88.9  |
```

## Method 2: Import from Artificial Analysis

Fetch benchmark scores directly from Artificial Analysis API.

### Integrated Approach (Recommended)

```bash
# Import scores for Claude Sonnet 4.5
python3 scripts/evaluation_manager.py import-aa \
  --creator-slug "anthropic" \
  --model-name "claude-sonnet-4" \
  --repo-id "your-username/claude-mirror"
```

### With Pull Request

```bash
# Create PR instead of direct commit
python3 scripts/evaluation_manager.py import-aa \
  --creator-slug "openai" \
  --model-name "gpt-4" \
  --repo-id "your-username/gpt-4-mirror" \
  --create-pr
```

### Standalone Script

For simple, one-off imports, use the standalone script:

```bash
# Navigate to examples directory
cd examples

# Run standalone script
AA_API_KEY="your-key" HF_TOKEN="your-token" \
python3 artificial_analysis_to_hub.py \
  --creator-slug "anthropic" \
  --model-name "claude-sonnet-4" \
  --repo-id "your-username/your-repo"
```

### Finding Creator Slug and Model Name

1. Visit [Artificial Analysis](https://artificialanalysis.ai/)
2. Navigate to the model you want to import
3. The URL format is: `https://artificialanalysis.ai/models/{creator-slug}/{model-name}`
4. Or check their [API documentation](https://artificialanalysis.ai/api)

Common examples:
- Anthropic: `--creator-slug "anthropic" --model-name "claude-sonnet-4"`
- OpenAI: `--creator-slug "openai" --model-name "gpt-4-turbo"`
- Meta: `--creator-slug "meta" --model-name "llama-3-70b"`

## Standalone vs Integrated

### Standalone Script Features
- ✓ Simple, single-purpose
- ✓ Can run via `uv run` from URL
- ✓ Minimal dependencies
- ✗ No README extraction
- ✗ No validation
- ✗ No dry-run mode

**Use when:** You only need AA imports and want a simple script.

### Integrated Script Features
- ✓ Both README extraction AND AA import
- ✓ Validation and show commands
- ✓ Dry-run preview mode
- ✓ Better error handling
- ✓ Merge with existing evaluations
- ✓ More flexible options

**Use when:** You want full evaluation management capabilities.

## Common Workflows

### Workflow 1: New Model with README Tables

You've just created a model with evaluation tables in the README.

```bash
# Step 1: Preview extraction
python3 scripts/evaluation_manager.py extract-readme \
  --repo-id "your-username/new-model-7b" \
  --dry-run

# Step 2: Apply if it looks good
python3 scripts/evaluation_manager.py extract-readme \
  --repo-id "your-username/new-model-7b"

# Step 3: Validate
python3 scripts/evaluation_manager.py validate \
  --repo-id "your-username/new-model-7b"

# Step 4: View results
python3 scripts/evaluation_manager.py show \
  --repo-id "your-username/new-model-7b"
```

### Workflow 2: Model Benchmarked on AA

Your model appears on Artificial Analysis with fresh benchmarks.

```bash
# Import scores and create PR for review
python3 scripts/evaluation_manager.py import-aa \
  --creator-slug "your-org" \
  --model-name "your-model" \
  --repo-id "your-org/your-model-hf" \
  --create-pr
```

### Workflow 3: Combine Both Methods

You have README tables AND AA scores.

```bash
# Step 1: Extract from README
python3 scripts/evaluation_manager.py extract-readme \
  --repo-id "your-username/hybrid-model"

# Step 2: Import from AA (will merge with existing)
python3 scripts/evaluation_manager.py import-aa \
  --creator-slug "your-org" \
  --model-name "hybrid-model" \
  --repo-id "your-username/hybrid-model"

# Step 3: View combined results
python3 scripts/evaluation_manager.py show \
  --repo-id "your-username/hybrid-model"
```

### Workflow 4: Contributing to Community Models

Help improve community models by adding missing evaluations.

```bash
# Find a model with evaluations in README but no model-index
# Example: community/awesome-7b

# Create PR with extracted evaluations
python3 scripts/evaluation_manager.py extract-readme \
  --repo-id "community/awesome-7b" \
  --create-pr

# GitHub will notify the repository owner
# They can review and merge your PR
```

### Workflow 5: Batch Processing

Update multiple models at once.

```bash
# Create a list of repos
cat > models.txt << EOF
your-org/model-1-7b
your-org/model-2-13b
your-org/model-3-70b
EOF

# Process each
while read repo_id; do
  echo "Processing $repo_id..."
  python3 scripts/evaluation_manager.py extract-readme \
    --repo-id "$repo_id"
done < models.txt
```

### Workflow 6: Automated Updates (CI/CD)

Set up automatic evaluation updates using GitHub Actions.

```yaml
# .github/workflows/update-evals.yml
name: Update Evaluations Weekly
on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday
  workflow_dispatch:  # Manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          pip install huggingface-hub python-dotenv pyyaml requests

      - name: Update from Artificial Analysis
        env:
          AA_API_KEY: ${{ secrets.AA_API_KEY }}
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
        run: |
          python scripts/evaluation_manager.py import-aa \
            --creator-slug "${{ vars.AA_CREATOR_SLUG }}" \
            --model-name "${{ vars.AA_MODEL_NAME }}" \
            --repo-id "${{ github.repository }}" \
            --create-pr
```

## Verification and Validation

### Check Current Evaluations

```bash
python3 scripts/evaluation_manager.py show \
  --repo-id "your-username/your-model"
```

### Validate Format

```bash
python3 scripts/evaluation_manager.py validate \
  --repo-id "your-username/your-model"
```

### View in HuggingFace UI

After updating, visit:
```
https://huggingface.co/your-username/your-model
```

The evaluation widget should display your scores automatically.

## Troubleshooting Examples

### Problem: No tables found

```bash
# Check what tables exist in your README
python3 scripts/evaluation_manager.py extract-readme \
  --repo-id "your-username/your-model" \
  --dry-run

# If no output, ensure your README has markdown tables with numeric scores
```

### Problem: AA model not found

```bash
# Verify the creator and model slugs
# Check the AA website URL or API directly
curl -H "x-api-key: $AA_API_KEY" \
  https://artificialanalysis.ai/api/v2/data/llms/models | jq
```

### Problem: Token permission error

```bash
# Verify your token has write access
# Generate a new token at: https://huggingface.co/settings/tokens
# Ensure "Write" scope is enabled
```

## Tips and Best Practices

1. **Always dry-run first**: Use `--dry-run` to preview changes
2. **Use PRs for others' repos**: Always use `--create-pr` for repositories you don't own
3. **Validate after updates**: Run `validate` to ensure proper formatting
4. **Keep evaluations current**: Set up automated updates for AA scores
5. **Document sources**: The tool automatically adds source attribution
6. **Check the UI**: Always verify the evaluation widget displays correctly

## Getting Help

```bash
# General help
python3 scripts/evaluation_manager.py --help

# Command-specific help
python3 scripts/evaluation_manager.py extract-readme --help
python3 scripts/evaluation_manager.py import-aa --help
```

For issues or questions, consult:
- `../SKILL.md` - Complete documentation
- `../README.md` - Troubleshooting guide
- `../QUICKSTART.md` - Quick start guide
