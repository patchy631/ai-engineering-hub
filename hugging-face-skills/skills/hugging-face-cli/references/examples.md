# HF CLI Common Workflows & Examples

Practical examples for common Hugging Face Hub tasks.

## Table of Contents
- [Browse Hub](#browse-hub)
- [Model Workflows](#model-workflows)
- [Dataset Workflows](#dataset-workflows)
- [Space Workflows](#space-workflows)
- [Inference Endpoints](#inference-endpoints)
- [Cache Management](#cache-management)
- [Automation Patterns](#automation-patterns)

---

## Browse Hub

### Discover Models

```bash
# Find popular text generation models
hf models ls --filter "text-generation" --sort downloads --limit 10

# Search for specific model architecture
hf models ls --search "MiniMax" --author MiniMaxAI

# Find models with expanded info
hf models ls --search "MiniMax" --expand downloads,likes,pipeline_tag

# Get detailed info about a model
hf models info MiniMaxAI/MiniMax-M2.1
hf models info MiniMaxAI/MiniMax-M2.1 --expand downloads,likes,tags,config
```

### Discover Datasets

```bash
# Find popular datasets
hf datasets ls --sort downloads --limit 10

# Search for datasets by topic
hf datasets ls --search "finepdfs" --author HuggingFaceFW

# Get detailed info about a dataset
hf datasets info HuggingFaceFW/finepdfs
hf datasets info HuggingFaceFW/finepdfs --expand downloads,likes,description
```

### Discover Spaces

```bash
# List top trending spaces
hf spaces ls --limit 10

# Filter by 3D modeling spaces
hf spaces ls --filter "3d" --limit 10

# Find spaces by author
hf spaces ls --author enzostvs --limit 20

# Get detailed info about a space
hf spaces info enzostvs/deepsite
hf spaces info enzostvs/deepsite --expand sdk,runtime,likes
```

---

## Model Workflows

### Download a Model for Local Inference

```bash
# Download entire model to cache (recommended)
hf download meta-llama/Llama-3.2-1B-Instruct

# Download specific files only
hf download meta-llama/Llama-3.2-1B-Instruct config.json tokenizer.json

# Download only safetensors (skip pytorch .bin files)
hf download meta-llama/Llama-3.2-1B-Instruct --include "*.safetensors" --exclude "*.bin"

# Download to specific directory for deployment
hf download meta-llama/Llama-3.2-1B-Instruct --local-dir ./models/llama
```

### Publish a Fine-Tuned Model

```bash
# Create repository
hf repo create my-username/my-finetuned-model --private

# Upload model files
hf upload my-username/my-finetuned-model ./output . \
  --commit-message="Initial model upload after SFT training"

# Add version tag
hf repo tag create my-username/my-finetuned-model v1.0

# List tags to verify
hf repo tag list my-username/my-finetuned-model
```

### Download Specific Model Revision

```bash
# Download from a specific branch
hf download stabilityai/stable-diffusion-xl-base-1.0 --revision fp16

# Download from a specific commit
hf download gpt2 --revision 11c5a3d5811f50298f278a704980280950aedb10

# Download from a PR
hf download bigcode/starcoder2 --revision refs/pr/42
```

---

## Dataset Workflows

### Download a Dataset

```bash
# Full dataset to cache
hf download HuggingFaceH4/ultrachat_200k --repo-type dataset

# Specific split/file
hf download HuggingFaceH4/ultrachat_200k data/train.parquet --repo-type dataset

# To local directory for processing
hf download tatsu-lab/alpaca --repo-type dataset --local-dir ./data/alpaca
```

### Upload a Dataset

```bash
# Create dataset repo
hf repo create my-username/my-dataset --repo-type dataset --private

# Upload data folder
hf upload my-username/my-dataset ./data . --repo-type dataset \
  --commit-message="Add training data"

# Upload with structured paths
hf upload my-username/my-dataset ./train_data /train --repo-type dataset
hf upload my-username/my-dataset ./test_data /test --repo-type dataset
```

### Contribute to Existing Dataset

```bash
# Create a PR with new data
hf upload community/shared-dataset ./my_contribution /contributed \
  --repo-type dataset --create-pr \
  --commit-message="Add 1000 new samples for domain X"
```

---

## Space Workflows

### Download Space for Local Development

```bash
hf download HuggingFaceH4/zephyr-chat --repo-type space --local-dir ./my-space
```

### Deploy/Update a Space

```bash
# Create space
hf repo create my-username/my-app --repo-type space --space_sdk gradio

# Upload application files
hf upload my-username/my-app . . --repo-type space \
  --exclude="__pycache__/*" --exclude=".git/*" --exclude="*.pyc"

# Continuous deployment during development (upload every 5 min)
hf upload my-username/my-app . . --repo-type space --every=5
```

### Sync Local Changes

```bash
# Upload changes and delete removed files from remote
hf upload my-username/my-app . . --repo-type space \
  --exclude="/logs/*" --exclude="*.tmp" \
  --delete="*" \
  --commit-message="Sync local with Hub"
```

---

## Inference Endpoints

### List Endpoints

```bash
hf endpoints ls
hf endpoints ls --namespace my-org
```

### Deploy an Endpoint

```bash
hf endpoints deploy my-endpoint \
  --repo openai/gpt-oss-120b \
  --framework vllm \
  --accelerator gpu \
  --instance-size x4 \
  --instance-type nvidia-a10g \
  --region us-east-1 \
  --vendor aws
```

### Operate an Endpoint

```bash
hf endpoints describe my-endpoint
hf endpoints pause my-endpoint
hf endpoints resume my-endpoint
hf endpoints scale-to-zero my-endpoint
```

---

## Cache Management

### Inspect Cache Usage

```bash
# Overview of all cached repos
hf cache ls

# Include revisions
hf cache ls --revisions

# Custom cache location
hf cache ls --cache-dir /path/to/custom/cache
```

### Clean Up Disk Space

```bash
# Remove a specific repo from cache
hf cache rm model/gpt2

# Remove detached revisions
hf cache prune

# Non-interactive mode (for scripts)
hf cache rm model/gpt2 --yes
```

---

## Automation Patterns

### Scripted Authentication

```bash
# Non-interactive login for CI/CD
hf auth login --token $HF_TOKEN --add-to-git-credential

# Verify authentication
hf auth whoami

# List stored tokens
hf auth list
```

### Quiet Mode for Scripting

```bash
# Get just the cache path for further processing
MODEL_PATH=$(hf download gpt2 --quiet)
echo "Model downloaded to: $MODEL_PATH"

# Get just the upload URL
UPLOAD_URL=$(hf upload my-model ./output . --quiet)
echo "Uploaded to: $UPLOAD_URL"
```

### Batch Download Multiple Models

```bash
#!/bin/bash
MODELS=(
  "meta-llama/Llama-3.2-1B-Instruct"
  "microsoft/phi-2"
  "google/gemma-2b"
)

for model in "${MODELS[@]}"; do
  echo "Downloading $model..."
  hf download "$model" --quiet
done
```

### CI/CD Model Publishing

```bash
#!/bin/bash
# Typical CI workflow for model release

# Authenticate
hf auth login --token $HF_TOKEN

# Create repo (if needed - will succeed if exists with same settings)
hf repo create $ORG/$MODEL_NAME --private || true

# Upload model artifacts
hf upload $ORG/$MODEL_NAME ./model_output . \
  --commit-message="Release v${VERSION}" \
  --commit-description="Training metrics: loss=${LOSS}, accuracy=${ACC}"

# Tag the release
hf repo tag create $ORG/$MODEL_NAME "v${VERSION}"
```

### Run GPU Training Job

```bash
# Run training script on A100
hf jobs run --flavor a100-large \
  pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel \
  --secrets HF_TOKEN \
  -e WANDB_API_KEY=$WANDB_KEY \
  python train.py --epochs 10 --batch-size 32

# Monitor job
hf jobs ps
hf jobs logs <job_id>
```

### Scheduled Data Pipeline

```bash
# Run data processing every day at midnight
hf jobs scheduled run "0 0 * * *" python:3.12 \
  --secrets HF_TOKEN \
  python -c "
import huggingface_hub
# Your daily data pipeline code
"

# List scheduled jobs
hf jobs scheduled ps
```

---

## Quick Reference Patterns

| Task | Command |
|------|---------|
| Download model | `hf download <repo_id>` |
| Download to folder | `hf download <repo_id> --local-dir ./path` |
| Upload folder | `hf upload <repo_id> . .` |
| Create model repo | `hf repo create <name>` |
| Create dataset repo | `hf repo create <name> --repo-type dataset` |
| Create private repo | `hf repo create <name> --private` |
| Create space | `hf repo create <name> --repo-type space --space_sdk gradio` |
| Tag a release | `hf repo tag create <repo_id> v1.0` |
| Delete files | `hf repo-files delete <repo_id> <files>` |
| List models | `hf models ls` |
| Get model info | `hf models info <model_id>` |
| List datasets | `hf datasets ls` |
| Get dataset info | `hf datasets info <dataset_id>` |
| List spaces | `hf spaces ls` |
| Get space info | `hf spaces info <space_id>` |
| Check cache | `hf cache ls` |
| Clear cache | `hf cache prune` |
| Run on GPU | `hf jobs run --flavor a10g-small <image> <cmd>` |
| Get environment info | `hf env` |
