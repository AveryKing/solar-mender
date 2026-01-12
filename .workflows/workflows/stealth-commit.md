---
description: Stage and commit changes in logical chunks with professional, human-sounding messages to mask AI involvement.
---

# Stealth Commit Workflow

Use this workflow when you want to push code to GitHub that looks like it was written by a human engineer, not an AI.

## 1. Analysis
1. Run `git status` to see untracked and modified files.
2. Read `.gitignore` to ensure we are strictly enforcing the "Hide AI" rules (no `.agent/`, `.gemini/`, or internal logs).
3. **Plan the Commits**: detailed mental grouping of files into logical "features" or "chores".
   - *Bad*: `git add . && git commit -m "update"`
   - *Good*: Group `src/types` -> "feat: update type definitions"
   - *Good*: Group `Dockerfile` + `package.json` -> "chore: update build configuration"

## 2. Execution Loop
For each logical group identified in step 1:

1. **Stage**: Run `git add [specific_files]`.
2. **Commit**: Run `git commit -m "[message]"`.
   - **Rules for Human-Like Messages**:
     - Use [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`).
     - Use **Imperative Mood** ("add feature" not "added feature").
     - **Lowercase** subject line.
     - **No period** at the end.
     - **Avoid AI Buzzwords**: Don't say "optimize LLM reasoning", say "refactor decision logic". Don't say "update context window", say "increase buffer size".
     - Keep it under 50-72 characters if possible.

## 3. Cleanup & Push
1. Run `git status` to ensure nothing important was missed.
2. Run `git push origin [branch]` (default to current branch).

## Example Sequence
```bash
# Group 1: Infrastructure
git add Dockerfile package.json
git commit -m "chore: update dependency versions and build target"

# Group 2: Core Logic
git add src/agents/visionary.ts
git commit -m "feat: implement image analysis pipeline"
```
