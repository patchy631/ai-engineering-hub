#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Generate AGENTS.md from AGENTS_TEMPLATE.md and SKILL.md frontmatter.

Also validates that marketplace.json is in sync with discovered skills,
and updates the skills table in README.md.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = ROOT / "scripts" / "AGENTS_TEMPLATE.md"
OUTPUT_PATH = ROOT / "agents" / "AGENTS.md"
MARKETPLACE_PATH = ROOT / ".claude-plugin" / "marketplace.json"
README_PATH = ROOT / "README.md"

# Markers for the auto-generated skills table in README
README_TABLE_START = "<!-- BEGIN_SKILLS_TABLE -->"
README_TABLE_END = "<!-- END_SKILLS_TABLE -->"


def load_template() -> str:
    return TEMPLATE_PATH.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse a minimal YAML-ish frontmatter block without external deps."""
    match = re.search(r"^---\s*\n(.*?)\n---\s*", text, re.DOTALL)
    if not match:
        return {}
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def collect_skills() -> list[dict[str, str]]:
    skills: list[dict[str, str]] = []
    for skill_md in ROOT.glob("skills/*/SKILL.md"):
        meta = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        name = meta.get("name")
        description = meta.get("description")
        if not name or not description:
            continue
        skills.append(
            {
                "name": name,
                "description": description,
                "path": str(skill_md.parent.relative_to(ROOT)),
            }
        )
    # Keep deterministic order for consistent output
    return sorted(skills, key=lambda s: s["name"].lower())


def render(template: str, skills: list[dict[str, str]]) -> str:
    """Very small Mustache-like renderer that only supports a single skills loop."""
    def repl(match: re.Match[str]) -> str:
        block = match.group(1).strip("\n")
        rendered_blocks = []
        for skill in skills:
            rendered = (
                block.replace("{{name}}", skill["name"])
                .replace("{{description}}", skill["description"])
                .replace("{{path}}", skill["path"])
            )
            rendered_blocks.append(rendered)
        return "\n".join(rendered_blocks)

    # Render loop blocks
    content = re.sub(r"{{#skills}}(.*?){{/skills}}", repl, template, flags=re.DOTALL)
    return content


def load_marketplace() -> dict:
    """Load marketplace.json and return parsed structure."""
    if not MARKETPLACE_PATH.exists():
        raise FileNotFoundError(f"marketplace.json not found at {MARKETPLACE_PATH}")
    return json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))


def generate_readme_table(skills: list[dict[str, str]]) -> str:
    """Generate the skills table for README.md using marketplace.json names."""
    marketplace = load_marketplace()
    plugins = {p["source"]: p for p in marketplace.get("plugins", [])}

    lines = [
        "| Name | Description | Documentation |",
        "|------|-------------|---------------|",
    ]

    for skill in skills:
        source = f"./{skill['path']}"
        plugin = plugins.get(source, {})
        name = plugin.get("name", skill["name"])
        description = plugin.get("description", skill["description"])
        doc_link = f"[SKILL.md]({skill['path']}/SKILL.md)"
        lines.append(f"| `{name}` | {description} | {doc_link} |")

    return "\n".join(lines)


def update_readme(skills: list[dict[str, str]]) -> bool:
    """
    Update the README.md skills table between markers.
    Returns True if the file was updated, False if markers not found.
    """
    if not README_PATH.exists():
        print(f"Warning: README.md not found at {README_PATH}", file=sys.stderr)
        return False

    content = README_PATH.read_text(encoding="utf-8")

    start_idx = content.find(README_TABLE_START)
    end_idx = content.find(README_TABLE_END)

    if start_idx == -1 or end_idx == -1:
        print(
            f"Warning: README.md markers not found. Add {README_TABLE_START} and "
            f"{README_TABLE_END} to enable table generation.",
            file=sys.stderr,
        )
        return False

    if end_idx < start_idx:
        print("Warning: README.md markers are in wrong order.", file=sys.stderr)
        return False

    table = generate_readme_table(skills)
    new_content = (
        content[: start_idx + len(README_TABLE_START)]
        + "\n"
        + table
        + "\n"
        + content[end_idx:]
    )

    README_PATH.write_text(new_content, encoding="utf-8")
    return True


def validate_marketplace(skills: list[dict[str, str]]) -> list[str]:
    """
    Validate marketplace.json against discovered skills.
    Returns list of error messages (empty = passed).
    """
    errors: list[str] = []
    marketplace = load_marketplace()
    plugins = marketplace.get("plugins", [])

    # Build lookups (normalize paths: skill uses "skills/x", marketplace uses "./skills/x")
    skill_by_source = {f"./{s['path']}": s for s in skills}
    plugin_by_source = {p["source"]: p for p in plugins}

    # Check: every skill has a marketplace entry with matching name
    for skill in skills:
        expected_source = f"./{skill['path']}"
        if expected_source not in plugin_by_source:
            errors.append(
                f"Skill '{skill['name']}' at '{skill['path']}' is missing from marketplace.json"
            )
        elif plugin_by_source[expected_source]["name"] != skill["name"]:
            errors.append(
                f"Name mismatch at '{expected_source}': "
                f"SKILL.md='{skill['name']}', marketplace.json='{plugin_by_source[expected_source]['name']}'"
            )

    # Check: every marketplace plugin has a corresponding skill
    for plugin in plugins:
        if plugin["source"] not in skill_by_source:
            errors.append(
                f"Marketplace plugin '{plugin['name']}' at '{plugin['source']}' has no SKILL.md"
            )

    return errors


def main() -> None:
    template = load_template()
    skills = collect_skills()
    output = render(template, skills)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(output, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} with {len(skills)} skills.")

    # Validate marketplace.json
    errors = validate_marketplace(skills)
    if errors:
        print("\nMarketplace.json validation errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    print("Marketplace.json validation passed.")

    # Update README.md skills table
    if update_readme(skills):
        print(f"Updated {README_PATH} skills table.")


if __name__ == "__main__":
    main()
