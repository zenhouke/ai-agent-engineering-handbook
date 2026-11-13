# 3.5.2 Policy enforcement, caching and delegation

> Visual route · Established approaches · Reference code

Local reference: trusted identity injection and SQLite transactions, without a login server or remote writes.

## Start with the problem

Can a service trust one allow forever? Should child workers inherit all parent credentials?

![Failure path versus controlled path](../../assets/diagrams/architecture/permissions/auth02/en/problem.png)



## See the mechanism

Enforce current facts at execution. Cache by principal/action/object plus policy/fact versions. Delegation narrows scope; approval cannot convert deny into allow.

![How data, computation or state changes](../../assets/diagrams/architecture/permissions/auth02/en/mechanism.png)

## Choose an established approach

![Choose by the problem condition](../../assets/diagrams/architecture/permissions/auth02/en/selection.png)

| Approach | Mechanism | Use when | Tradeoff / boundary |
|---|---|---|---|
| In-process policy service | Evaluate local role/attribute rules | Small stable rule sets | Distributed rules become hard to audit |
| External policy engine | PDP decides; application PEP enforces | Cross-service policy governance | Network/cache/consistency/failure choices |
| Scoped task delegation | Require child scope subset | Multi-agent/background workers | Audience, expiry, revocation and audit |

## Inside the mainstream approaches

### 1 · In-process policy service

![In-process policy service](../../assets/diagrams/architecture/permissions/auth02/en/solution-1.png)

**Concrete trace:** Role downgrade blocks a new run in an existing session.

<details><summary>Expand steps, state and failure boundaries</summary>

1. Centralize checks
2. Inject trusted context
3. Load current object
4. Record reason

**State** Identity, objects and policy version.

**Failure / recovery** Reuse service rules from handlers and workers.

**Verification** Consistent denial across entrypoints.

</details>

### 2 · External policy engine

![External policy engine](../../assets/diagrams/architecture/permissions/auth02/en/solution-2.png)

**Concrete trace:** Do not cache allow by user ID alone.

<details><summary>Expand steps, state and failure boundaries</summary>

1. Construct trusted input
2. Evaluate policy
3. Handle unavailable decisions
4. Check freshness

**State** Principal/action/resource/context, version and reason.

**Failure / recovery** Cedar/OPA policy evaluation differs from OpenFGA relation queries.

**Verification** Invalidation, unavailable engine and changed object tests.

</details>

### 3 · Scoped task delegation

![Scoped task delegation](../../assets/diagrams/architecture/permissions/auth02/en/solution-3.png)

**Concrete trace:** A quote-a reader cannot request quote-b or draft creation.

<details><summary>Expand steps, state and failure boundaries</summary>

1. Define parent scope
2. Request minimal child
3. Reject amplification
4. Authorize again server-side

**State** Task/run, actions/resources, expiry and policy version.

**Failure / recovery** A Python set is not a signed capability system.

**Verification** Out-of-scope delegation and revoked authority fail.

</details>

## Reference code

Expand the implementation corresponding to this mechanism. Training code is provided but not executed. See the reference-code guide for dependencies and verification limits.

[Reference code and verification limits](code-guide.md)

<details><summary>Expand code and limits</summary>

```python
"""Evaluate current facts, not a model-supplied role or cached allow flag."""

from .governance.domain import Action, Principal
from .governance.policies import PolicyService
from .governance.repos import GovernanceRepository
from .governance.sessions import SessionService


def decide_action(
    connection, actor: Principal, session_id: str, action: Action, now: int
):
    repository = GovernanceRepository(connection)
    with repository.transaction():
        context = SessionService(repository).context(actor, session_id, now)
        return PolicyService(repository).decide(context, action)


# allowed=true only answers the current policy check. needs_approval remains a separate gate.
```

</details>

## Required design artifact

PEP/PDP placement, invalidation keys, unavailable decisions, delegation and audit correlation.

The reference implements application sessions and pending draft preparation, not OIDC, cookies or credential issuance. Local RBAC+ABAC does not deploy OPA/Cedar/OpenFGA. Membership changes increment one global policy epoch, conservatively invalidating approvals; production can version facts more narrowly.

Consumption prepares a pending local operation, not a remote write. Workers recheck current revocation/policy before fresh effects and query existing UNKNOWN outcomes. Session expiry does not erase tasks or issued effects.

References: [OPA Policy Language](https://www.openpolicyagent.org/docs/policy-language), [OpenFGA Authorization Concepts](https://openfga.dev/docs/authorization-concepts).


## Change a condition

Can human approval override a policy deny?

<details><summary>Suggested answer</summary>

No. Approval supplements permission; it cannot bypass hard resource/tenant/amount constraints.

</details>

[Official sources and approach rationale](resources.md)
