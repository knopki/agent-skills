# AGENTS.md

## Purpose

Agent Skills repository in Agent Skills format.

## How to use this repository

- Skills are located at `skills/`
- Agent-visible paths:
  - `.agents/skills/`
  - `.claude/skills/`
- Setup virtual env via `uv`
- Use `agentskills validate` to validate skills
- Use `npx markdownlint-cli2 skills/**/*.md` to validate skill's markdown files
- Use `ruff`, `zuban`, `pytest` to lint/test skill's scripts

- Skills are reusable and independent

When solving tasks:

1. Identify if a relevant skill exists
2. Prefer using a skill over improvising
3. Follow the skill strictly once selected

## Output quality

Always:

- prioritize correctness over verbosity
- surface risks and uncertainties explicitly
- structure outputs (sections, bullet points)
- avoid vague statements

## Safety and scope

- Do not assume access to external systems unless explicitly provided
- Do not fabricate data (PRs, logs, metrics, etc.)
- Clearly state assumptions

## Modification rules

When editing this repository:

- keep skills portable (vendor-neutral)
- do not introduce agent-specific logic into `SKILL.md`
- place agent-specific config under `skills/<name>/agents/`
- keep `.agents/skills/` and `.claude/skills/` symlinks in sync with `skills/`
- prefer repo-provided tooling from the `uv run`

## Adding new skills

When creating a skill:

- ensure `description` is an activation rule
- include:
  - "When to use"
  - "Steps"
  - "Output"
- avoid duplication with existing skills
- consult the Agent Skills references instead of duplicating their guidance here:
  - Specification: <https://agentskills.io/specification>
  - Optimizing descriptions: <https://agentskills.io/skill-creation/optimizing-descriptions>
  - Best practices: <https://agentskills.io/skill-creation/best-practices>
- use repository tooling where applicable:
  - git hooks for baseline checks
  - `agentskills` CLI from the dev environment

---

## Priority order

When multiple sources conflict:

1. Explicit user instructions
2. Selected skill
3. This file (AGENTS.md)
4. General best practices

---

## Notes

- This repository is designed for **cross-agent compatibility**
- Prefer simple, explicit workflows over clever abstractions
- Skills should be understandable without external context
