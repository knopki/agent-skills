#!/usr/bin/env bash
# Module brief.
# region MODULE_CONTRACT
# PURPOSE: [Describe the GOAL of the module — what business/operational need it fulfills, why.]
# SCOPE:
# - [Main functional areas covered by the module.]
# - NOT: [What is out of scope]
# INVARIANTS: [Condition/State that always holds]
# USECASES:
# - [Entity]: [Actor] => [Action] => [Goal]
# DEPENDENCIES: [Non-trivial deps - CALLS: ..., READS: ..., WRITES: ...]
# RATIONALE:
# - Q: [Why was it implemented this way?]
#   A: [Justification, environmental constraints.]
# KEYWORDS: [Comma-separated keywords for grep search]
# endregion MODULE_CONTRACT

set -euo pipefail

# region LIBRARY_ExampleClass
# PURPOSE: [Goal of the function group and why — what it enables the user/agent to do.]

_example_private_helper_not_needed_for_trivial_helpers() {
  return 0
}

# region FUNC_example_method
# PURPOSE: [Goal of the function, why]
# REQUIRES: [Optional preconditions]
# ENSURES: [Optional postconditions]
# RATIONALE: [Optional rationale]
# Args:
#   $1 - param1 (Optional purpose/semantic meaning of input if non-trivial).
# Outputs:
#   Writes the result to stdout.
example_method() {
  local param1="$1"

  # region BLOCK_calculate_regression Non trivial big block summary
  # ... skip 10 lines
  echo "Pre calculation" >&2
  # ... skip 10 lines
  local result=$((param1 * 2))
  # endregion BLOCK_calculate_regression

  echo "$result"
}
# endregion FUNC_example_method

# endregion LIBRARY_ExampleClass

_example_private_function_not_needed_for_trivial_functions() {
  return 0
}

# region FUNC_example_function
# PURPOSE: [Describe the GOAL of this function and why.]
# Args:
#   $@ - data (Optional purpose/semantic meaning of input if non-trivial).
# Outputs:
#   Writes the sum to stdout.
example_function() {
  echo "INIT" >&2

  # region BLOCK_loop
  local total=0
  local item
  for item in "$@"; do
    total=$((total + item))
    echo "Loop step" >&2 # block name + structured data to stderr
  done
  # endregion BLOCK_loop

  echo "RESULT" >&2
  echo "$total"
}
# endregion FUNC_example_function
