## Three recovery mechanisms for the same crash

**Scenario:** Research is complete, approval arrives tomorrow, and a remote draft is created but its success response is lost. Recovery must resume without creating another draft.

| Dimension | LangGraph + persistent Checkpointer | Temporal Workflow + Activity | Database + Outbox + queue |
|---|---|---|---|
| Persisted data | Graph state, checkpoints and pending work | Workflow event history and Activity results/retries | Custom tasks, approval, operations, Outbox and leases |
| Recovery | Load the checkpoint for the same thread_id | Deterministically replay history, then schedule unfinished work | Read pending records and claim with version checks |
| Repeated work | Unfinished nodes; interrupted nodes re-enter | Workflow replay and potentially retried Activities | Unacknowledged messages and worker operations |
| Approval | Trusted application resumes an interrupt | Trusted application sends signal/update; wait state persists | Transactional approval state and pending event |
| External deduplication | Business adapter and remote system | Business adapter and remote system | Business adapter and remote system |
| Ownership | Depends on chosen storage/deployment; thread_id is not a lock | Service schedules tasks; external effects still need deduplication | Implement CAS, leases and fencing; expiry does not stop an old worker |
| Best fit | Graph-based Agents and human interrupts | Long waits and reliable Activity scheduling | Existing database/queue infrastructure with custom state-machine ownership |

### Remote success before local receipt persistence

1. Persist `operation_id=op-42` and the payload fingerprint before sending.
2. The remote service creates `draft-42`, but the response is lost. Local state is **UNKNOWN**, not proof of failure.
3. Query by `op-42` and store the receipt. A deduplicating service can also return the same result for the **same key and payload**.
4. Without remote deduplication or query support, require manual reconciliation. Retrying with a new key may create a second draft.

A request ID correlates one RPC reply; an operation ID identifies a business effect across restarts. Recoverable orchestration cannot invent exactly-once guarantees for a remote system.

### LangGraph interrupts need a separate effect node

Resuming an interrupt re-enters its node; code preceding the interrupt can run again. Keep approval validation in that node and place draft creation in a separate, idempotent node. InMemorySaver demonstrates semantics only; cross-process recovery requires a durable checkpointer, state migrations and an explicit concurrency policy.

### Temporal separates Workflow from Activity

Workflow history restores conditions, timers and recorded Activity results, so Workflow code must replay deterministically. Put network requests and database writes in Activities. start_to_close_timeout bounds one attempt; schedule_to_close_timeout bounds the complete scheduling/retry window. Permission failures are not transient network errors. Long Activities additionally need heartbeat/cancellation design; the short reference below does not implement them.

References: [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts), [Temporal Python retries](https://docs.temporal.io/develop/python/best-practices/error-handling).
