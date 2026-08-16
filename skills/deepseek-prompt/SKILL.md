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

This skill operates in two lanes (how *you* use it):

- **Interactive mode** (prompt is for the end user in this session): run the
  interrogation in §3 — collect the info the user has, then fill the template.
- **Subagent / autonomous mode** (prompt will be sent to a DeepSeek subagent or
  a fresh DeepSeek session): decide the content yourself from available context
  — do NOT interrogate the user. Use §4.

Separately, DeepSeek V4 itself has **three thinking modes** you can force by
appending a Chinese instruction block — Default / Pure Analysis / Role
Immersion. That is the prompt-injection mechanism this skill relies on; see
*Three thinking modes — when and whether to inject* below.

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

## Three thinking modes — when and whether to inject

DeepSeek V4 (API `deepseek-v4-pro` / `deepseek-v4-flash`, and the official
APP/web client in **Expert Mode**) has three thinking styles. You choose one by
appending a Chinese instruction block to the **end of the first user message**
— the training-native injection position, and the most stable. Putting it in the
system prompt is markedly less reliable.

| Mode | What you append | Thinking looks like |
| :--: | :-- | :-- |
| **Default** | nothing | Model auto-selects by scenario complexity |
| **Pure Analysis** | `【思维模式要求】` block | Pure logical analysis only — no inner monologue, no parenthetical asides |
| **Role Immersion** | `【角色沉浸要求】` block | First-person inner monologue wrapped in parentheses |

**When and whether to inject — the precise rule:**

- Inject **only when you want to force a specific thinking style.**
- **Engineering / analysis / structured tasks → Pure Analysis**
  (`【思维模式要求】`): stable structure, no roleplay drift.
- **Roleplay / creative / emotional tasks → Role Immersion**
  (`【角色沉浸要求】`): more authentic emotion in the reply.
- **Otherwise, or when the model's own choice is fine → Default** (inject
  nothing): the model auto-selects, often toward analysis on complex tasks.
  Don't inject "just in case" — an unused block is noise.

So the injection block is **not mandatory**. Reach for Pure Analysis when you
must *guarantee* no roleplay thinking (most engineering work); reach for Role
Immersion only for character/creative work; otherwise leave it in Default.

**Effort vs. style — don't conflate them.** The injection controls the thinking
*style*. It is orthogonal to thinking *effort* — the `reasoning_effort` API
param (Fast/Explore/Standard/Complex), which controls *how much* the model
thinks and cannot be switched by prompt text. Set both: effort via the API
param, style via the block.

**Effect is probabilistic and acts on thinking only.** A 100% trigger rate is
not guaranteed; the block raises the probability of the expected format. If it
does not take on the first try, re-roll (regenerate). The instruction affects
only the thinking process; it influences the final reply only indirectly —
Pure Analysis → more stable structure, Role Immersion → more authentic emotion.

**Scope:** API (`deepseek-v4-pro`, `deepseek-v4-flash`) and the APP/web client
**Expert Mode**. The APP/web **Quick Mode ignores the block** — don't promise
its effect there.

### Canonical blocks (copy verbatim)

**Pure Analysis Mode:**

```text
【思维模式要求】在你的思考过程（<think>标签内）中，请遵守以下规则：
1. 禁止使用圆括号包裹内心独白，例如"（心想：……）"或"(内心OS：……)"，所有分析内容直接陈述即可
2. 禁止以角色第一人称描写内心活动，例如"我心想""我觉得""我暗自"等，请用分析性语言替代
3. 思考内容应聚焦于剧情走向分析和回复内容规划，不要在思考中进行角色扮演式的内心戏表演
```

**Role Immersion Mode:**

```text
【角色沉浸要求】在你的思考过程（<think>标签内）中，请遵守以下规则：
1. 请以角色第一人称进行内心独白，用括号包裹内心活动，例如"（心想：……）"或"(内心OS：……)"
2. 用第一人称描写角色的内心感受，例如"我心想""我觉得""我暗自"等
3. 思考内容应沉浸在角色中，通过内心独白分析剧情和规划回复
```

### Luck-based alternative (not trained for roleplay)

`<｜begin▁of▁thinking｜>` is DeepSeek's fixed thinking-start token. Forcing the
thinking to begin with a chosen token (e.g. `**Hmm**`, `**Okay**`) can push the
model into a different reasoning pattern (QA / writing / reasoning / Agent).
This is **not** specially trained for roleplay and "depends on luck," so treat
it as a fallback, not a primary lever:

```text
Your thinking output must strictly start with `<｜begin▁of▁thinking｜>**Hmm**`
verbatim, only output the thinking once, and must not repeat the output of
`<｜begin▁of▁thinking｜>`.
```

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

【思维模式要求】在你的思考过程（<think>标签内）中，请遵守以下规则：
1. 禁止使用圆括号包裹内心独白，例如"（心想：……）"或"(内心OS：……)"，所有分析内容直接陈述即可
2. 禁止以角色第一人称描写内心活动，例如"我心想""我觉得""我暗自"等，请用分析性语言替代
3. 思考内容应聚焦于剧情走向分析和回复内容规划，不要在思考中进行角色扮演式的内心戏表演
```

Two structural choices are DeepSeek-specific and sourced from the official
prompting guide and injection-block doc:

| Choice | Why it matters on DeepSeek V4 |
| --- | --- |
| Constraints placed **before** the injection block | Per the prompt guide, constraints go on their own line right before `【思维模式要求】` so the block doesn't bury them |
| Injection block `【思维模式要求】` at the end | Training-native switch to Pure Analysis thinking; suppresses roleplay monologue (per injection-block doc) |

§1 uses the **Pure Analysis** block — the engineering default. See *Three
thinking modes — when and whether to inject* for when to use Default (inject
nothing) or Role Immersion instead, and Rule 4 for the engineering-hardened
variant.

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

### Rule 4 — Pick the thinking mode; inject only when forcing a style

See *Three thinking modes — when and whether to inject* for the full decision.
The short version: inject **Pure Analysis** (`【思维模式要求】`) for
engineering/analysis tasks where you must guarantee no roleplay thinking;
inject **Role Immersion** (`【角色沉浸要求】`) for character/creative work;
otherwise use **Default** (inject nothing — the model auto-selects). The block
goes at the end of the first user message, after one blank line.

The block is **not mandatory**. Default mode already biases toward analysis on
complex tasks; inject Pure Analysis only when you need to lock it in. Without
it on a hard task, DeepSeek V4 *may* drift into roleplay-style thinking —
internal monologue, "hmm", "I think...", parenthetical asides — and toward
commentary over execution, but this is not guaranteed, which is exactly why the
block exists as an override rather than a default.

**Engineering-hardened variant (optional — a skill extension, not the official
block).** The canonical Pure Analysis block (see *Three thinking modes*) is the
training-native 3-rule form and the most reliable trigger. For demanding
engineering tasks you may append two extra rules to steer the analysis itself;
since these are not part of the trained block, prefer the canonical form when
trigger reliability matters most:

```text
【思维模式要求】在你的思考过程（<think>标签内）中，请遵守以下规则：
1. 禁止使用圆括号包裹内心独白，例如"（心想：……）"或"(内心OS：……)"，所有分析内容直接陈述即可
2. 禁止以第一人称描写内心活动，例如"我心想""我觉得""我暗自"等，请用分析性语言替代
3. 思考内容只包含：约束条件、陷阱识别、工具选择、执行步骤。禁止角色扮演式的内心戏
4. 复杂任务使用结构化分析：UNDERSTAND→ANALYZE→APPROACH→PLAN→CRITIQUE
5. 路径明确时跳过思考，立即执行工具调用
```

### Rule 5 — `【】` safety: sanitize attached files

**Critical.** DeepSeek V4 processes **any** `【】` instruction block in
context at training-level priority. A file loaded into the prompt that contains
`【角色沉浸要求】` or `【思维模式要求】` (or any other `【】` block) **overrides**
the thinking mode you intended — forcing Role Immersion or Pure Analysis
regardless of your choice → wrong thinking style, ignored tool calls,
degradation within 1–2 turns.

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
which controls thinking **effort** (how much the model thinks). It is separate
from the thinking **mode/style** controlled by the injection block (see *Three
thinking modes*); `reasoning_effort` is the main effort regulator and text in
the prompt does not change it:

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

- **Injecting the wrong mode — or injecting for no reason.** There are three
  thinking modes (Default / Pure Analysis / Role Immersion). Pick by task:
  Pure Analysis `【思维模式要求】` for engineering/analysis, Role Immersion
  `【角色沉浸要求】` for roleplay/creative, Default (inject nothing) when the
  model's own choice is fine. Don't inject "just in case," and never use
  `【角色沉浸要求】` for an engineering task — it forces inner-monologue
  thinking. The block is optional, not mandatory.
- **`【】` blocks in attached files.** Any `【】` in loaded context (either
  `【角色沉浸要求】` or `【思维模式要求】`) overrides the mode you chose at
  training priority → wrong style, ignored tools, fast degradation. Sanitize
  attachments (Rule 5).
- **Expecting a 100% trigger.** The block raises the probability of the target
  thinking style; it does not guarantee it. If the first reply still shows
  roleplay thinking despite a Pure Analysis block, re-roll instead of assuming
  the approach failed.
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
- [ ] Thinking mode chosen by task type — Default (inject nothing) / Pure
  Analysis `【思维模式要求】` (engineering, analysis) / Role Immersion
  `【角色沉浸要求】` (roleplay, creative). Block appended at the end of the
  first user message, after one blank line, **only when forcing a mode**.
  Canonical verbatim CN block preferred.
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
