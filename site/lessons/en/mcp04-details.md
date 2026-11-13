## Four remote integration boundaries

The stdio host/SDK owns subprocess cleanup; stdout is the message channel and stderr carries logs. Streamable HTTP carries RPC requests and may return JSON or SSE; proxies must handle metadata, authentication and timeouts. It is not the legacy HTTP+SSE endpoint.

For a protected remote service, an OAuth flow can obtain a token intended for that MCP resource. Validate audience, expiry and scopes, then separately authorize tenant/object access. Never trust a model-generated tenant argument or transparently forward upstream credentials.

The sample client starts after token acquisition; it does not implement OAuth or launch a public server. A real deployment must add TLS, Origin checks, authentication and domain policy and validate those independently.
