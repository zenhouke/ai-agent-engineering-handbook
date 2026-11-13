# 2.6.4 Tool binding, MCP and permission intersections

> Visual route · Established approaches · Reference code

Based on Agent Skills format; version pins, bundle digests and tool bindings are example Host conventions, not execution authority.

## Start with the problem

Does a Skill instructing “read everything and order” grant those abilities? Does MCP discovery grant object access?

![Failure path versus controlled path](../../assets/lessons/en/skill04-problem.svg)

## See the mechanism

Trusted task policy, deployed capabilities and reviewed bindings constrain actions; services authorize objects again. Skills supply method, Function Calling expresses proposals and MCP carries capability calls.

![How data, computation or state changes](../../assets/lessons/en/skill04-mechanism.svg)

## Choose an established approach

![Choose by the problem condition](../../assets/lessons/en/skill04-selection.svg)

| Approach | Mechanism | Use when | Tradeoff / boundary |
|---|---|---|---|
| Direct SDK adapter | Use registered application functions | Small stable internal tools | Object authorization still required |
| MCP adapter | Client invokes server contracts | Independent tools and multiple Hosts | Protocol success is not task acceptance |
| Binding gateway | Intersect task policy with reviewed bindings | Multiple Skills/tenants and write actions | Declarations are not authority |

## Inside the mainstream approaches

### 1 · Direct SDK adapter

![Direct SDK adapter](../../assets/lessons/en/skill04-solution-1.svg)

**Concrete trace:** Direct SDK can read evidence while the Skill supplies review method.

### 2 · MCP adapter

![MCP adapter](../../assets/lessons/en/skill04-solution-2.svg)

**Concrete trace:** Real SDK tests read A and reject B.

### 3 · Binding gateway

![Binding gateway](../../assets/lessons/en/skill04-solution-3.svg)

**Concrete trace:** Activating a method cannot create an order or read another customer.

## Reference code

Expand the implementation corresponding to this mechanism. Training code is provided but not executed. See the reference-code guide for dependencies and verification limits.

[Reference code and verification limits](../../docs/zh/projects/03-code-guide.md)

<details><summary>Expand code and limits</summary>

```python
"""Skill method + trusted Host policy + an actual in-memory MCP call; no LLM."""

from .mcp_host_bridge import call_authorized, check_quote_access
from .mcp_server_example import build_server
from .skill_host import build_host


async def review_quote(quote_id: str) -> dict:
    from mcp import Client

    service, session = build_host()
    service.activate("quote-review", session)
    check_quote_access(
        "read_quote",
        {"quote_id": quote_id},
        session.policy.allowed_tools,
        session.policy.quote_ids,
    )
    async with Client(build_server()) as client:

        async def adapter(tool, arguments, policy):
            return await call_authorized(
                client, tool, arguments, policy.allowed_tools, policy.quote_ids
            )

        return await service.invoke(
            "quote-review", "read_quote", {"quote_id": quote_id}, session, adapter
        )


# The skill explains how to review a quote. It does not grant access to B or create orders.
```

</details>

## The Host connects method to execution

Trusted deployment bindings intersect task permissions and currently deployed tools. This example binds only read_quote; neither model nor Skill text can add create_order. An adapter can map the semantic binding to MCP or a direct SDK without claiming a universal binding field.

Host checks tool/arguments/resource scope; the MCP service checks object access again. Activation prepares context and never automatically runs scripts or tools.

The real in-memory SDK returns A at 180 cents with unknown shipping and rejects B. Discovery, valid schema and authentication do not substitute for object authorization. Writes additionally require approval, stable operation IDs and reconciliation.

These tests make no model request, purchase or training run. They check specified contracts, not arbitrary third-party Skill safety; digests detect changes rather than establish trust.


References: [Official 1](https://agentskills.io/client-implementation/adding-skills-support), [Official 2](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)。


## Change a condition

Can allowed-tools in a Skill override a Host ban on create_order?

<details><summary>Suggested answer</summary>

No. Trusted Policy and registry bindings govern this example; declarations cannot bypass task or server authorization.

</details>

[Official sources and approach rationale](../../docs/zh/resources.md)
