/**
 * Module brief.
 * #region moduleContract
 * @modulecontract
 * @purpose [Describe the GOAL of the module — what business/operational need it fulfills, why.]
 * @scope
 *  - [Main functional areas covered by the module.]
 *  - NOT: [What is out of scope]
 * @invariants
 *  - [Condition/State that always holds]
 * @usecases
 *  - [Entity]: [Actor] => [Action] => [Goal]
 * @dependencies [Non-trivial deps - USES API: ..., READS: ..., WRITES: ...]
 * @rationale
 *  - Q: [Why was it implemented this way?]
 *    A: [Justification, environmental constraints.]
 * @keywords [Comma-separated keywords for grep search]
 * #endregion moduleContract
 **/

// this is just for decorator example
function frozen(target: Function) {
  Object.freeze(target);
  Object.freeze(target.prototype);
}

// #region CLASS_ExampleClass
/**
 * Class brief.
 *
 * @purpose [Goal of the class and why — what it enables the user/agent to do.]
 */
@frozen
export class ExampleClass {
  private privateMethodMarkupNotNeededForTrivialMethods(): number {
    return 1;
  }

  // #region METHOD_exampleMethod
  /**
   * Optional brief.
   *
   * @purpose [Goal of the method, why]
   * @requires [Optional preconditions]
   * @ensures [Optional postconditions]
   * @rationale [Optional rationale]
   * @param param1 - Optional purpose/semantic meaning of input if non-trivial.
   * @returns Optional purpose/semantic meaning of output if non-trivial.
   */
  exampleMethod(param1: number): string {
    // #region BLOCK_calculateRegression Non trivial big block summary
    this.privateMethodMarkupNotNeededForTrivialMethods();
    // ... skip 10 lines
    console.debug("Pre calculation", { event: "start", param1 }); // block name + structured data
    // ... skip 10 lines
    const result = String(param1 * 2);
    // #endregion BLOCK_calculateRegression
    console.debug("Business result", { result });
    return result;
  }
  // #endregion METHOD_exampleMethod
}
// #endregion CLASS_ExampleClass

function privateFunctionMarkupNotNeededForTrivialFunctions(): void {
  // no-op
}

// #region FUNC_exampleFunction
/**
 * @purpose [Describe the GOAL of this function and why.]
 */
export function exampleFunction(data: number[]): number {
  console.debug("INIT", { dataLength: data.length });
  privateFunctionMarkupNotNeededForTrivialFunctions();

  // #region BLOCK_loop
  let total = 0;
  for (const item of data) {
    total += item;
    console.debug("Loop step", { item, runningTotal: total });
  }
  // #endregion BLOCK_loop

  console.debug("RESULT", { sumComputed: total });
  return total;
}
// #endregion FUNC_exampleFunction
