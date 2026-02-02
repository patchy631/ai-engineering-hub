---
title: README
emoji: 🐠
colorFrom: yellow
colorTo: gray
sdk: static
pinned: false
---

# Humanity's Last Hackathon (of 2025)

<img src="https://github.com/huggingface/skills/raw/main/assets/banner.png" alt="Humanity's Last Hackathon (of 2025)" width="100%">

Welcome to our hackathon!

Whether you’re a tooled up ML engineer, a classicist NLP dev, or an AGI pilled vibe coder, this hackathon is going to be hard work! We’re going to take the latest and greatest coding agents 
and use them to level up open source AI. After all, **why use December to relax and spend time with loved ones, when you can solve AI for all humanity?** Jokes aside, this hackathon is not 
about learning skills from zero or breaking things down in their simplest components. It’s about collaborating, shipping, and making a difference for the open source community.

## What We're Building

Over four weeks, we're using coding agents to level up the open source AI ecosystem:

- **Week 1** — Evaluate models and build a distributed leaderboard
- **Week 2** — Create high-quality datasets for the community  
- **Week 3** — Fine-tune and share models on the Hub
- **Week 4** — Sprint to the finish line together

Every contribution earns XP. Top contributors make the leaderboard. Winners get prizes!

Here's the schedule:

| Date | Event | Link |
|------|-------|------|
| Dec 2 (Mon) | Week 1 Quest Released | [Evaluate a Hub Model](02_evaluate-hub-model.md) |
| Dec 4 (Wed) | Livestream 1 | [Q&A 1](https://youtube.com/live/rworGSh-Rgk?feature=share) |
| Dec 9 (Mon) | Week 2 Quest Released | [Publish a Hub Dataset](03_publish-hub-dataset.md) |
| Dec 11 (Wed) | Livestream 2 | TBA |
| Dec 16 (Mon) | Week 3 Quest Released | [Supervised Fine-Tuning](04_sft-finetune-hub.md) |
| Dec 18 (Wed) | Livestream 3 | TBA |
| Dec 23 (Mon) | Week 4 Community Sprint | TBA |
| Dec 31 (Tue) | Hackathon Ends | TBA

## Getting Started

### 1. Join the Organization

Join [hf-skills](https://huggingface.co/organizations/hf-skills/share/KrqrmBxkETjvevFbfkXeezcyMbgMjjMaOp) on Hugging Face. This is where your contributions will be tracked and updated on the leaderboard.

### 2. Set Up Your Coding Agent

Use whatever coding agent you prefer:

- **Claude Code** — `claude` in your terminal
- **Codex** — `codex` CLI
- **Gemini CLI** — `gemini` in your terminal
- **Cursor / Windsurf** — IDE-based agents
- **Open source** — aider, continue, etc.

The skills in this repo work with any agent that can read markdown instructions and run Python scripts. To install the skills, follow the instructions in the [README](../README.md).

### 3. Get Your HF Token

Most quests require a Hugging Face token with write access:

```bash
# mac/linux
curl -LsSf https://hf.co/cli/install.sh | bash

# windows
powershell -ExecutionPolicy ByPass -c "irm https://hf.co/cli/install.ps1 | iex"

# Login (creates/stores your token)
hf auth login
```

This will set your `HF_TOKEN` environment variable.

### 4. Clone the Skills Repo

```bash
git clone https://github.com/huggingface/skills.git
cd skills
```

Point your coding agent at the relevant configuration. Check the [README](../README.md) for instructions on how to use the skills with your coding agent.

## Your First Quest

**Week 1 is live!** Head to [02_evaluate-hub-model.md](02_evaluate-hub-model.md) to start evaluating models and climb the leaderboard.

<iframe
	src="https://hf-skills-hacker-leaderboard.hf.space"
	frameborder="0"
	width="850"
	height="450"
></iframe>

[Leaderboard](https://hf-skills-hacker-leaderboard.hf.space)

## Earning XP

Each quest has three tiers:

| Tier | What it takes | XP |
|------|---------------|-----|
| 🐢 | Complete the basics | 50-75 XP |
| 🐕 | Go deeper with more features | 100-125 XP |
| 🦁 | Ship something impressive | 200-225 XP |

You can complete multiple tiers, and you can complete the same quest multiple times with different models/datasets/spaces.

## Getting Help

- [Discord](https://discord.com/channels/879548962464493619/1442881667986624554) — Join the Hugging Face Discord for real-time help
- [Livestreams](https://www.youtube.com/@HuggingFace/streams) — Weekly streams with walkthroughs and Q&A
- [Issues](https://github.com/huggingface/skills/issues) — Open an issue in this repo if you're stuck

To join the Hackathon, join the organization on the hub and setup your coding agent. 

Ready? Let's ship some AI. 🚀
