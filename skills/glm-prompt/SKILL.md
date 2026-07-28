---
name: glm-prompt
description: 'Use when the user asks to "write a prompt for GLM", "compose a GLM prompt", wants to send a task to a GLM model, needs to launch a GLM subagent. Also use when explicitly named: GLM. Trigger on any request to draft, refine, or assemble a prompt targeting a GLM-family model — for either interactive use or subagent delegation.'
disable-model-invocation: true
license: MIT
metadata:
  author: Sergei Korolev <knopki@duck.com>
  url: https://github.com/knopki/agent-skills
---

# GLM Prompt Skill

## Overview

Build prompts that play to GLM 5.2's strengths and avoid its known failure modes.

Two operating modes:

- **Interactive mode** (prompt is for the end user in this session): run the
  interrogation in §3 — collect the info the user has, then fill the template.
- **Subagent / autonomous mode** (prompt will be sent to a GLM subagent or a
  fresh GLM session): decide the content yourself from available context —
  do NOT interrogate the user. Use §4.

Decide the mode from how the request is phrased:

- "write me a prompt for GLM to do X" / "I want to prompt GLM to…" → interactive.
- "launch a subagent to do X on GLM" / "prepare a prompt for the GLM agent" /
  the prompt is a parameter you pass to a `Task`/`Agent` call → subagent mode.

If the intent is ambiguous, ask one clarifying question: *"Is this prompt for
you to send into a GLM session yourself, or should I write it as a
subagent/Agent task prompt?"* — then proceed.

## When to Use

Trigger this skill whenever you are about to produce a prompt whose target
runtime is a GLM model. Concretely:

- The user asks you to "write / draft / compose a prompt for GLM", "make a
  prompt for GLM", "format this task for GLM".
- You are composing the `prompt:` argument of a `task()` / subagent call that
  will run on a GLM model.
- You are translating a vague user request into a clean DeepSeek task spec.

Do **not** trigger this skill for non-GLM models.

---

## 1) The format — Goal, Context, Constraints, Done

GLM is trained on structured long-horizon tasks. Four sections are
enough for it to plan a trajectory. Use this exact structure:

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
```

How GLM uses each section:

| Section | How GLM uses it | reasoning_effort hint |
| --- | --- | --- |
| Goal | Activates long-horizon planning; builds trajectory | `max` |
| Context | DSA searches for key tokens (paths, names, numbers) | `high` |
| Constraints | GLM respects boundaries better than prior versions | `high` |
| Done | stop criterion — model knows when to stop | `max` or `high` |

---

## 2) Rules of construction

### Rule 0 — Don't put "thinking" instructions in the prompt

GLM ignores prompt directives about thinking. **Never write**:

- "think step by step", "let's think"
- Chinese brackets `【】` (that's a DeepSeek device, ignored by GLM)
- "enable deep thinking", `/think`, `/no_think`
- long persona preambles ("you are a great engineer who…")

Instead: state a clear goal and context. GLM decides how much to think.
Thinking is controlled **only** via API params `thinking.type` and
`reasoning_effort` — not by text.

### Rule 1 — Highlight key tokens

GLM 5.2 uses DeepSeek Sparse Attention (DSA): top-k relevant tokens per
layer. Tokens that aren't salient get skipped. With IndexCache, adjacent
layers share 70–100% of selected tokens, so **the first sentences are
decisive** — they set which tokens the whole network attends to.

Therefore:

- File paths → wrap as `code` or lead with `/` (`~/.config/opencode/...`)
- Function/class/variable names → exact spelling, no paraphrasing
- Numbers, versions, dates → write explicitly (`v13`, `2026-06-17`, `1024`)
- Commands → put in fenced code blocks

**Bad:** "look at the agent protocol file and check the temperature section"

**Good:**

```markdown
### Context

- File: `~/.pi/agent/agents/glm-master.md`
- Section: §2.3 Sampling & output — temperature behavior
- Current: `temperature: 1.0` (creative default)
```

### Rule 2 — Don't issue instructions the model can't execute

GLM controls only its own responses and tool calls. It **cannot**:

| Instruction | Why it fails |
| --- | --- |
| "compress trajectory / delete extra steps" | Model doesn't control message history — the harness does |
| "apply keep-recent-k" | Model can't manage the context window |
| "discard tool-call history" | API gives the model no write access to history |
| "switch thinking.type to disabled" | It's an API param, not a text switch |
| "remove everything but last 5 steps from context" | same as above |

**Write instead:**

- "produce a short summary of what's done — I'll hand it to the harness for `/compact`"
- "emit a `## STITCH COMPRESSION` signal to the harness"
- "write CONFIRMED_FACTS for the handoff section"

### Rule 3 — Pair every "don't" with a "do" (W2 guard)

GLM 5.2 under `max` can stall on negative-only constraints and emit an empty
or delimiter-less first output. Treat this as a structural rule for the
prompts you write:

- `Don't narrate` → `Keep output to results + evidence`.
- `Don't refactor unrelated code` → `Touch only the function that fixes the bug`.
- If you cannot state the positive action, the line is under-specified —
  restate it before sending.

### Rule 4 — Use stop-signals wording for long-horizon prompts

For non-trivial GLM tasks, add one line that names the stop signal so the
model doesn't overthink under `max`:

> Exit thinking and emit the tool call when: you know the tool+args, OR you
> are repeating without new data, OR the next action is fully framed.

### Rule 5 — Evidence-first Done

The `Done` section must give an **observable** check, not "probably works".

- `Validation:` → `command + expected result`
- For a fix: `curl … ; expect { "ok": true }`
- For a refactor: `npm run typecheck && npm test -- grep X` → exit 0
- Bad: "the bug should be gone" / "it should work now".

For ≥2-file or model-affecting changes, add: *run a business-outcome
check, not just a syntax/HTTP-200 proxy.*

---

## 3) Interactive mode — interrogation protocol

When the prompt is for the user to send into a GLM session themselves,
collect what they know before filling the template. Run this as a short
focused dialogue — don't ask all questions at once; group and follow up.

### Round 1 — goal & shape

1. What does the GLM model need to do? (one sentence)
2. Is this a fix, a new feature, an investigation/audit, or a refactor?
3. Is the target GLM 5.2 on the Coding Plan endpoint, or another GLM variant?
  (Coding Plan → Preserved Thinking is on; reuse prior conclusions.)

### Round 2 — context material

For each of these, accept pointers (paths/URLs) over prose:

- Which files and line ranges? (give me paths)
- Current state — if a bug, what exactly is wrong? when does it trigger?
- Why is this being done now? (motivation shapes the trajectory)

### Round 3 — constraints

- What must NOT be touched? (boundaries)
- Language / code style / architecture rules to keep?
- Versions / API contracts / dependencies pinned?

### Round 4 — done

- What command or scenario proves it worked? (must be observable)
- What should the model return — a file edit, a summary, a diff, a report?

### Round 5 — mode & effort (optional, but useful)

- Workflow Mode: if ≥3 deliverables → Plan / Execute / Audit.
- reasoning_effort hint: `high` for standard, `max` for
  debugging/architecture/multi-file.
- For deterministic code (configs, rigid syntax, exact reproduction): advise
  `do_sample: false`.

### Filling

Once you have answers, fill the template in §1 verbatim — short, structured,
key tokens highlighted per Rule 1. Show the finished prompt to the user; do
not send it yourself unless asked.

If the user can't answer something, **leave that field with a clear TODO
placeholder** rather than inventing content — GLM treats invented paths and
numbers as fact and will act on them.

---

## 4) Subagent / autonomous mode

When the prompt is the instruction for a GLM subagent or a fresh GLM Agent
task, you decide the contents from available context. Do not ask the user
the interrogation questions; gather from the codebase/this conversation.

Procedure:

1. Read the target file(s) yourself (or via `codegraph_explore`/`read`).
  Quote real paths and line ranges — never invent.

2. Identify the exact goal and the smallest effective change.

3. Decide Workflow Mode: single deliverable → omit; ≥3 → Plan/Execute/Audit.

4. Decide reasoning_effort: `high` unless the task is debugging / architecture /
  multi-file / long-horizon → `max`.

5. Fill the template. Add the stop-signal line (Rule 4) and the 5-section
  subagent Output Contract if the subagent is expected to report back:
  Output contract:

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

6. For delegation: pick subagent by TASK, not model loyalty —
  semantic/local/audit → GLM-native subagent; web research / mechanical
  verify → DeepSeek. (This skill only writes the prompt; it does not
  enforce the model pick.)

### Bounded effort (fold into the prompt when relevant)

Add effort caps when the subagent could run long:

- audit: 15 calls max · file-search: 5 · web-research: 10 · code-review: 10 ·
  run/verify: 2 attempts per command · 2 same-tool failures in a row → stop.

---

## Common Pitfalls

- **"Think step by step" in the prompt.** GLM ignores thinking directives in
  text. Thinking is controlled only via API params (`thinking.type`,
  `reasoning_effort`). Drop the line; state a clear goal instead.
- **Invented paths / versions / numbers.** GLM treats fabricated specifics as
  fact and will act on them. If a field is unknown, leave a `TODO` placeholder
  rather than guessing.
- **Negative-only constraints.** Bare "don't refactor unrelated code" can stall
  GLM under `max` (W2 guard) and produce empty/delimiter-less output. Pair every
  "don't" with a positive "do".
- **Vague proxies in `Done`.** `curl -I` (HEAD) does not prove a webhook POST; a
  syntax check does not prove business data arrived. Require a business-outcome
  check, especially for ≥2-file or model-affecting changes.
- **Paraphrased key tokens.** DSA searches exact tokens — paraphrasing paths,
  names, versions, or dates causes them to be skipped. Wrap paths as `code`,
  spell names exactly, write numbers explicitly.
- **Missing stop-signal on long-horizon tasks.** Without a named stop condition,
  GLM under `max` can loop or overthink. Add the Rule 4 stop-signal line.
- **Persona preambles.** Long "you are a great engineer who…" openings waste the
  decisive first sentences (IndexCache attention sinks) and don't change
  behavior. Cut them.
- **Interrogating the user in subagent mode.** If the prompt is for a
  subagent/`Task` call, fill it from context yourself — don't run the §3
  dialogue.
- **Inventing context in subagent mode.** Read files yourself; quote real paths
  and line ranges. Never fabricate.
- **Asking GLM for things it does itself.** Self-correction after errors,
  interleaved thinking, DSA selection, IndexCache speedup, state continuity —
  don't request these; they're automatic.
- **Over-delegation for trivial lookups.** Don't ask a subagent to spawn further
  subagents for <3-file, single-step tasks — say "execute directly".
- **Mode-collapse invitations.** Instructions that reward repeating prior
  structure can collapse output. If the task is one of several, name exactly
  which.

## Verification Checklist

Before sending/handing off the prompt, confirm:

- [ ] Mode decided: interactive (§3 interrogation) vs subagent (§4, fill from
  context).
- [ ] Four sections present and in order: `### Goal`, `### Context`, `###
  Constraints`, `### Done`.
- [ ] Goal is 1–2 sentences, states a clear action — no persona preamble.
- [ ] No thinking directives in text: no "think step by step", no `【】`, no
  `/think`, no "enable deep thinking".
- [ ] No model-managed-context instructions: no "compress trajectory", "discard
  history", "apply keep-recent-k", "switch thinking.type".
- [ ] Key tokens highlighted per Rule 1: file paths as `code` or leading `/`,
  exact names, explicit versions/numbers/dates, commands in fenced blocks.
- [ ] Every "don't" paired with a positive "do" (W2 guard).
- [ ] `Done` is evidence-first: a command + expected result (or observable
  scenario), not "should work".
- [ ] For ≥2-file or model-affecting changes: a business-outcome check, not just
  a syntax/HTTP-200 proxy.
- [ ] Stop-signal line present for non-trivial / long-horizon tasks (Rule 4).
- [ ] No invented specifics — unknown fields are `TODO` placeholders, not
  guesses.
- [ ] Subagent mode only: real paths/line ranges quoted from actual file reads;
  no fabrication.
- [ ] Subagent mode only: Output Contract (SUMMARY / EVIDENCE / CHANGES / RISKS
  / BLOCKERS) included when the subagent reports back.
- [ ] Subagent mode only: bounded-effort caps added when the task could run
  long.
- [ ] Subagent mode only: delegation target chosen by task type, not model
  loyalty.
- [ ] reasoning_effort advised correctly: `high` (standard) or `max`
  (debug/arch/multi-file); no `low`/`medium`/`none`/`minimal` (they alias to
  `high`).
- [ ] `do_sample: false` advised for deterministic code; `true` + temp 1.0 for
  creative — kept out of the prompt body, advised to the user.
- [ ] No mode-collapse invitations: if the task is one of several, name
  exactly which.
- [ ] No over-delegation: trivial (<3-file, single-step) lookups executed
  directly, not spawned as further subagents.
- [ ] Prompt is short and structured — first sentences carry the decisive tokens
  (IndexCache / attention sinks).
