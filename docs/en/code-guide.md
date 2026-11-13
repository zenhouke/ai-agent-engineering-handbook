# 4.3 Reference code and verification limits

Training code is supplied for reading; actually training a model is not required. Expand each lesson’s reference implementation and compare it with the diagram.

| Stage | Implementations | Inspect |
|---|---|---|
| 1 Model foundations | Task contracts, autograd, classification pipeline, MLP, CNN, bigram, decoder block, LoRA | Shapes, data boundaries, masks and frozen weights |
| 2 Applications and Agent principles | Output checks, RRF, KV estimate, ReAct, planning/reflection, context budgets, compaction, Function Calling, MCP, Skills, checkpoints and scoped memory | Structure versus truth, proposal versus execution, methods versus state |
| 3 Architecture design | Ownership/messages, state conflicts, sessions, delegation, approval, scheduling, recovery, evaluation/operations and deployment | Decision authority, state ownership and recovery |
| 4 Integrated practice | Studio commercial/run/delivery gates and four offline labs | Business conditions, transaction boundaries and evidence |

## Dependencies

Autograd, MLP, CNN, decoder and LoRA references use PyTorch. The classification pipeline uses scikit-learn. Training functions are not called by documentation builds or tests. Optional dependency ranges are declarations, not a tested matrix across every version and device; lock compatible versions when using them.

Other mechanism examples mainly use the Python standard library. Model and tool functions are injected, so deterministic test doubles can check control flow without real inference or external side effects.

A complete optional classifier reference also covers separate train/validation CSVs, train-only normalization, a 2→2→1 MLP, batch updates, evaluation mode and saving the best weights with preprocessing parameters. It is supplied as code only, without training results or quality claims.

## What was checked

Syntax/static checks establish that source is parseable, not that tensor libraries work on every machine. Non-training mechanism tests establish selected properties of budgets, authorization, transitions and ranking. They do not establish trained model quality, external tool performance or production reliability.

Scores, matrices and traces are teaching examples. A LoRA layer, one decoder block or a bounded loop is not a complete training platform or production agent.

## MCP and workflow references

MCP is pinned to protocol **2026-07-28** and official Python SDK **2.3.0**. Optional framework pins are LangGraph 1.2.21 and Temporal Python 1.36.0.

```sh
python3 -m pip install -r requirements-mcp.txt -r examples/requirements-architecture.txt
python3 -m unittest discover -s tests -p 'test_mcp_sdk.py' -v
python3 -m unittest discover -s tests -p 'test_workflow_frameworks.py' -v
python3 -m unittest discover -s tests -p 'test_outbox_recovery.py' -v
```

Real in-memory and stdio MCP checks cover discovery, tools/resources/prompts and scope rejection. LangGraph checks cover approval interrupt/resume with InMemorySaver, not durable cross-process recovery. Temporal checks import SDK definitions and invoke the Activity adapter directly; no server/Worker or replay/retry test runs. SQLite tests cover transactional rollback, lost-success reconciliation and redelivery against a deduplicating fake backend, without a live broker or purchasing service. None of these checks trains a model.

## Skills and Function Calling

The actual package follows Agent Skills metadata/body/resource structure. The local format validator checks a subset of constraints, including required fields; it is not a complete specification validator. Host digests, versions and bindings are local application conventions. Optional PyYAML 6.0.3 supports loading; MCP integration uses SDK 2.3.0. Tests cover disclosure, deduplication, scope, paths, changed bundles, artifacts and provider call correlation. Proposals are fixed inputs, not model generations; no uplift results, training, OS sandbox or durable skill runtime are claimed.

## Governance and multi-Agent design

New standard-library examples separate sessions/tasks/runs, current policy and exact-action approvals. SQLite tests cover concurrent consumption and transaction rollback. Additional contracts cover work ownership, envelopes, evidence conflicts, bounded DAG execution, recovery proposals, paired task metrics and capacity estimates. No login service, broker, policy engine, remote effect or model experiment is deployed. Numbered headings/navigation/outline share one manifest, and the retired Skills overview redirects to composition/planning.

## Personal studio contracts

The studio checks cover independent run/commercial approval, trusted funds, changed terms/customer, expiry/current authority and exact settled delivery. Pure contracts do not authenticate, consume approvals or perform external actions; governance and outbox examples cover those separate mechanisms. Run `python3 -m unittest discover -s tests -p 'test_studio_contracts.py' -v`.
