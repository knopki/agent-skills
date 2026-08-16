---
name: donsetch-cli
description: 'Use when a task needs live web research: web search for URLs, fetching a page as clean markdown, or crawling a site into markdown. Trigger on "search the web", "fetch/read this URL", "crawl this site/docs", current info beyond training data, bot-walled/JS pages, PDF text extraction.'
license: MIT
compatibility: Requires the `donsetch` CLI on PATH and access to the internet
allowed-tools: Bash(donsetch:*)
metadata:
  author: knopki <knopki@duck.com>
  version: "1.0.0"
  hermes:
    category: research
    complexity: intermediate
    icon: 🌐
    tags:
      - web-search
      - web-fetch
      - web-crawl
      - markdown
      - donsetch
    requires_toolsets:
      - terminal
---

# donsetch CLI

## Overview

Drive the `donsetch` CLI to do web research for an agent: `search`, `fetch`, and
`crawl`. Each command returns clean markdown plus a machine-readable JSON
envelope (`--json`), token-efficient by default, with bot-wall/PDF handling
built in. The MCP server (`donsetch mcp`) exposes the same three tools over
JSON-RPC; this skill uses the CLI form only.

Install if missing, then sanity-check the environment before relying on it:

```bash
command -v donsetch || npm install -f donsetch
donsetch doctor
```

## When to Use

Trigger this skill when live web content is needed:

- The user asks to search the web, look something up online, or get current
  information beyond the model's training data.
- A specific URL must be read as clean markdown (incl. pages behind a bot-wall
  or JS shell, or a PDF).
- A whole site or docs subsite must be extracted into markdown.
- Token cost matters and only the relevant blocks of a long page are wanted.

Do **not** trigger this skill for:

- Code search across public GitHub repos — use the `grep-app-cli` skill
  (literal source matching, not web search).
- Reading files already on the local filesystem — use `read`.

## Decision: which command?

| Need | Command |
|---|---|
| Discover **what** to read (find URLs) | `donsetch search` |
| Read **one** specific URL | `donsetch fetch` |
| Read a **long** docs page efficiently | `fetch --toc`, then `--section` or `--focus` |
| Extract a **multi-page** site/docs | `donsetch crawl` |
| See a site's URL inventory before fetching | `crawl --mode map` |
| Sitemap missing or `map` returned empty | `crawl --mode content` |
| A crawl stopped on budget/deadline | `crawl --resume <token>` |

Pipeline: `search` → pick best URLs → `fetch` (or `crawl` for many pages).

## `donsetch search` — find URLs

```bash
donsetch search rust async trait dyn dispatch
donsetch search "exact phrase" --intent code --max-results 10
donsetch search site:github.com tokio
```

- `--max-results` (default 7, max 12). The top 7 almost always suffice; raise
  only when results are weak.
- `--intent` `auto|web|code|paper|news|entity`. `auto` detects from the query
  and adds verticals: `code` → GitHub/HN/StackExchange/MDN, `paper` →
  Scholar/arXiv, `news` → Google News/HN, `entity` → Wikipedia.
- `--json` for the full envelope; `-q` to silence the stderr stats line.

**Output (text):** numbered list `N. **Title** — domain / snippet / URL`.
**JSON `meta`:** `{intent, weak, cached, elapsed_ms, provider, results[],
engines[]}`. Each result has `consensus` (how many independent engines agreed
— higher is more authoritative) and `score`.

Signals to act on:

- `weak=true` → low cross-engine consensus; treat with care, broaden the query
  or switch intent.
- `engines[].status` ≠ `ok` → `blocked:NNN`, `timeout`, or `no-results` per
  engine; if all are blocked, try a different intent or rephrase.

## `donsetch fetch` — one URL to markdown

```bash
donsetch fetch https://docs.rs/async-trait --focus "dyn trait future boxing"
donsetch fetch https://long-docs-page --toc               # heading outline only
donsetch fetch https://long-docs-page --section "Error handling"
donsetch fetch https://long-docs-page --offset 16000       # resume truncation
donsetch fetch https://a.com/x https://b.com/y            # bulk fetch
```

- `--focus` — the #1 token saver. Hybrid keyword + semantic matching returns
  only relevant blocks (catches different vocabulary than the query); if
  nothing matches, returns the full page with a notice, so it is always safe to
  set. **Always set `--focus` when you know what you are looking for.**
- `--max-chars` (default 16000). Truncated pages expose `next_offset` for
  resumption via `--offset`.
- `--toc` → heading outline only; then target with `--section` (substring,
  case-insensitive) or `--focus`.
- `--selector` — CSS selector to narrow scope precisely.
- `--links` to keep `[text](url)` links (off by default, saves ~30%);
  `--media` to keep images. `--shot <path>` saves a PNG only on interactive
  captcha (not a general screenshot tool). `--json`, `-q`.

**JSON `structuredContent`:** `{status, tier, verdict, thin, content_kind,
title, byline, published, site, blocks_shown, blocks_total, total_chars,
next_offset, tokens_est, url}`. `thin=true` → JS shell, content may be
incomplete; `content_kind` is `Article|Listing|Forum|Docs|Table|Page`;
`isError=true` on block/captcha/network failure.

## `donsetch crawl` — whole site to markdown

```bash
donsetch crawl https://docs.site.com --topic "authentication"
donsetch crawl https://docs.site.com --mode map              # URL inventory only
donsetch crawl https://docs.site.com --max-pages 25 --deadline 300
donsetch crawl https://docs.site.com --resume <token>         # continue after budget stop
```

- `--mode` `full` (default; sitemap map + content) | `map` (cheap URL
  inventory, no content) | `content` (skip sitemap, BFS from seed — use when
  sitemap is missing or `map` returns the wrong/empty set).
- `--topic` — like `--focus` but ranks pages and crawls only matching ones.
  Essential for large sites; without it the crawl wastes budget on noise. Set
  it whenever a specific topic is in mind.
- Budgets: `--max-pages` (default 10, cap 200), `--max-depth` (default 2, 0 =
  seed only), `--max-chars` (total, default 60000, range 4000–500000),
  `--per-page-max` (default 8000, 400–40000), `--deadline` (default 120s,
  range 5–600).
- Filters: `--include`/`--exclude` path globs (e.g. `["/docs/*"]`,
  `["*/tags/*"]`). `--any-host` (default false) to follow cross-domain links.
  `--no-robots` to ignore robots.txt. `--resume` token is valid 30 min.

**JSON `structuredContent`:** `{seed, pages[], map, queued, filtered_out,
skipped[], stop, elapsed_s, resume}`. Each page: `{url, title, kind, chars,
quality}` with `quality ∈ [0,1]` content trust.

`stop` reasons: `FrontierEmpty` (done) · `MaxPages|CharBudget|DepthLimit|`
`Deadline` (budget — use `--resume`) · `ThrottledOut` (host blocked you — wait
and resume).

## Exit codes and error strategy

- `0` success · `1` permanent error · `2` transient (retry) · `3` walled (try
  a different source).
- Retry unchanged only on exit `2` — and only when the cause is plausibly
  transient (e.g. the JSON envelope reports `{"kind":"transient",...}`).
- On exit `3` or a blocked/`no-results` engine, change the source: different
  intent, rephrase, or switch `search` → direct `fetch` of a known URL.
- Do not loop retries on stable `1`/`3`; change the approach instead.

## Common Pitfalls

- **Fetching instead of searching.** `fetch` needs a URL. To discover URLs,
  start with `search`. Fetching a search-engine results URL usually returns the
  bot-walled shell.
- **Skipping `--focus` on long pages.** A docs page can be 50k+ chars. Always
  pass `--focus` (or `--toc`/`--section`) when you know what you want; it cuts
  tokens 50–80% and is safe — full page returns on no match.
- **Using `crawl --mode map` on the wrong seed.** A site-wide sitemap may list
  unrelated pages (e.g. docs.rs' global crate index). If `map` looks wrong or
  empty, use `--mode content` or a more specific seed URL.
- **Crawling without `--topic`.** On a large site, no topic means budget spent
  on noise. Set `--topic` plus `--max-pages`/`--deadline` to bound the effort.
- **Raising `--max-results` reflexively.** Top 7 is usually enough; widen only
  if results are weak.
- **Retrying permanent/walled errors.** Exit `1`/`3` will not fix themselves
  on a same-query retry. Change the source or the query.
- **Ignoring `thin=true`/`isError=true`.** They mark JS shells and failures;
  do not treat such content as authoritative.

## Limits

- Web content is a snapshot, not a guarantee of version/forever behavior. For
  spec- or version-sensitive claims, prefer official docs and cite the URL.
- `consensus`/`quality` signal likely authority, not truth. High consensus
  does not make a claim correct.
- Bot-walled or captcha-protected pages may still return partial/unstable
  content (`thin=true`); flag uncertainty.
- `crawl` resumes are short-lived (30 min); do not store them long-term.

## Verification Checklist

Before reporting results, confirm:

- [ ] Right command chosen: `search` to find, `fetch` for one URL, `crawl` for
  a site.
- [ ] `--focus`/`--topic` set when a specific need is known (token economy);
  or `--toc`/`--section` used for long structured pages.
- [ ] Search results not `weak`; if weak, intent adjusted or query broadened.
- [ ] `thin`/`isError`/`stop`/`skipped` inspected and surfaced (not hidden).
- [ ] Exit code handled: retried only on transient (`2`); approach changed on
  `1`/`3`.
- [ ] URLs cited for any factual claim taken from fetched/crawled content.
- [ ] No claim of authority from `consensus`/`quality` alone.
