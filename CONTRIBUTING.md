# Contributing to AI Engineering Hub 🚀

Thank you for your interest in contributing! This repository is a community-driven collection of 93+ hands-on, production-ready AI projects covering LLMs, RAG, agents, fine-tuning, multimodal systems, MCP/ACP protocols, and more. Whether you're fixing a typo, improving documentation, or adding a brand-new project, your contribution is very welcome.

We follow the “fork → branch → pull request” workflow. All contributions must adhere to this guide.

## Code of Conduct
This project adheres to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you agree to uphold this code. Report unacceptable behavior to the maintainers.

## How to Contribute

### 1. Find something to work on
- Check the [Issues tab](https://github.com/patchy631/ai-engineering-hub/issues) for “help wanted” or “good first issue” labels.
- If you have a new project idea, open an issue first to discuss it — this prevents duplicated effort.

### 2. Fork & Clone
```bash
git clone https://github.com/YOUR_USERNAME/ai-engineering-hub.git
cd ai-engineering-hub
```

### 3. Create a descriptive branch
```bash
git checkout -b feature/your-awesome-feature
# or
git checkout -b fix/typo-in-project-42
```

### 4. Make your changes
#### General rules
- Keep projects self-contained (code + README + requirements in its own folder).
- Use Python 3.10+.
- Prefer open/free models & tools (Ollama, Groq, DeepSeek, Llama-3, Qwen, Gemma, etc.) so everyone can run the project without paid API keys.
- Include a clear `README.md` inside the project folder with:
  - Short description & learning goal
  - Installation steps
  - How to run
  - Example output/screenshot (highly encouraged!)
  - Difficulty level tag: `[Beginner]`, `[Intermediate]`, or `[Advanced]`

#### Adding a new project
1. Create a new folder named kebab-case or snake_case (e.g., `multi-modal-rag-with-qwen-vl`).
2. Add your code/notebooks.
3. Add a detailed `README.md` (see existing projects as templates).
4. Update the main repository README:
   - Add your project to the correct difficulty section.
   - Include a short one-line description and the difficulty tag.

#### Code style
- Python → follow PEP 8 (use `ruff` or `black` if you want).
- Notebooks → keep them clean; restart kernel and run all before committing.

### 5. Commit with clear messages
```bash
git commit -m "feat: add real-time voice agent with AssemblyAI and CrewAI [Intermediate]"
```

### 6. Keep your branch up to date
```bash
git remote add upstream https://github.com/patchy631/ai-engineering-hub.git
git fetch upstream
git rebase upstream/main
```

### 7. Push & open a Pull Request
- Push to your fork.
- Open a PR against `main`.
- Use a clear title and description.
- Link related issues (`Closes #123` or `Fixes #45`).
- Tag @patchy631 if you want quick feedback.

## What makes a great contribution?
- Projects that teach a new technique or stack (MCP, ACP, GraphRAG, tool-calling agents, etc.).
- Clear, beginner-friendly explanations.
- Screenshots or short Loom/GIF demos.
- Comparisons (e.g., “Llama-3.2 vs DeepSeek-R1 on reasoning tasks”).
- Performance benchmarks when relevant.

## Questions?
- Open an issue — we’re happy to help!
- Join the community via the [Daily Dose of DS newsletter](https://join.dailydoseofds.com/) for updates and discussions.

Thank you for helping make the AI Engineering Hub better for everyone! ❤️

>The AI Engineering Hub community
