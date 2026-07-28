---
name: grep-app-cli
description: 'Use when a task needs to find real code patterns in public GitHub repositories via the grep.app MCP CLI — for example, verifying how a library, framework, config file, or language feature is actually used in production. Trigger on requests to search code (not documentation), find concrete usage examples, or inspect repository-scoped implementation patterns.'
license: MIT
compatibility: Requires uv and access to the internet
allowed-tools: Bash(uv run --with fastmcp python ./scripts/grep-app-mcp.py:*) Bash(sh ./scripts/grep-app-mcp.sh:*)
metadata:
  author: knopki <knopki@duck.com>
  version: "1.0.2"
  hermes:
    category: research
    complexity: intermediate
    icon: 🔍
    tags:
      - code-search
      - github
      - mcp
      - grep.app
    requires_toolsets:
      - terminal
---

# grep.app CLI

## Overview

Query `mcp.grep.app` from the terminal to find real code from public
repositories. grep.app indexes over a million public GitHub repos and matches
**literal code** (like `grep`), not keywords or natural-language topics.

This skill wraps the grep.app MCP server with a small CLI so the agent can run
scoped, reproducible code searches and cite concrete examples instead of
guessing at usage.

## When to Use

Trigger this skill when you are about to search for code rather than docs.
Concretely:

- The user asks for "real examples of …", "how do people actually use …", or
  "show me usage of `<token>`".
- You need to verify how a library, framework, config format, or language
  feature is used in production before writing code.
- You need concrete API usage, call signatures, or config fragments that
  official docs do not cover clearly.
- You want repository-scoped examples (a specific org or repo).

Do **not** trigger this skill for:

- Documentation, prose explanations, or conceptual questions — use a docs/web
  search instead.
- Authoritative specs or version guarantees — prefer official docs.

## Workflow

1. Translate the user's need into a literal code pattern that would
  actually appear in source files.
2. Start with the narrowest useful query.
3. Add filters for `--language`, `--repo`, or `--path` before
  broadening the pattern.
4. Use `--use-regexp` only when a literal string is too restrictive.
5. Summarize the returned pattern and why it is relevant instead of
  dumping raw matches.

## Query Design

- Search for code, not topics.
- Prefer tokens such as `useState(`, `getServerSession`, `CORS(`,
  `server.listen(`, `FROM node:`, or `name: ci`.
- Avoid natural-language queries such as `react auth example` or
  `python cors tutorial`.
- Keep the first pass short and exact; broaden only if the result set is
  empty or obviously too narrow.

## Filter Strategy

- Use `--language` when syntax or framework usage is language-specific.
- Use `--repo` when the user asks about a known project, organization, or ecosystem.
- Use `--path` when the pattern is expected in files like
  `package.json`, `Dockerfile`, `.github/workflows/`, or `/route.ts`.
- Combine filters before switching to regex. Narrowing scope is usually
  cheaper than making the pattern more complex.

## Regex Guidance

- Add `--use-regexp` for flexible patterns, optional spacing, or
  multi-line matches.
- Prefix with `(?s)` when the match may span line breaks.
- Escape regex metacharacters when the intent is literal punctuation.
- Prefer targeted regex such as
  `(?s)useEffect\\(\\(\\) => \\{.*removeEventListener` over overly broad
  `.*` searches with no anchors.

## Commands

Resolve paths from the skill directory when invoking the bundled script.

```bash
cd skills/grep-app-cli
sh ./scripts/grep-app-mcp.sh list-tools
```

```bash
cd skills/grep-app-cli
sh ./scripts/grep-app-mcp.sh call-tool searchGitHub \
  --query "useState(" --language TSX --language TypeScript
```

```bash
cd skills/grep-app-cli
sh ./scripts/grep-app-mcp.sh call-tool searchGitHub \
  --query "(?s)try \\{.*await" --use-regexp --language Python
```

## Supported Operations

- `list-tools`
- `list-resources`
- `read-resource <uri>`
- `list-prompts`
- `get-prompt <name> [key=value ...]`
- `call-tool searchGitHub --query <pattern> [filters...]`

## searchGitHub Flags

- `--query`: required literal code pattern or regex.
- `--match-case`: use for case-sensitive identifiers or formats.
- `--match-whole-words`: use when partial identifier matches create noise.
- `--use-regexp`: enable regex interpretation.
- `--repo`: restrict to a repository or org fragment such as `vercel/`.
- `--path`: restrict to a file path or fragment such as `/route.ts`.
- `--language`: repeatable language filter such as
  `--language TypeScript --language TSX`.

## Output Expectations

- Explain what pattern was searched and why.
- Call out any filters that materially shaped the result.
- Distinguish direct matches from your inference about best practice.
- Mention when results are sparse, noisy, or biased toward a specific
  ecosystem.

## Common Pitfalls

- **Searching topics instead of code.** grep.app matches literal source text,
  not keywords. `react auth example` returns noise; `getServerSession(` returns
  real usage.
- **Starting too broad.** A bare `useState(` returns a flood. Add `--language`
  or `--path` filters before widening the pattern.
- **Overusing regex.** Unanchored `.*` matches everything. Prefer a literal
  first; when you must use regex, anchor it or prefix with `(?s)` for multi-line
  intent.
- **Treating popularity as correctness.** A pattern appearing often does not
  make it recommended or idiomatic. Treat results as examples, not authority.
- **Ignoring ecosystem bias.** Results skew toward the most-indexed ecosystems;
  sparse or missing matches do not prove a pattern is unused.
- **Forgetting filters are repeatable.** `--language` can be passed multiple
  times (e.g. `--language TypeScript --language TSX`) to broaden within a
  family.

## Limits

- Treat grep.app as a source of implementation examples, not as
  authoritative documentation.
- Do not claim a pattern is recommended solely because it appears in public repositories.
- Prefer official docs when the task depends on guarantees, specs, or
  version-specific behavior.

## Verification Checklist

Before reporting search results, confirm:

- [ ] Query is literal code (tokens like `useState(`, `FROM node:`,
  `name: ci`), not natural-language keywords.
- [ ] Started narrow; added `--language` / `--repo` / `--path` filters before
  broadening the pattern.
- [ ] `--use-regexp` used only when a literal string was too restrictive; regex
  is anchored or uses `(?s)` for multi-line intent.
- [ ] Results summarized: what pattern was searched, why, and which filters
  shaped the result set.
- [ ] Direct matches distinguished from inference about best practice.
- [ ] No claim that a pattern is "recommended" solely because it appears in
  public repos.
- [ ] Official docs consulted when the task depends on guarantees, specs, or
  version-specific behavior.
