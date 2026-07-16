/// <summary>
/// Module brief.
/// </summary>
/// <contract>
/// <purpose>[Describe the GOAL of the module — what business/operational need it fulfills, why.]</purpose>
/// <scope>
///   [Main functional areas covered by the module.]
///   NOT: [What is out of scope]
/// </scope>
/// <invariants>
///   [Condition/State that always holds]
/// </invariants>
/// <usecases>
///   - [Entity]: [Actor] => [Action] => [Goal]
/// </usecases>
/// <dependencies>
///   [Non-trivial deps - USES API: ..., READS: ..., WRITES: ...]
/// </dependencies>
/// <rationale>
///   - Q: [Why was it implemented this way?]
///     A: [Justification, environmental constraints.]
/// </rationale>
/// <keywords>[Comma-separated keywords for grep search]</keywords>
/// </contract>

using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
namespace Example.Api;



/// <summary>
/// Saves configuration to JSON file
/// </summary>
/// <purpose>Saving parameters to file</purpose>
public bool SaveConfig(Dictionary<string, object> config, string configPath = "config.json")
{ ... }


/// <summary>
/// Request payload for creating an item.
/// </summary>
/// <purpose>[Goal of the record and why.]</purpose>
public record CreateItemRequest(string Name, int Value);

#region CLASS_ExampleController
/// <summary>
/// Class brief.
/// </summary>
/// <purpose>[Goal of the controller and why — what it enables the user/agent to do.]</purpose>
[ApiController]
[Route("api/[controller]")]
public class ExampleController(ILogger<ExampleController> logger) : ControllerBase
{
    private void PrivateMethodMarkupNotNeededForTrivialMethods()
    {
        // no-op
    }

    #region METHOD_ExampleMethodAsync
    /// <summary>
    /// Optional brief.
    /// </summary>
    /// <purpose>[Goal of the method, why]</purpose>
    /// <requires>[Optional preconditions]</requires>
    /// <ensures>[Optional postconditions]</ensures>
    /// <rationale>[Optional rationale]</rationale>
    /// <param name="param1">Optional purpose/semantic meaning of input if non-trivial.</param>
    /// <returns>Optional purpose/semantic meaning of output if non-trivial.</returns>
    [HttpGet("{param1}")]
    public async Task<ActionResult<string>> ExampleMethodAsync(
        int param1,
        CancellationToken cancellationToken)
    {
        #region BLOCK_calculate_regression Non-trivial big block summary
        // ... skip 10 lines
        logger.LogDebug("Pre calculation {Event} {Param1}", "start", param1);
        // ... skip 10 lines
        var result = (param1 * 2).ToString();
        #endregion BLOCK_calculate_regression

        logger.LogDebug("Business result {Result}", result);
        return result;
    }
    #endregion METHOD_ExampleMethodAsync
}
#endregion CLASS_ExampleController

void PrivateFunctionMarkupNotNeededForTrivialFunctions()
{
    // no-op — top-level statement only valid in Program.cs
}

#region FUNC_ExampleFunction
/// <summary>
/// Optional brief.
/// </summary>
/// <purpose>[Describe the GOAL of this function and why.]</purpose>
/// <param name="data">Optional purpose/semantic meaning of input if non-trivial.</param>
/// <returns>Optional purpose/semantic meaning of output if non-trivial.</returns>
static int ExampleFunction(int[] data)
{
    logger?.LogDebug("INIT {DataLength}", data.Length);

    #region BLOCK_loop
    var total = 0;
    foreach (var item in data)
    {
        total += item;
        logger?.LogDebug("Loop step {Item} {RunningTotal}", item, total);
    }
    #endregion BLOCK_loop

    logger?.LogDebug("RESULT {SumComputed}", total);
    return total;
}
#endregion FUNC_ExampleFunction
