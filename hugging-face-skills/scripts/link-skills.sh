#!/bin/bash
# Bash script to link skills to .claude/skills/
# Run from the project root directory
#
# Claude Code expects: .claude/skills/<skill-name>/SKILL.md
# This script symlinks entire skill directories (not just SKILL.md files)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SKILLS_SOURCE="$PROJECT_ROOT/skills"
CLAUDE_SKILLS="$PROJECT_ROOT/.claude/skills"

# Create .claude/skills directory if it doesn't exist
if [ -e "$CLAUDE_SKILLS" ]; then
    # Remove existing directory/symlink
    rm -rf "$CLAUDE_SKILLS"
fi

mkdir -p "$CLAUDE_SKILLS"

echo -e "\033[36mLinking skills to $CLAUDE_SKILLS\033[0m"

linked=0

# Find all skill directories containing SKILL.md and create symlinks
for skill_dir in "$SKILLS_SOURCE"/*/; do
    skill_name=$(basename "$skill_dir")
    skill_md="$skill_dir/SKILL.md"
    
    if [ -f "$skill_md" ]; then
        link_path="$CLAUDE_SKILLS/$skill_name"
        
        # Create symbolic link to the entire skill directory
        ln -s "$skill_dir" "$link_path"
        
        if [ $? -eq 0 ]; then
            echo -e "  \033[32m[OK]\033[0m $skill_name/"
            ((linked++))
        else
            echo -e "  \033[31m[FAILED]\033[0m $skill_name/"
        fi
    fi
done

echo -e "\n\033[36mLinked $linked skill directories to .claude/skills/\033[0m"
echo -e "\033[33mExpected structure: .claude/skills/<skill-name>/SKILL.md\033[0m"
