# 4.4 How to use the reference courses

> Condensed English reading notes. The Chinese edition contains the full worked lesson.

## Read each source to answer a specific question

The course organization draws on D2L for a progression from mathematical prerequisites to models, Neural Networks: Zero to Hero for inspecting small numerical computations, LLM Cookbook for required versus optional application topics, and Hello-Agents for the progression toward agent construction.

The explanations, examples and vector diagrams in this repository are independently written. Reference courses have their own prerequisites and licenses. Reading their tables of contents is not a claim to have executed their projects.

For technical mechanisms, consult the original Transformer and LoRA papers and official framework documentation. Record a version before relying on a changing software interface. Avoid collecting frameworks without completing a concrete reading exercise.

## Check your understanding

What is a useful source-reading note?

<details><summary>Suggested answer</summary>

A question, the mechanism that answers it, a counterexample, and an explanation of how the result changes your own design.

</details>

## Established approaches and official documentation

Autograd and classification baselines: [PyTorch](https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html), [scikit-learn](https://scikit-learn.org/stable/supervised_learning.html). Parameter-efficient adaptation: [PEFT LoRA](https://huggingface.co/docs/peft/main/en/conceptual_guides/lora), using main documentation rather than a release guarantee. Persistent state and workflow patterns: [LangGraph](https://docs.langchain.com/oss/python/langgraph/persistence). Interoperable tool discovery and calls: [MCP architecture](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture). Cache internals: [vLLM Paged Attention](https://docs.vllm.ai/en/latest/design/paged_attention/). Durable cross-process execution: [Temporal](https://docs.temporal.io/workflow-execution). These are mechanism references, not dependencies all learners must install.

## Multi-repository evidence for the studio (2026-11-13)

ForgePilot local `13d673c` informs order, funds, approval and runtime boundaries. Compare [LangGraph](https://github.com/langchain-ai/langgraph) for persisted state and resumable interruption, [Temporal](https://github.com/temporalio/sdk-python) for durable deterministic control and activities, [CrewAI](https://github.com/crewAIInc/crewAI) for role collaboration inside controlled flows, and [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) for sequential/concurrent/handoff orchestration. [AutoGen](https://github.com/microsoft/autogen) is archived and used only as historical reference. [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) informs capability integration; [Agent Skills](https://github.com/agentskills/agentskills) informs reusable, progressively loaded methods.

Reviewed READMEs, LangGraph interrupt implementation and Temporal determinism guidance. The studio chapter maps each to a decision and boundary. These are alternatives, not a combined dependency stack or a claim that ForgePilot uses them; all repositories were not installed or deployed.
