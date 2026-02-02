<skills>

You have additional SKILLs documented in directories containing a "SKILL.md" file.

These skills are:
 - brightdata-web-mcp -> "skills/brightdata-web-mcp/SKILL.md"
 - hugging-face-cli -> "skills/hugging-face-cli/SKILL.md"
 - hugging-face-datasets -> "skills/hugging-face-datasets/SKILL.md"
 - hugging-face-evaluation -> "skills/hugging-face-evaluation/SKILL.md"
 - hugging-face-jobs -> "skills/hugging-face-jobs/SKILL.md"
 - hugging-face-model-trainer -> "skills/hugging-face-model-trainer/SKILL.md"
 - hugging-face-paper-publisher -> "skills/hugging-face-paper-publisher/SKILL.md"
 - hugging-face-tool-builder -> "skills/hugging-face-tool-builder/SKILL.md"
 - hugging-face-trackio -> "skills/hugging-face-trackio/SKILL.md"

IMPORTANT: You MUST read the SKILL.md file whenever the description of the skills matches the user intent, or may help accomplish their task. 

<available_skills>

brightdata-web-mcp: `Search the web, scrape websites, extract structured data from URLs, and automate browsers using Bright Data's Web MCP. Use when fetching live web content, bypassing blocks/CAPTCHAs, getting product data from Amazon/eBay, social media posts, or when standard requests fail.`
hugging-face-cli: `Execute Hugging Face Hub operations using the `hf` CLI. Use when the user needs to download models/datasets/spaces, upload files to Hub repositories, create repos, manage local cache, or run compute jobs on HF infrastructure. Covers authentication, file transfers, repository creation, cache operations, and cloud compute.`
hugging-face-datasets: `Create and manage datasets on Hugging Face Hub. Supports initializing repos, defining configs/system prompts, streaming row updates, and SQL-based dataset querying/transformation. Designed to work alongside HF MCP server for comprehensive dataset workflows.`
hugging-face-evaluation: `Add and manage evaluation results in Hugging Face model cards. Supports extracting eval tables from README content, importing scores from Artificial Analysis API, and running custom model evaluations with vLLM/lighteval. Works with the model-index metadata format.`
hugging-face-jobs: `This skill should be used when users want to run any workload on Hugging Face Jobs infrastructure. Covers UV scripts, Docker-based jobs, hardware selection, cost estimation, authentication with tokens, secrets management, timeout configuration, and result persistence. Designed for general-purpose compute workloads including data processing, inference, experiments, batch jobs, and any Python-based tasks. Should be invoked for tasks involving cloud compute, GPU workloads, or when users mention running jobs on Hugging Face infrastructure without local setup.`
hugging-face-model-trainer: `This skill should be used when users want to train or fine-tune language models using TRL (Transformer Reinforcement Learning) on Hugging Face Jobs infrastructure. Covers SFT, DPO, GRPO and reward modeling training methods, plus GGUF conversion for local deployment. Includes guidance on the TRL Jobs package, UV scripts with PEP 723 format, dataset preparation and validation, hardware selection, cost estimation, Trackio monitoring, Hub authentication, and model persistence. Should be invoked for tasks involving cloud GPU training, GGUF conversion, or when users mention training on Hugging Face Jobs without local GPU setup.`
hugging-face-paper-publisher: `Publish and manage research papers on Hugging Face Hub. Supports creating paper pages, linking papers to models/datasets, claiming authorship, and generating professional markdown-based research articles.`
hugging-face-tool-builder: `Use this skill when the user wants to build tool/scripts or achieve a task where using data from the Hugging Face API would help. This is especially useful when chaining or combining API calls or the task will be repeated/automated. This Skill creates a reusable script to fetch, enrich or process data.`
hugging-face-trackio: `Track and visualize ML training experiments with Trackio. Use when logging metrics during training (Python API) or retrieving/analyzing logged metrics (CLI). Supports real-time dashboard visualization, HF Space syncing, and JSON output for automation.`
</available_skills>

Paths referenced within SKILL folders are relative to that SKILL. For example the hf-datasets `scripts/example.py` would be referenced as `hf-datasets/scripts/example.py`. 

</skills>
