/**
 * Counter widget module.
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

import { useCallback, useEffect, useState } from "react";

// this is just for decorator example
function sealed(constr: Function) {
  Object.seal(constr);
  Object.seal(constr.prototype);
}

interface CounterProps {
  initialValue?: number;
  step?: number;
}

// #region CLASS_CounterFormatter
/**
 * Formats counter values for display.
 *
 * @purpose [Goal of the class and why — what it enables the user/agent to do.]
 */
@sealed
class CounterFormatter {
  format(value: number): string {
    return String(value);
  }
}
// #endregion CLASS_CounterFormatter

// #region COMPONENT_Counter
/**
 * @purpose [Render an interactive counter with increment/decrement controls.]
 * @requires [Optional preconditions]
 * @ensures [Optional postconditions]
 * @rationale [Optional rationale]
 */
export function Counter({ initialValue = 0, step = 1 }: CounterProps) {
  // #region BLOCK_init
  const [count, setCount] = useState(initialValue);
  const formatter = new CounterFormatter();
  // #endregion BLOCK_init

  // #region BLOCK_handlers
  const handleIncrement = useCallback(() => {
    setCount((c) => c + step);
  }, [step]);

  const handleDecrement = useCallback(() => {
    setCount((c) => c - step);
  }, [step]);
  // #endregion BLOCK_handlers

  // #region BLOCK_persist
  // ... skip 10 lines
  useEffect(() => {
    localStorage.setItem("counter", String(count));
  }, [count]);
  // ... skip 10 lines
  // #endregion BLOCK_persist

  return (
    <div className="counter">
      <button onClick={handleDecrement} aria-label="decrement">
        -
      </button>
      <span>{formatter.format(count)}</span>
      <button onClick={handleIncrement} aria-label="increment">
        +
      </button>
    </div>
  );
}
// #endregion COMPONENT_Counter

// #region FUNC_useCounter
/**
 * @purpose Encapsulate counter state logic for reuse across components.
 */
export function useCounter(initial: number = 0) {
  const [count, setCount] = useState(initial);
  const increment = useCallback(() => setCount((c) => c + 1), []);
  const decrement = useCallback(() => setCount((c) => c - 1), []);
  return { count, increment, decrement };
}
// #endregion FUNC_useCounter
