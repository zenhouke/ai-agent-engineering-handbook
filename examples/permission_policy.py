"""Current policy evaluation and non-amplifying worker delegation."""

from .governance.policies import PolicyService


def narrow_worker(
    parent: frozenset[tuple[str, str]], requested: frozenset[tuple[str, str]]
):
    return PolicyService.delegated_scope(parent, requested)


# Evaluate subject + action + resource + trusted context; retain the policy version/reason.
# This is a small local reference; it does not install or benchmark OPA/Cedar/OpenFGA.
