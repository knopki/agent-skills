---
title: "Example Document"
description: "Module brief."
license: MIT
---

<!-- #region MODULE_CONTRACT -->
<!-- PURPOSE: [Describe the GOAL of the document — what business/operational
     need it fulfills, why.]
SCOPE:
- [Main functional areas covered by the document.]
- NOT: [What is out of scope]
INVARIANTS: [Condition/State that always holds]
USECASES:
- [Entity]: [Actor] => [Action] => [Goal]
DEPENDENCIES: [Non-trivial deps - REFERENCES: ..., LINKS: ...]
RATIONALE:
- Q: [Why was it written this way?]
  A: [Justification, environmental constraints.]
KEYWORDS: [Comma-separated keywords for grep search]
<!-- #endregion MODULE_CONTRACT -->

<!-- #region SECTION_overview -->

## Overview

Optional brief for the document.

<!-- #endregion SECTION_overview -->

<!-- #region SECTION_architecture -->

## Architecture

<!-- #region BLOCK_diagram -->

### Diagram

```text
[A] --> [B] --> [C]
```

<!-- #endregion BLOCK_diagram -->

<!-- #region SUBSECTION_components -->

### Components

- **Component A**: [purpose]
- **Component B**: [purpose]

<!-- #endregion SUBSECTION_components -->

Trivial paragraph — markup not needed.

<!-- #region BLOCK_data_flow -->

### Data flow

Non-trivial big block summary.

1. [Step 1]
2. [Step 2]
3. [Step 3]

<!-- #endregion BLOCK_data_flow -->
<!-- #endregion SECTION_architecture -->

<!-- #region SECTION_usage -->

## Usage

<!-- #region SUBSECTION_cli -->

### CLI

```bash
example-command --flag value
```

<!-- #endregion SUBSECTION_cli -->

<!-- #region SUBSECTION_api -->

### API

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET    | `/items` | List items  |
| POST   | `/items` | Create item |

<!-- #endregion SUBSECTION_api -->
<!-- #endregion SECTION_usage -->

<!-- #region SECTION_appendix -->

## Appendix

<!-- #region SUBSECTION_glossary -->

### Glossary

- **Term A**: [definition]
- **Term B**: [definition]

<!-- #endregion SUBSECTION_glossary -->

<!-- #region SUBSECTION_references -->

### References

- [Reference 1](https://example.com/ref1)
- [Reference 2](https://example.com/ref2)

<!-- #endregion SUBSECTION_references -->
<!-- #endregion SECTION_appendix -->
