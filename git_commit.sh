#!/bin/bash

# Git commit and push script for paper research
# Usage: ./git_commit.sh YYYY-MM-DD

if [ -z "$1" ]; then
    echo "Error: Date argument required"
    exit 1
fi

DATE=$1
cd "$(dirname "$0")"

# Check if there are any changes (including untracked files)
if ! git diff --quiet || [ -n "$(git status --porcelain)" ]; then
    # Add all changes including untracked files
    git add .
    
    # Commit with date
    git commit -m "Update research papers - $DATE"
    
    # Push changes
    if git push; then
        echo "Git push: 성공"
        exit 0
    else
        echo "Git push: 실패"
        exit 1
    fi
else
    echo "Git push: 변경없음"
    exit 0
fi