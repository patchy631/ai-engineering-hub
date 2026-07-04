# HF CLI Command Reference

Complete reference for all `hf` CLI commands and options.

## Table of Contents
- [Authentication](#authentication)
- [Download](#download)
- [Upload](#upload)
- [Repository Management](#repository-management)
- [Repository Files](#repository-files)
- [Cache Management](#cache-management)
- [Datasets](#datasets)
- [Models](#models)
- [Spaces](#spaces)
- [Jobs](#jobs)
- [Inference Endpoints](#inference-endpoints)
- [Environment](#environment)

---

## Authentication

### hf auth login
Authenticate with Hugging Face Hub.

```bash
hf auth login                              # Interactive login
hf auth login --token $HF_TOKEN            # Non-interactive with token
hf auth login --token $HF_TOKEN --add-to-git-credential  # Also save as git credential
```

**Options:**
| Option | Description |
|--------|-------------|
| `--token` | Access token to use |
| `--add-to-git-credential` | Save token to git credential helper |

### hf auth whoami
Display current authenticated user and organizations.

```bash
hf auth whoami
# Output: username + orgs list
```

### hf auth list
List all stored access tokens.

```bash
hf auth list
```

### hf auth switch
Switch between stored access tokens.

```bash
hf auth switch                              # Interactive selection
hf auth switch --token-name my-token        # Switch to specific token
hf auth switch --add-to-git-credential      # Also update git credentials
```

### hf auth logout
Remove stored authentication tokens.

```bash
hf auth logout                              # Remove active token
hf auth logout --token-name my-token        # Remove specific token
```

**Note:** If logged in via `HF_TOKEN` environment variable, you must unset it in your shell configuration.

---

## Download

### hf download
Download files from the Hub. Uses cache system by default.

**Syntax:**
```bash
hf download <repo_id> [files...] [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--repo-type` | `model` (default), `dataset`, or `space` |
| `--revision` | Specific commit, branch, or tag |
| `--include` | Glob patterns to include (e.g., `"*.safetensors"`) |
| `--exclude` | Glob patterns to exclude (e.g., `"*.fp16.*"`) |
| `--local-dir` | Download to specific directory instead of cache |
| `--cache-dir` | Custom cache directory |
| `--force-download` | Force re-download even if cached |
| `--max-workers` | Number of concurrent downloads |
| `--token` | Authentication token |
| `--quiet` | Suppress output except final path |

**Examples:**
```bash
# Single file
hf download gpt2 config.json

# Entire repository
hf download HuggingFaceH4/zephyr-7b-beta

# Multiple specific files
hf download gpt2 config.json model.safetensors

# Nested file path
hf download HiDream-ai/HiDream-I1-Full text_encoder/model.safetensors

# Filter with patterns
hf download stabilityai/stable-diffusion-xl-base-1.0 --include "*.safetensors" --exclude "*.fp16.*"

# Dataset
hf download HuggingFaceH4/ultrachat_200k --repo-type dataset

# Space
hf download HuggingFaceH4/zephyr-chat --repo-type space

# Specific revision
hf download bigcode/the-stack --repo-type dataset --revision v1.1

# To local directory
hf download adept/fuyu-8b model-00001-of-00002.safetensors --local-dir fuyu

# Quiet mode (outputs only path)
hf download gpt2 --quiet
```

**Timeout:** Set `HF_HUB_DOWNLOAD_TIMEOUT` environment variable (default: 10 seconds).

---

## Upload

### hf upload
Upload files or folders to the Hub.

**Syntax:**
```bash
hf upload <repo_id> [local_path] [path_in_repo] [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--repo-type` | `model` (default), `dataset`, or `space` |
| `--revision` | Target branch/ref |
| `--include` | Glob patterns to include |
| `--exclude` | Glob patterns to exclude |
| `--delete` | Patterns of remote files to delete |
| `--commit-message` | Custom commit message |
| `--commit-description` | Extended commit description |
| `--create-pr` | Create a pull request |
| `--every` | Upload at regular intervals (minutes) |
| `--token` | Authentication token |
| `--quiet` | Suppress output except final URL |

**Examples:**
```bash
# Upload current directory to repo root
hf upload my-cool-model . .

# Upload specific folder
hf upload my-cool-model ./models .

# Upload to specific path in repo
hf upload my-cool-model ./path/to/curated/data /data/train

# Upload single file
hf upload Wauplin/my-cool-model ./models/model.safetensors

# Upload to subdirectory
hf upload Wauplin/my-cool-model ./models/model.safetensors /vae/model.safetensors

# Upload to organization
hf upload MyCoolOrganization/my-cool-model . .

# Upload dataset
hf upload Wauplin/my-cool-dataset ./data /train --repo-type=dataset

# Create PR instead of direct push
hf upload bigcode/the-stack . . --repo-type dataset --create-pr

# Sync with delete (remove remote files not in local)
hf upload Wauplin/space-example --repo-type=space --exclude="/logs/*" --delete="*"

# Upload with custom commit message
hf upload Wauplin/my-cool-model ./models . --commit-message="Epoch 34/50" --commit-description="Val accuracy: 68%"

# Continuous upload every 10 minutes
hf upload training-model logs/ --every=10
```

### hf upload-large-folder
Optimized upload for very large folders with many files. Uses multi-threading and handles interruptions gracefully.

```bash
hf upload-large-folder <repo_id> <local_folder> [path_in_repo] [options]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--repo-type` | `model`, `dataset`, or `space` |
| `--revision` | Target branch |
| `--private` | Create as private repo if doesn't exist |
| `--include` / `--exclude` | Filter patterns |
| `--num-workers` | Number of upload threads |
| `--token` | Authentication token |

---

## Repository Management

### hf repo create
Create a new repository.

```bash
hf repo create my-cool-model                                    # Public model
hf repo create my-cool-dataset --repo-type dataset --private    # Private dataset
hf repo create my-gradio-space --repo-type space --space_sdk gradio  # Gradio space
```

**Options:**
| Option | Description |
|--------|-------------|
| `--repo-type` | `model`, `dataset`, or `space` |
| `--private` | Create as private repository |
| `--space_sdk` | For spaces: `gradio`, `streamlit`, `docker`, `static` |
| `--exist-ok` | Do not error if repo already exists |
| `--resource-group-id` | Enterprise resource group (org-only) |
| `--token` | Authentication token |

**Note:** Use `--space_sdk` (with underscore), not `--space-sdk`.

### hf repo delete
Delete a repository.

```bash
hf repo delete my-username/my-model
hf repo delete my-username/my-dataset --repo-type dataset
```

**Options:**
| Option | Description |
|--------|-------------|
| `--repo-type` | `model`, `dataset`, or `space` |
| `--missing-ok` | Do not error if repo does not exist |
| `--token` | Authentication token |

### hf repo move
Move a repository between namespaces.

```bash
hf repo move old-namespace/my-model new-namespace/my-model
```

**Options:**
| Option | Description |
|--------|-------------|
| `--repo-type` | `model`, `dataset`, or `space` |
| `--token` | Authentication token |

### hf repo settings
Update repository settings.

```bash
hf repo settings my-username/my-model --private true
hf repo settings my-username/my-model --gated auto
```

**Options:**
| Option | Description |
|--------|-------------|
| `--gated` | `auto`, `manual`, or `false` |
| `--private` | Set repo privacy |
| `--repo-type` | `model`, `dataset`, or `space` |
| `--token` | Authentication token |

### hf repo list
List repositories and print results as JSON.

```bash
hf repo list --repo-type model --limit 5
hf repo list --repo-type dataset --search "text" --sort downloads
hf repo list --repo-type space --author my-org --limit 20
```

**Options:**
| Option | Description |
|--------|-------------|
| `--repo-type` | `model`, `dataset`, or `space` |
| `--limit` | Maximum number of results (default: 10) |
| `--filter` | Filter by tag (repeatable) |
| `--search` | Search by name |
| `--author` | Filter by author or org |
| `--sort` | `created_at`, `downloads`, `last_modified`, `likes`, `trending_score` |
| `--token` | Authentication token |

**Note:** `--sort downloads` is not valid for spaces.

### hf repo branch
Manage repository branches.

#### Create a branch
```bash
hf repo branch create <repo_id> <branch> [options]
```

```bash
hf repo branch create Wauplin/my-cool-model release-v1
hf repo branch create Wauplin/my-cool-model release-v1 --revision refs/pr/12
```

#### Delete a branch
```bash
hf repo branch delete <repo_id> <branch> [options]
```

```bash
hf repo branch delete Wauplin/my-cool-model release-v1
```

**Options:**
| Option | Description |
|--------|-------------|
| `--repo-type` | `model`, `dataset`, or `space` |
| `--revision` | Base revision (create only) |
| `--exist-ok` | Do not error if branch already exists (create only) |
| `--token` | Authentication token |

### hf repo tag
Manage repository tags.

#### Create a tag
```bash
hf repo tag create <repo_id> <tag> [options]
```

```bash
hf repo tag create Wauplin/my-cool-model v1.0                  # Tag main branch
hf repo tag create Wauplin/my-cool-model v1.0 --revision refs/pr/104  # Tag specific revision
hf repo tag create bigcode/the-stack v1.0 --repo-type dataset  # Tag dataset
hf repo tag create Wauplin/my-cool-model v1.0 -m "Release v1.0"
```

#### List tags
```bash
hf repo tag list <repo_id> [options]
```

```bash
hf repo tag list Wauplin/my-cool-model
hf repo tag list Wauplin/gradio-space-ci --repo-type space
```

#### Delete a tag
```bash
hf repo tag delete <repo_id> <tag> [options]
```

```bash
hf repo tag delete Wauplin/my-cool-model v1.0
hf repo tag delete Wauplin/my-cool-model v1.0 -y  # Skip confirmation
```

**Common options for all tag commands:**
| Option | Description |
|--------|-------------|
| `--repo-type` | `model`, `dataset`, or `space` |
| `--message` | Tag description (create only) |
| `--token` | Authentication token |
| `-y` | Skip confirmation (for delete) |

---

## Repository Files

### hf repo-files delete
Delete files from a repository.

```bash
hf repo-files delete <repo_id> <path_in_repo>... [options]
```

**Examples:**
```bash
# Delete folder
hf repo-files delete Wauplin/my-cool-model folder/

# Delete multiple files
hf repo-files delete Wauplin/my-cool-model file.txt folder/pytorch_model.bin

# Use Unix-style wildcards
hf repo-files delete Wauplin/my-cool-model "*.txt" "folder/*.bin"

# With explicit token
hf repo-files delete Wauplin/my-cool-model file.txt --token=hf_****

# Dataset
hf repo-files delete Wauplin/my-dataset data/old.parquet --repo-type dataset
```

**Options:**
| Option | Description |
|--------|-------------|
| `--repo-type` | `model`, `dataset`, or `space` |
| `--revision` | Branch to delete from |
| `--commit-message` | Custom commit message |
| `--commit-description` | Extended commit description |
| `--create-pr` | Create a PR instead of direct delete |
| `--token` | Authentication token |

---

## Cache Management

### hf cache ls
List cached repositories or revisions.

```bash
hf cache ls                                 # List cached repos
hf cache ls --revisions                     # Include revisions
hf cache ls --filter "size>1GB" --limit 20  # Filter and limit
hf cache ls --format json                   # JSON output
```

**Options:**
| Option | Description |
|--------|-------------|
| `--cache-dir` | Cache directory to scan |
| `--revisions` | Include revisions instead of aggregated repos |
| `--filter` | Filter expressions (repeatable) |
| `--format` | `table`, `json`, or `csv` |
| `--quiet` | Print only IDs (repo IDs or revision hashes) |
| `--sort` | `accessed`, `modified`, `name`, or `size` (with `:asc`/`:desc`) |
| `--limit` | Limit the number of results |

### hf cache rm
Remove cached repositories or revisions.

```bash
hf cache rm model/gpt2           # Remove repo from cache
hf cache rm <revision_hash>      # Remove a revision by hash
hf cache rm model/gpt2 --dry-run # Preview deletions
hf cache rm model/gpt2 --yes     # Skip confirmation
```

**Options:**
| Option | Description |
|--------|-------------|
| `--cache-dir` | Cache directory to scan |
| `-y, --yes` | Skip confirmation |
| `--dry-run` | Preview deletions without removing files |

### hf cache prune
Remove detached (unreferenced) revisions from the cache.

```bash
hf cache prune                   # Prune detached revisions
hf cache prune --dry-run         # Preview deletions
hf cache prune --yes             # Skip confirmation
```

**Options:**
| Option | Description |
|--------|-------------|
| `--cache-dir` | Cache directory to scan |
| `-y, --yes` | Skip confirmation |
| `--dry-run` | Preview deletions without removing files |

### hf cache verify
Verify checksums for a repo revision from cache or a local directory.

```bash
hf cache verify gpt2
hf cache verify gpt2 --revision refs/pr/1
hf cache verify karpathy/fineweb-edu-100b-shuffle --repo-type dataset
hf cache verify deepseek-ai/DeepSeek-OCR --local-dir /path/to/repo
```

**Options:**
| Option | Description |
|--------|-------------|
| `--repo-type` | `model`, `dataset`, or `space` |
| `--revision` | Revision to verify |
| `--cache-dir` | Cache directory to use |
| `--local-dir` | Verify files from a local directory |
| `--fail-on-missing-files` | Error if remote files are missing locally |
| `--fail-on-extra-files` | Error if local files are absent remotely |
| `--token` | Authentication token |

**Note:** Use either `--cache-dir` or `--local-dir`, not both.

---

## Datasets

Interact with datasets on the Hub.

### hf datasets ls
List datasets on the Hub.

```bash
hf datasets ls                                      # List top trending datasets
hf datasets ls --limit 20                           # List more results
hf datasets ls --search "finepdfs"                  # Search by name
hf datasets ls --author HuggingFaceFW               # Filter by author/org
hf datasets ls --filter "task_categories:text-generation"  # Filter by tags
hf datasets ls --sort downloads                     # Sort by downloads
hf datasets ls --expand downloads,likes,tags        # Include extra fields
```

**Options:**
| Option | Description |
|--------|-------------|
| `--search` | Search query |
| `--author` | Filter by author or organization |
| `--filter` | Filter by tags (can be used multiple times) |
| `--sort` | `created_at`, `downloads`, `last_modified`, `likes`, `trending_score` |
| `--limit` | Number of results (default: 10) |
| `--expand` | Comma-separated properties to include |
| `--token` | Authentication token |

**Expandable properties:** `author`, `cardData`, `citation`, `createdAt`, `description`, `disabled`, `downloads`, `downloadsAllTime`, `gated`, `lastModified`, `likes`, `paperswithcode_id`, `private`, `resourceGroup`, `sha`, `siblings`, `tags`, `trendingScore`, `usedStorage`

### hf datasets info
Get info about a specific dataset on the Hub.

```bash
hf datasets info HuggingFaceFW/finepdfs
hf datasets info HuggingFaceFW/finepdfs --revision main
hf datasets info HuggingFaceFW/finepdfs --expand downloads,likes,tags
```

**Options:**
| Option | Description |
|--------|-------------|
| `--revision` | Branch, tag, or commit hash |
| `--expand` | Comma-separated properties to include |
| `--token` | Authentication token |

---

## Models

Interact with models on the Hub.

### hf models ls
List models on the Hub.

```bash
hf models ls                                        # List top trending models
hf models ls --limit 20                             # List more results
hf models ls --search "MiniMax"                     # Search by name
hf models ls --author MiniMaxAI                     # Filter by author/org
hf models ls --filter "text-generation"             # Filter by tags
hf models ls --sort downloads                       # Sort by downloads
hf models ls --expand downloads,likes,tags          # Include extra fields
```

**Options:**
| Option | Description |
|--------|-------------|
| `--search` | Search query |
| `--author` | Filter by author or organization |
| `--filter` | Filter by tags (can be used multiple times) |
| `--sort` | `created_at`, `downloads`, `last_modified`, `likes`, `trending_score` |
| `--limit` | Number of results (default: 10) |
| `--expand` | Comma-separated properties to include |
| `--token` | Authentication token |

**Expandable properties:** `author`, `baseModels`, `cardData`, `childrenModelCount`, `config`, `createdAt`, `disabled`, `downloads`, `downloadsAllTime`, `gated`, `gguf`, `inference`, `inferenceProviderMapping`, `lastModified`, `library_name`, `likes`, `mask_token`, `model-index`, `pipeline_tag`, `private`, `resourceGroup`, `safetensors`, `sha`, `siblings`, `spaces`, `tags`, `transformersInfo`, `trendingScore`, `usedStorage`, `widgetData`

### hf models info
Get info about a specific model on the Hub.

```bash
hf models info MiniMaxAI/MiniMax-M2.1
hf models info MiniMaxAI/MiniMax-M2.1 --revision main
hf models info MiniMaxAI/MiniMax-M2.1 --expand downloads,likes,tags,pipeline_tag
```

**Options:**
| Option | Description |
|--------|-------------|
| `--revision` | Branch, tag, or commit hash |
| `--expand` | Comma-separated properties to include |
| `--token` | Authentication token |

---

## Spaces

Interact with spaces on the Hub.

### hf spaces ls
List spaces on the Hub.

```bash
hf spaces ls                                        # List top trending spaces
hf spaces ls --limit 20                             # List more results
hf spaces ls --search "TRELLIS.2"                    # Search by name
hf spaces ls --author microsoft                      # Filter by author/org
hf spaces ls --filter "3d"                          # Filter by 3D modeling spaces
hf spaces ls --sort likes                           # Sort by likes
hf spaces ls --expand likes,tags,sdk                # Include extra fields
```

**Options:**
| Option | Description |
|--------|-------------|
| `--search` | Search query |
| `--author` | Filter by author or organization |
| `--filter` | Filter by tags (can be used multiple times) |
| `--sort` | `created_at`, `last_modified`, `likes`, `trending_score` |
| `--limit` | Number of results (default: 10) |
| `--expand` | Comma-separated properties to include |
| `--token` | Authentication token |

**Note:** `--sort downloads` is not valid for spaces.

**Expandable properties:** `author`, `cardData`, `createdAt`, `datasets`, `disabled`, `lastModified`, `likes`, `models`, `private`, `resourceGroup`, `runtime`, `sdk`, `sha`, `siblings`, `subdomain`, `tags`, `trendingScore`, `usedStorage`

### hf spaces info
Get info about a specific space on the Hub.

```bash
hf spaces info enzostvs/deepsite
hf spaces info enzostvs/deepsite --revision main
hf spaces info enzostvs/deepsite --expand likes,tags,sdk,runtime
```

**Options:**
| Option | Description |
|--------|-------------|
| `--revision` | Branch, tag, or commit hash |
| `--expand` | Comma-separated properties to include |
| `--token` | Authentication token |

---

## Jobs

Run compute jobs on Hugging Face infrastructure.

### hf jobs run
Execute a job.

```bash
hf jobs run <image> <command> [options]
```

**Examples:**
```bash
# Basic Python execution
hf jobs run python:3.12 python -c 'print("Hello from the cloud!")'

# With GPU
hf jobs run --flavor a10g-small pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel \
  python -c "import torch; print(torch.cuda.get_device_name())"

# In organization namespace
hf jobs run --namespace my-org-name python:3.12 python -c "print('Running in org')"

# From HF Space
hf jobs run hf.co/spaces/lhoestq/duckdb duckdb -c "select 'hello world'"

# With environment variables
hf jobs run -e FOO=foo -e BAR=bar python:3.12 python -c "import os; print(os.environ['FOO'])"

# With env file
hf jobs run --env-file .env python:3.12 python script.py

# With secrets (encrypted)
hf jobs run -s MY_SECRET=psswrd python:3.12 python -c "import os; print(os.environ['MY_SECRET'])"

# Pass HF_TOKEN implicitly
hf jobs run --secrets HF_TOKEN python:3.12 python -c "print('authenticated')"

# Detached mode (returns job ID immediately)
hf jobs run --detach python:3.12 python -c "print('background job')"
```

**Options:**
| Option | Description |
|--------|-------------|
| `--flavor` | Hardware configuration (see below) |
| `--namespace` | Organization namespace |
| `-e` | Environment variable (KEY=value) |
| `--env-file` | Load env vars from file |
| `-s, --secrets` | Secret (encrypted, KEY=value or KEY to read from env) |
| `--secrets-file` | Load secrets from file |
| `--detach` | Run in background, print job ID |
| `--timeout` | Job timeout in seconds |

**Available Flavors:**
| Category | Flavors |
|----------|---------|
| CPU | `cpu-basic`, `cpu-upgrade`, `cpu-xl` |
| T4 GPU | `t4-small`, `t4-medium` |
| L4 GPU | `l4x1`, `l4x4` |
| L40S GPU | `l40sx1`, `l40sx4`, `l40sx8` |
| A10G GPU | `a10g-small`, `a10g-large`, `a10g-largex2`, `a10g-largex4` |
| A100 GPU | `a100-large` |
| H100 GPU | `h100`, `h100x8` |

### hf jobs uv run
Run UV scripts (Python with inline dependencies).

```bash
hf jobs uv run <script.py> [options]
hf jobs uv run <url> [options]
hf jobs uv run --with <package> python -c "<code>"
```

**Examples:**
```bash
hf jobs uv run my_script.py                        # Run script
hf jobs uv run my_script.py --repo my-uv-scripts   # With persistent repo
hf jobs uv run ml_training.py --flavor a10g-small  # With GPU
hf jobs uv run --with transformers --with torch train.py  # Add dependencies
hf jobs uv run https://huggingface.co/datasets/user/scripts/resolve/main/example.py
```

### Job Management
```bash
hf jobs ps                    # List running jobs
hf jobs inspect <job_id>      # Check job status and details
hf jobs logs <job_id>         # View job logs
hf jobs cancel <job_id>       # Cancel a running job
```

### Scheduled Jobs
Schedule jobs to run on a recurring basis.

```bash
# Schedule syntax: @hourly, @daily, @weekly, @monthly, or CRON expression
hf jobs scheduled run @hourly python:3.12 python -c 'print("Every hour")'
hf jobs scheduled run "*/5 * * * *" python:3.12 python -c 'print("Every 5 min")'
hf jobs scheduled run @daily --flavor a10g-small <image> <cmd>
```

**Manage scheduled jobs:**
```bash
hf jobs scheduled ps              # List scheduled jobs
hf jobs scheduled inspect <id>    # View schedule details
hf jobs scheduled suspend <id>    # Pause a schedule
hf jobs scheduled resume <id>     # Resume a paused schedule
hf jobs scheduled delete <id>     # Delete a schedule
```

**Scheduled UV scripts:**
```bash
hf jobs scheduled uv run @hourly my_script.py
```

---

## Inference Endpoints

Manage Hugging Face Inference Endpoints.

### hf endpoints ls
List endpoints in a namespace.

```bash
hf endpoints ls
hf endpoints ls --namespace my-org
```

**Options:**
| Option | Description |
|--------|-------------|
| `--namespace` | Namespace to list (defaults to current user) |
| `--token` | Authentication token |

### hf endpoints deploy
Deploy an endpoint from a Hub model.

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

**Options:**
| Option | Description |
|--------|-------------|
| `--repo` | Model repo to deploy |
| `--framework` | Serving framework (e.g., `vllm`) |
| `--accelerator` | Accelerator type (e.g., `cpu`, `gpu`) |
| `--instance-size` | Instance size (e.g., `x4`) |
| `--instance-type` | Instance type (e.g., `intel-icl`) |
| `--region` | Cloud region |
| `--vendor` | Cloud vendor (e.g., `aws`) |
| `--namespace` | Namespace for the endpoint |
| `--task` | Task (e.g., `text-generation`) |
| `--min-replica` | Minimum replicas |
| `--max-replica` | Maximum replicas |
| `--scale-to-zero-timeout` | Minutes before scaling to zero |
| `--scaling-metric` | Scaling metric |
| `--scaling-threshold` | Scaling threshold |
| `--token` | Authentication token |

### hf endpoints catalog ls
List catalog models.

```bash
hf endpoints catalog ls
```

### hf endpoints catalog deploy
Deploy an endpoint from the catalog.

```bash
hf endpoints catalog deploy --repo openai/gpt-oss-120b --name my-endpoint
```

**Options:**
| Option | Description |
|--------|-------------|
| `--repo` | Catalog model repo |
| `--name` | Endpoint name (optional) |
| `--namespace` | Namespace for the endpoint |
| `--token` | Authentication token |

### hf endpoints describe
Get endpoint details.

```bash
hf endpoints describe my-endpoint
```

**Options:**
| Option | Description |
|--------|-------------|
| `--namespace` | Endpoint namespace |
| `--token` | Authentication token |

### hf endpoints update
Update endpoint settings.

```bash
hf endpoints update my-endpoint --min-replica 1 --max-replica 2
hf endpoints update my-endpoint --repo openai/gpt-oss-120b --revision refs/pr/12
```

**Options:**
| Option | Description |
|--------|-------------|
| `--repo` | Model repo |
| `--revision` | Model revision |
| `--framework` | Serving framework |
| `--accelerator` | Accelerator type |
| `--instance-size` | Instance size |
| `--instance-type` | Instance type |
| `--task` | Task |
| `--min-replica` | Minimum replicas |
| `--max-replica` | Maximum replicas |
| `--scale-to-zero-timeout` | Minutes before scaling to zero |
| `--scaling-metric` | Scaling metric |
| `--scaling-threshold` | Scaling threshold |
| `--namespace` | Endpoint namespace |
| `--token` | Authentication token |

### hf endpoints delete
Delete an endpoint permanently.

```bash
hf endpoints delete my-endpoint --yes
```

**Options:**
| Option | Description |
|--------|-------------|
| `--yes` | Skip confirmation prompt |
| `--namespace` | Endpoint namespace |
| `--token` | Authentication token |

### hf endpoints pause
Pause an endpoint.

```bash
hf endpoints pause my-endpoint
```

### hf endpoints resume
Resume an endpoint.

```bash
hf endpoints resume my-endpoint
hf endpoints resume my-endpoint --fail-if-already-running
```

### hf endpoints scale-to-zero
Scale an endpoint to zero.

```bash
hf endpoints scale-to-zero my-endpoint
```

---

## Environment

### hf env
Print environment information (useful for bug reports).

```bash
hf env
```

**Output includes:**
- huggingface_hub version
- Platform and Python version
- Token status
- Cache paths
- Relevant environment variables

### hf version
Print CLI version.

```bash
hf version
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HF_TOKEN` | Authentication token | - |
| `HF_HUB_CACHE` | Cache directory | `~/.cache/huggingface/hub` |
| `HF_HUB_DOWNLOAD_TIMEOUT` | Download timeout (seconds) | 10 |
| `HF_HUB_OFFLINE` | Offline mode | False |
| `HF_HUB_DISABLE_PROGRESS_BARS` | Disable progress bars | False |

---

## Global Options

All commands support:
- `--help` - Show command help and options
- `--token` - Override authentication token
- `--repo-type` - Specify repository type (`model`, `dataset`, `space`)
