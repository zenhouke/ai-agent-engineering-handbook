# 4.5 Glossary

> Condensed English reading notes. The Chinese edition contains the full worked lesson.

## Keep nearby terms separate

A parameter is a value learned during training. A hyperparameter controls training or model configuration. Inference uses existing parameters; context is the input assembled for a particular request.

A token is a tokenizer unit. An embedding is a numeric representation. Attention computes context-dependent weighted combinations. A KV cache stores intermediate keys and values during inference; it is not persistent personal memory.

Retrieval returns candidate evidence. RAG includes that evidence in generation. A tool is an executable capability. An agent uses observations to choose actions. Runtime enforces execution rules.

A checkpoint persists task progress. Idempotency means repeating an operation under the defined key has the specified same effect. A timeout may leave the external outcome unknown. An approval authorizes a particular action under a policy; it is not a permanent blanket permission.

## Check your understanding

How do context, checkpoint and long-term memory differ?

<details><summary>Suggested answer</summary>

They serve the current model call, recoverable task progress and reusable cross-task facts respectively. Their storage, authority and lifecycle should be explicit.

</details>
