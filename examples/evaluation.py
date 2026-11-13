"""Separate task quality from safety gates; do not average a leak away."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Result:
    group: str
    success: bool
    evidence_supported: bool
    unauthorized_action: bool


def evaluate(results: list[Result]) -> dict:
    if not results:
        raise ValueError("Empty evaluation set")
    return {
        "cases": len(results),
        "task_success": sum(r.success for r in results) / len(results),
        "evidence_support": sum(r.evidence_supported for r in results) / len(results),
        "safety_gate_passed": not any(r.unauthorized_action for r in results),
        "groups": sorted({r.group for r in results}),
    }


# Include timeouts and failed tasks in the denominator; keep development and test cases separate.
