# 4.5 Glossary

> Condensed English reading notes. The Chinese edition contains the full worked lesson.

## Keep nearby terms separate

A parameter is a value learned during training. A hyperparameter controls training or model configuration. Inference uses existing parameters; context is the input assembled for a particular request.

A token is a tokenizer unit. An embedding is a numeric representation. Attention computes context-dependent weighted combinations. A KV cache stores intermediate keys and values during inference; it is not persistent personal memory.

Retrieval returns candidate evidence. RAG includes that evidence in generation. A tool is an executable capability. An agent uses observations to choose actions. Runtime enforces execution rules.

A checkpoint persists task progress. Idempotency means repeating an operation under the defined key has the specified same effect. A timeout may leave the external outcome unknown. An approval authorizes a particular action under a policy; it is not a permanent blanket permission.

## Agent engineering terms

| Term | Meaning | Boundary |
|---|---|---|
| Function Calling | A model proposes a tool name and structured arguments; the application validates and executes | It is distinct from MCP and does not mean execution has occurred |
| MCP | A protocol for connecting model applications to tools, resources and prompts | Connection does not grant business authorization |
| Skills | Progressively loaded packages of methods, instructions and resources | They grant no authority and do not replace current plans or state |
| Authentication / AuthN | Establishing who the current principal is | Identity alone does not permit an action |
| Authorization / AuthZ | Deciding whether the current principal may act on an object | Previous approval does not establish current permission |
| Session | An interaction association with a defined scope and lifecycle | Application sessions, model threads and external-account sessions are separate |
| Run | One execution instance of a business task | It is distinct from both the task and a login session |
| operation_id | A stable identifier correlating an operation, fixed payload and receipt | Keep it on retry; services must implement its deduplication semantics |
| CAS | Update only when the current value matches the expected value | A version check alone does not enforce lease expiry |
| Fencing token | A monotonically increasing ownership generation checked by the resource | Giving a worker a lock or number without resource-side enforcement is insufficient |
| Outbox | An event saved in the business transaction and published asynchronously | Delivery can repeat; consumers and external effects still need idempotency |
| Evaluation | Checking quality and rules with defined tasks, criteria and comparisons | Aggregate success must not hide unauthorized actions or synthetic examples |
| Monitoring | Observing live states, latency, errors and queues to trigger action | Logs alone do not establish evaluated quality |
| A2A | A protocol for exchanging tasks and artifacts across Agent systems | It is not a queue or a prerequisite for multi-Agent design |

## Check your understanding

How do context, checkpoint and long-term memory differ?

<details><summary>Suggested answer</summary>

They serve the current model call, recoverable task progress and reusable cross-task facts respectively. Their storage, authority and lifecycle should be explicit.

</details>
