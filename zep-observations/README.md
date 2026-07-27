# Zep Observations Demo

A deep-dive into how Zep's Observations feature detects behavioral patterns from knowledge graph data.

## What this does

Seeds a Zep knowledge graph with three e-commerce support conversations for a user named Maya, then checks what Observations Zep generates from that data.

The three conversations simulate Maya purchasing ergonomic products over four weeks:

| Conversation | Product | Mentioned |
|---|---|---|
| Conv 1  | Standing desk | Back pain, home office |
| Conv 2  | Ergonomic chair | Back pain, lumbar support, commute |
| Conv 3  | Car seat cushion | Lumbar support, commute |

## Prerequisites

- Python 3.10+
- A Zep API key ([get one here](https://www.getzep.com/))
- **Flex Plus or Enterprise tier** (Observations is not available on lower tiers)

## Setup

```bash
git clone https://github.com/patchy631/ai-engineering-hub.git
cd zep-observations

pip install -r requirements.txt

export ZEP_API_KEY="your-api-key"
```

## Usage

**Step 1: Seed the graph**

```bash
python seed.py
```

This creates a user, three conversation threads, and adds messages to each.

**Step 2: Wait 20-30 minutes**

Zep's observation engine runs as a background process. It checks for new data every 10 minutes and processes graphs that have been idle for at least 30 minutes.

**Step 3: Check the results**

```bash
python check.py
```

This prints any observations, facts, and entities Zep generated from the seeded data.

## How the observation mechanism works

Zep's observation pipeline is a two-stage process:

1. **Deterministic clustering.** Every fact in the graph gets reduced to a signature (entity pair + relationship type). Episodes that share signatures get linked. The connected components of this episode graph become observation candidates. No ML model is involved in this step.

2. **Constrained LLM summarization.** A single LLM call receives the cluster's entities, episodes, and relationship types, and writes a name and summary. The LLM never decides what gets grouped — it only describes what the algorithm already found.

---

## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)
[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
