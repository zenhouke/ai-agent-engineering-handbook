## Required design artifact

Principal/action/object model, default deny, trusted attributes/relations and policy version.

The reference implements application sessions and pending draft preparation, not OIDC, cookies or credential issuance. Local RBAC+ABAC does not deploy OPA/Cedar/OpenFGA. Membership changes increment one global policy epoch, conservatively invalidating approvals; production can version facts more narrowly.

Consumption prepares a pending local operation, not a remote write. Workers recheck current revocation/policy before fresh effects and query existing UNKNOWN outcomes. Session expiry does not erase tasks or issued effects.

References: [Cedar Authorization](https://docs.cedarpolicy.com/auth/authorization.html), [OpenFGA Authorization Concepts](https://openfga.dev/docs/authorization-concepts).
