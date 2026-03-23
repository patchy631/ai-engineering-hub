---
name: pr-summary
description: Generate a well-structured PR description from recent commits and changed files
user-invocable: true
allowed-tools:
  - read_file
  - grep
  - bash
---

# PR Summary Skill

Generate a pull request description by analyzing the recent commits and changed files in the current branch compared to main.

## Instructions

1. Run `git log main..HEAD --oneline` to see the commits on this branch.
2. Run `git diff main --stat` to see which files changed and how much.
3. For key changed files, read them to understand the intent of the changes.
4. Produce a PR description with the following sections:

### Output Format

**Title:** A concise one-line summary of the change.

**Summary:** 2-3 sentences explaining what this PR does and why.

**Changes:**
- List the key changes, grouped logically (not file-by-file).

**Testing:** How the changes were tested or how a reviewer can verify them.

**Notes:** Any caveats, follow-up work, or things the reviewer should pay attention to.
