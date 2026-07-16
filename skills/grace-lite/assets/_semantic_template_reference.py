"""Module brief."""
# region MODULE_CONTRACT
# PURPOSE: [Describe the GOAL of the module — what business/operational need it fulfills, why.]
# SCOPE:
# - [Main functional areas covered by the module.]
# - NOT: [What is out of scope]
# INVARIANTS: [Condition/State that always holds]
# USECASES:
# - [Entity]: [Actor] => [Action] => [Goal]
# DEPENDENCIES: [Non-trivial deps - USES API: ..., READS: ..., WRITES: ...]
# RATIONALE:
# - Q: [Why was it implemented this way?]
#   A: [Justification, environmental constraints.]
# KEYWORDS: [Comma-separated keywords for grep search]
# endregion MODULE_CONTRACT

import logging
from functools import cache

logger = logging.getLogger(__name__)

# Module Public API
__all__ = ["ExampleClass", "example_function"]


# region CLASS_ExampleClass
# PURPOSE: [Goal of the class and why — what it enables the user/agent to do.]
class ExampleClass:
    """Class brief."""

    def _private_method_markup_not_needed_for_trivial_methods(self) -> None:
        raise NotImplementedError

    # region METHOD_example_method
    # PURPOSE: [Goal of the method, why]
    # REQUIRES: [Optional precoditions]
    # ENSURES: [Optional postconditions]
    # RATIONALE: [Optional rationale]
    def example_method(self, param1: int) -> str:
        """Optional brief.

        Args:
            param1: Optional purpose/semantic meaning of input if non-trivial.
        """
        # region BLOCK_calculate_regression Non trivial big block summary
        # ... skip 10 lines
        logger.debug(
            "Pre calculation",
            extra={"event": "start", "param1": param1},
        )  # block name + structured data
        # ... skip 10 lines
        result = str(param1 * 2)
        # endregion BLOCK_calculate_regression
        logger.debug("Business result", extra={"result": result})
        return result

    # endregion METHOD_example_method


# endregion CLASS_ExampleClass


def _private_function_markup_not_needed_for_trivial_functions() -> None:
    pass


# region FUNC_example_function
# PURPOSE: [Describe the GOAL of this function and why.]
@cache
def example_function(data: list) -> int:
    logger.debug("INIT", extra={"data_length": len(data)})

    # region BLOCK_loop
    total = 0
    for item in data:
        total += item
        logger.debug("Loop step", extra={"item": item, "running_total": total})
    # endregion BLOCK_loop

    logger.debug("RESULT", extra={"sum_computed": total})
    return total


# endregion FUNC_example_function
