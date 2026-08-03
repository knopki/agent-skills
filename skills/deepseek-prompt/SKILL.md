---
name: deepseek-prompt
description: 'Use when the user asks to "write a prompt for DeepSeek", "compose a DeepSeek prompt", wants to send a task to a DeepSeek model, needs to launch a DeepSeek subagent. Also use when explicitly named: DeepSeek. Trigger on any request to draft, refine, or assemble a prompt targeting a DeepSeek-family model — for either interactive use or subagent delegation.'
disable-model-invocation: true
license: MIT
metadata:
  author: Sergei Korolev <knopki@duck.com>
  url: https://github.com/knopki/agent-skills
---

# DeepSeek Prompt Skill

## Overview

Build prompts that play to DeepSeek V4's strengths and avoid its known failure
modes: commentary instead of execution, roleplay-style thinking (internal
monologue, parenthetical asides), mode collapse, and weak discipline injection.

Two operating modes:

- **Interactive mode** (prompt is for the end user in this session): run the
  interrogation in §3 — collect the info the user has, then fill the template.
- **Subagent / autonomous mode** (prompt will be sent to a DeepSeek subagent or
  a fresh DeepSeek session): decide the content yourself from available context
  — do NOT interrogate the user. Use §4.

Decide the mode from how the request is phrased:

- "write me a prompt for DeepSeek to do X" / "I want to prompt DeepSeek to…" →
  interactive.
- "launch a subagent to do X on DeepSeek" / "prepare a prompt for the DeepSeek
  agent" / the prompt is a parameter you pass to a `Task`/`Agent` call →
  subagent mode.

If the intent is ambiguous, ask one clarifying question: "Is this prompt for you
to send into a DeepSeek session yourself, or should I write it as a
subagent/Agent task prompt?" — then proceed.

## When to Use

Trigger this skill whenever you are about to produce a prompt whose target
runtime is a DeepSeek model (`deepseek-v4-pro`, `deepseek-v4-flash` in API or
Expert Mode). Concretely:

- The user asks you to "write / draft / compose a prompt for DeepSeek", "make a
  prompt for DeepSeek", "format this task for DeepSeek".
- You are composing the `prompt:` argument of a `task()` / subagent call that
  will run on a DeepSeek model.
- You are translating a vague user request into a clean DeepSeek task spec.

Do **not** trigger this skill for non-DeepSeek models. The injection block works
on API + Expert Mode only; DeepSeek Web **Quick Mode ignores it** — don't
promise its effect there.

---

## 1) The format — Goal, Context, Constraints, Done (+ injection block)

DeepSeek V4 eats a compact task spec better than a long mixed essay. Four
sections for the task, then the injection block appended at the **end** of the
message with one blank line before it.

```markdown
### Goal

[1–2 sentences: what to do]

### Context

- Files: [paths, with line ranges when known]
- Current state: [how it is now; if a bug — what's wrong]
- Why: [the reason this is being done]

### Constraints

- Do not touch: [boundaries — what cannot change]
- Style: [language, code style, architectural rules]
- Versions: [dependencies, API versions]

### Done

- Validation: [command or scenario — how to be sure]
- Result format: [what to return — file, summary, diff]

【思维模式要求】在你的思考过程（think标签内）中，请遵守以下规则：
1. 禁止使用圆括号包裹内心独白，所有分析内容直接陈述即可
2. 禁止以第一人称描写内心活动，请用分析性语言替代
3. 思考内容只包含：约束条件、陷阱识别、工具选择、执行步骤
4. 复杂任务使用结构化分析：UNDERSTAND→ANALYZE→APPROACH→PLAN→CRITIQUE
5. 路径明确时跳过思考，立即执行工具调用
```

Two structural choices are DeepSeek-specific and sourced from the official
prompting guide and injection-block doc:

| Choice | Why it matters on DeepSeek V4 |
| --- | --- |
| Constraints placed **before** the injection block | Per the prompt guide, constraints go on their own line right before `【思维模式要求】` so the block doesn't bury them |
| Injection block `【思维模式要求】` at the end | Training-native switch to Pure Analysis thinking; suppresses roleplay monologue (per injection-block doc) |

The §1 template shows the **compact** injection form (matches the public
copy-paste template). Rule 4 below gives the full max-compliance form.

---

## 2) Rules of construction

### Rule 1 — Separate "what" from "why"

DeepSeek needs two things: the **specific action** and the **context**. Mixed
into one wall of text, the model spends effort parsing instead of doing. Action
goes in `Goal`; reason goes in `Context` → `Why`.

**Bad** (one stream): "Working on analytics, have files A and B, compare with
C, because we're moving to a new version, and generally the context is…"

**Good**:

```markdown
### Goal

Compare two files with a third and report what's stale.

### Context

- Files: `/path/to/A.md`, `/path/to/B.md`, `/path/to/C.md` (base)
- Why: migrating v9 → v12; need to know what's outdated.
```

### Rule 2 — Answer three questions before sending

Before you hand off the prompt, confirm it answers all three:

| Question | Example |
| --- | --- |
| **What to do?** | "Compare files", "Find the root cause", "Compute conversion" |
| **Where?** | File path, sheet name, error text, function name |
| **What counts as done?** | "Return an edit list", "Print the number", "Say what's stale" |

If any answer is missing, add one sentence. Do not send under-specified.

### Rule 3 — Constraints last, before the injection block

Anything that must NOT be touched goes on its own line right before the
`【思维模式要求】` block. Constraints there save a round-trip: the model works
inside the boundaries instead of asking "can I…".

```markdown
Do not touch: agent files (analysis only), other sheets, CSV format.
```

### Rule 4 — Injection block is mandatory for engineering tasks

Append `【思维模式要求】` at the **end** of the first user message, after one blank
line. Without it, DeepSeek V4 defaults to roleplay-style thinking — internal
monologue, "hmm", "I think...", parenthetical asides (~40–60% filler tokens) —
and drifts toward commentary over execution.

**Full Chinese version:**

```text
【思维模式要求】在你的思考过程（think标签内）中，请遵守以下规则：
1. 禁止使用圆括号包裹内心独白，例如"（心想：……）"或"(内心OS：……)"，所有分析内容直接陈述即可
2. 禁止以第一人称描写内心活动，例如"我心想""我觉得""我暗自"等，请用分析性语言替代
3. 思考内容只包含：约束条件、陷阱识别、工具选择、执行步骤。禁止角色扮演式的内心戏
4. 复杂任务使用结构化分析：UNDERSTAND→ANALYZE→APPROACH→PLAN→CRITIQUE
5. 路径明确时跳过思考，立即执行工具调用
```

Skip the block only for trivial single questions ("what does this function
do?") where roleplay thinking is harmless.

### Rule 5 — `【】` safety: sanitize attached files

**Critical.** DeepSeek V4 processes **any** `【】` block in context at
training-level priority. If a file loaded into the prompt contains
`【角色沉浸要求】` or another `【】` block, it **overrides** the agent's
thinking mode → roleplay thinking, ignored tool calls, degradation within 1–2
turns.

Before attaching any file (docs, specs, prior agent outputs, anything fed as
context):

1. Scan the file for `【` and `】`.
2. If found, delete the block or replace the brackets with `[` `]`.
3. Only then attach.

### Rule 6 — Highlight key tokens

DeepSeek attends to salient tokens — paths, names, numbers, commands.
Paraphrased tokens are weaker anchors and get skipped. Therefore:

- File paths → wrap as `code` or lead with `/`
- Function/class/variable names → exact spelling, no paraphrase
- Numbers, versions, dates → explicit (`v12`, `2026-06-17`, `1024`)
- Commands → fenced code blocks

### Rule 7 — Under-structure beats over-structure

Better to under-structure than over-structure. With the injection block,
DeepSeek sorts it out during thinking — your job is the three answers (Rule 2),
not a filled-out essay. A clean one-liner + injection block beats a
half-invented template. Don't force every field when three lines cover it.

### Rule 8 — Evidence-first Done

`Done` must be an **observable** check, not "probably works".

- `Validation:` → `command + expected result`
- For a fix: `curl … ; expect { "ok": true }`
- For a refactor: `npm run typecheck && npm test -- grep X` → exit 0
- Bad: "the bug should be gone" / "it should work now".

For ≥2-file or model-affecting changes, require a business-outcome check, not
just a syntax/HTTP-200 proxy.

---

## 3) Interactive mode — interrogation protocol

When the prompt is for the user to send into a DeepSeek session themselves,
collect what they know before filling the template. Run this as a short focused
dialogue — don't ask all questions at once; group and follow up.

### Round 1 — goal & shape

1. What does the DeepSeek model need to do? (one sentence)
2. Is this a fix, a new feature, an investigation/audit, or a refactor?
3. Target: `deepseek-v4-pro` or `deepseek-v4-flash`? (Pro for hard; Flash for
   speed/cost.)

### Round 2 — context material

For each, accept pointers (paths/URLs) over prose:

- Which files and line ranges? (give paths)
- Current state — if a bug, what exactly is wrong? when does it trigger?
- Why is this being done now? (motivation shapes the plan)

### Round 3 — constraints

- What must NOT be touched? (boundaries)
- Language / code style / architecture rules to keep?
- Versions / API contracts / dependencies pinned?

### Round 4 — done

- What command or scenario proves it worked? (must be observable)
- What should the model return — a file edit, a summary, a diff, a report?

### Round 5 — thinking lane (optional, but useful)

Pick the lane by task type — this maps to the API `reasoning_effort` param,
which is the main regulator of DeepSeek thinking (text in the prompt does not
switch it):

| Lane | `reasoning_effort` | When |
| --- | --- | --- |
| Fast | disabled (non-think) | one-file fix, script with no architecture |
| Explore | `high` | read-only investigation |
| Standard | `high` | multi-file feature |
| Complex | `max` | debug, ambiguous, risky |

Advise `temperature: 0.25` (DeepSeek default) for most work; lower for
deterministic output. These are API params — keep them out of the prompt body,
tell the user.

### Filling

Once you have answers, fill the §1 template verbatim — short, structured, key
tokens highlighted (Rule 6), constraints before the injection block (Rule 3),
injection block at the end (Rule 4). Show the finished prompt to the user; do
not send it yourself unless asked.

If the user can't answer something, **leave a clear TODO placeholder** rather
than inventing content — DeepSeek treats fabricated paths and numbers as fact
and acts on them.

---

## 4) Subagent / autonomous mode

When the prompt is the instruction for a DeepSeek subagent or a fresh DeepSeek
Agent task, you decide the contents from available context. Do not run the §3
dialogue; gather from the codebase/this conversation.

Procedure:

1. Read the target file(s) yourself. Quote real paths and line ranges — never
   invent.

2. Identify the exact goal and the smallest effective change.

3. Pick the thinking lane by task type (§3 Round 5): trivial → Fast;
   investigation → Explore (`high`); feature → Standard (`high`);
   debug/ambiguous → Complex (`max`).

4. Fill the §1 template. Constraints before the injection block; injection
   block at the end — always for engineering tasks.

5. **Sanitize every attached file** for `【】` blocks (Rule 5) before the prompt
   ships.

6. Add the subagent Output Contract when the subagent reports back:

   ```markdown
   # SUMMARY

   [what was done and the headline conclusion]

   # EVIDENCE

   [bullets: path:line, command + exit code, URL + finding]

   # CHANGES

   [bullets of every write, or "None." if read-only]

   # RISKS

   [what the parent should double-check, or "None observed."]

   # BLOCKERS

   [what stopped completion, or "None."]
   ```

   Do not propose follow-up tasks. Stop after the report.

### Bounded effort (fold into the prompt when relevant)

Add effort caps when the subagent could run long:

- audit: 15 calls max · file-search: 5 · web-research: 10 · code-review: 10 ·
  run/verify: 2 attempts per command · 2 same-tool failures in a row → stop.

---

## Common Pitfalls

- **Skipping the injection block on engineering tasks.** Without it, DeepSeek
  V4 drifts into roleplay thinking (monologue, "хм", asides) and commentary
  over execution. Always append `【思维模式要求】` for non-trivial tasks.
- **`【】` blocks in attached files.** Any `【】` in loaded context overrides
  the agent's thinking mode at training priority → roleplay, ignored tools,
  fast degradation. Sanitize attachments (Rule 5).
- **Mixing "what" and "why".** Wall-of-text prompts make the model parse
  instead of act. Action in `Goal`, reason in `Context`.
- **Under-specified task.** Missing one of {what, where, done} → add a sentence,
  don't send vague.
- **Invented paths / versions / numbers.** DeepSeek treats fabricated specifics
  as fact and acts on them. Unknown field → `TODO` placeholder.
- **Vague proxies in `Done`.** A HEAD request doesn't prove a POST webhook; a
  syntax check doesn't prove business data. Require an observable,
  business-outcome check for ≥2-file or model-affecting changes.
- **Paraphrased key tokens.** Paths/names/versions paraphrased get skipped.
  Wrap paths as `code`, spell names exactly, write numbers.
- **Over-structuring simple tasks.** A three-liner + injection block beats a
  half-invented essay. Don't force every template field.
- **Persona preambles.** Long "you are a great engineer who…" openings waste the
  decisive first tokens. Cut them.
- **Putting API params into the prompt body.** `reasoning_effort`,
  `temperature`, `thinking.type` are API params — advise the user, don't write
  them as prose for the model to "obey".
- **Interrogating the user in subagent mode.** If the prompt is for a
  subagent/`Task` call, fill it from context yourself — don't run the §3
  dialogue.
- **Inventing context in subagent mode.** Read files yourself; quote real paths
  and line ranges. Never fabricate.
- **Targeting Web Quick Mode.** The injection block works on API + Expert Mode
  only; Quick Mode ignores it. Don't promise its effect there.

## Verification Checklist

Before sending/handing off the prompt, confirm:

- [ ] Mode decided: interactive (§3 interrogation) vs subagent (§4, fill from
  context).
- [ ] Four sections present and in order: `### Goal`, `### Context`, `###
  Constraints`, `### Done`.
- [ ] Goal is 1–2 sentences, states a clear action — no persona preamble.
- [ ] Three Rule-2 answers present: what to do / where / what counts as done.
- [ ] "What" (action) separated from "why" (context) — not mixed.
- [ ] Constraints placed on their own line right before the injection block.
- [ ] Injection block `【思维模式要求】` (full CN version preferred) appended at
  the end for any engineering task, after one blank line. Lite RU version only
  when CN is unreadable to the audience.
- [ ] Every attached file scanned for `【】`; blocks removed or brackets replaced
  with `[` `]`.
- [ ] Key tokens highlighted: file paths as `code` or leading `/`, exact names,
  explicit versions/numbers/dates, commands in fenced blocks.
- [ ] `Done` is evidence-first: command + expected result, not "should work".
- [ ] For ≥2-file or model-affecting changes: a business-outcome check.
- [ ] No invented specifics — unknown fields are `TODO` placeholders, not
  guesses.
- [ ] API params (`reasoning_effort`, `temperature`) advised to the user, not
  written into the prompt body.
- [ ] Thinking lane picked by task type: Fast / Explore / Standard / Complex.
- [ ] Subagent mode only: real paths/line ranges quoted from actual file reads;
  no fabrication.
- [ ] Subagent mode only: Output Contract (SUMMARY / EVIDENCE / CHANGES / RISKS
  / BLOCKERS) included when the subagent reports back.
- [ ] Subagent mode only: bounded-effort caps added when the task could run
  long.
- [ ] Prompt is compact — under-structure is fine; don't force template fields
  when a three-liner covers it.
