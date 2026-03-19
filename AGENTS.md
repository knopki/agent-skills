# AGENTS.md

## Purpose

This file defines **repository-level rules and context**
for AI agents (Codex, OpenCode, etc.).

It is NOT a replacement for skills.
It provides global constraints, expectations, and conventions.

---

## How to use this repository

- Skills are located in `skills/`
- Agent-visible paths:
  - `.agents/skills/`
  - `.claude/skills/`
- Enter the repo through `devenv shell` before running formatting, validation,
  or helper commands

- Skills are reusable and independent

When solving tasks:

1. Identify if a relevant skill exists
2. Prefer using a skill over improvising
3. Follow the skill strictly once selected

---

## Skill usage rules

### When to use a skill

Use a skill if:

- the task matches its description
- it provides a structured workflow
- it reduces ambiguity or risk

### When NOT to use a skill

Do NOT use a skill if:

- the task is trivial
- the skill only partially applies and would introduce overhead
- a direct solution is clearer

---

## Execution expectations

When executing a skill:

- follow its steps in order
- do not skip validation steps
- respect its output format
- keep results structured and deterministic

If the skill references additional files:

- load them only when needed
- do not assume hidden context

---

## Output quality

Always:

- prioritize correctness over verbosity
- surface risks and uncertainties explicitly
- structure outputs (sections, bullet points)
- avoid vague statements

---

## Safety and scope

- Do not assume access to external systems unless explicitly provided
- Do not fabricate data (PRs, logs, metrics, etc.)
- Clearly state assumptions

---

## Modification rules

When editing this repository:

- keep skills portable (vendor-neutral)
- do not introduce agent-specific logic into `SKILL.md`
- place agent-specific config under `skills/<name>/agents/`
- keep `.agents/skills/` and `.claude/skills/` symlinks in sync with `skills/`
- prefer repo-provided tooling from the `devenv` shell

---

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
  - `treefmt` for formatting
  - git hooks for baseline checks
  - `agentskills.exec` for the `agentskills` CLI from the dev environment

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
