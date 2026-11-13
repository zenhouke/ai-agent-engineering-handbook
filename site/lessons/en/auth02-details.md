## Required design artifact

PEP/PDP placement, invalidation keys, unavailable decisions, delegation and audit correlation.

The reference implements application sessions and pending draft preparation, not OIDC, cookies or credential issuance. Local RBAC+ABAC does not deploy OPA/Cedar/OpenFGA. Membership changes increment one global policy epoch, conservatively invalidating approvals; production can version facts more narrowly.

Consumption prepares a pending local operation, not a remote write. Workers recheck current revocation/policy before fresh effects and query existing UNKNOWN outcomes. Session expiry does not erase tasks or issued effects.

References: [OPA Policy Language](https://www.openpolicyagent.org/docs/policy-language), [OpenFGA Authorization Concepts](https://openfga.dev/docs/authorization-concepts).
