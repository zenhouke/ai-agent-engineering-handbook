## Three architecture duties, three kinds of evidence

| Module | Placement | Mechanism and boundary |
|---|---|---|
| Evaluation | Before release and during regression | Fixed tasks, paired comparisons, traces and fault injection; logs do not prove quality |
| Observability | Host, workflow, gateway, services/storage | Correlate task_id/trace_id/operation_id; track latency, tokens, retries, denial, backlog and UNKNOWN |
| Security | Every trust boundary | Allowlisted tools, trusted identity, object authorization, source/instruction separation, approval and idempotency |

Multi-agent design adds worker correlation/budget ownership, Skills add provenance/versioned activation, and MCP adds transport/RPC/service failures. These integrate into architecture-level assurance rather than end-of-report advice. No telemetry backend or production defense deployment is claimed.

### Evaluation: evidence before changing versions

Fix tasks, evidence snapshots and acceptance criteria. Separate normal operation, denial, timeout, redelivery and recovery cases. Compare changed models, Skills, retrieval and collaboration against the same task baseline; average success cannot hide unauthorized actions.

### Observability: locate failures while tasks run

Correlate events/spans around model calls, retrieval, gateways and domain services. Start from the blocked task state and trace the call that caused waiting, retries or UNKNOWN. Track latency, tokens, backlog and denial separately. Trace IDs belong in traces rather than unbounded metric labels; avoid copying sensitive full context into logs.

### Security: enforce boundaries at execution

Hosts constrain tools/arguments and services authorize objects. External documents and Skills retain their actual authority level. Bind writes to approval and stable operation keys; reconcile uncertain outcomes. Delegated workers inherit restricted scope. Integrity hashes do not replace review, isolation or provenance.
