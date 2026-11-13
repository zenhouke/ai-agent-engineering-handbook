## Assign responsibilities in the architecture

| Part | Stores | Responsibility |
|---|---|---|
| Prompt | Current instructions/input | What to do now |
| Skill | Reusable method and resources | How to perform a class of tasks |
| Function Calling | Model tool schemas/proposals | Proposed capability and arguments |
| MCP | Client/Server message contracts | Discover and exchange capabilities |
| Workflow/Runtime | State, edges, budgets, receipts | Which action may run and how to recover |

These parts compose. A review Skill guides a model proposal; the Host authorizes direct SDK or MCP execution; deterministic checks accept the report. Short temporary guidance may use a normal prompt, and fixed arithmetic needs no model-selection round.

The running example has A at 180 cents plus unknown shipping and B at 170+80 cents. Preserve unknowns and compute totals from evidence. The conservative report contract declares no cheapest quote until all totals are known. Loading a Skill does not update model parameters.


References: [Agent Skills Specification](https://agentskills.io/specification), [Agent Skills Host Integration](https://agentskills.io/client-implementation/adding-skills-support)。
