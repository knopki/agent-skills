# Agent Skills Collection

A vendor-neutral collection of reusable **agent skills**.

## Repository layout

This repository uses a single canonical source of truth for skill contents:

```text
skills/<skill-name>/...
```

Agent-specific discovery paths should point at the canonical skill via symlink:

```text
.agents/skills/<skill-name>  -> ../../skills/<skill-name>
.claude/skills/<skill-name>  -> ../../skills/<skill-name>
```

This keeps skills DRY while still supporting different agent discovery conventions.

## Development environment

Use this repository from `devenv`:

```sh
devenv shell
```

The shell provides the expected tooling and checks for working on skills in
this repo, including:

- `treefmt` for repository formatting
- git hooks for baseline validation
- `agentskills`

Typical local workflow:

```sh
devenv shell
treefmt
git status
```

If you add or rename a skill, update the matching symlinks in:

- `.agents/skills/`
- `.claude/skills/`

## Writing skills

This repository follows the Agent Skills ecosystem rather than redefining it locally.

Contributor references:

- Specification: <https://agentskills.io/specification>
- Optimizing skill descriptions: <https://agentskills.io/skill-creation/optimizing-descriptions>
- Best practices for skill creators: <https://agentskills.io/skill-creation/best-practices>

Repository-specific rules live in `AGENTS.md`.

## Repository conventions

- Keep `skills/<name>/SKILL.md` vendor-neutral.
- Use `skills/<name>/agents/` for agent-specific metadata such as `openai.yaml`.
- Treat the `description` field as the primary activation rule for a skill.
- Prefer small, focused skills over large monoliths.
- Add scripts only when determinism or reliability justifies them.
- Keep exported symlinks in `.agents/skills/` and `.claude/skills/` in sync
  with `skills/`.

## Installation

If your environment supports the Agent Skills tooling, install from
the repository URL:

```sh
npx skills add <repo-url>
```

You can also clone the repository and expose the agent-specific skill
directories your tool supports.

## License

MIT
