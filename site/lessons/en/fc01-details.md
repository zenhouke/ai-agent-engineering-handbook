## One custom client-tool round

An ordinary function call enters program execution. Model Function Calling in this example produces a proposal; the actual function runs only when the Host dispatches it.

Expose schemas, receive text/refusal or zero/multiple proposals, validate each permitted proposal, then return actual results under the original call_id for the next turn. Never execute a default tool when no proposal exists or fabricate successful receipts.

The example uses Responses function_call/function_call_output shapes. Chat Completions and other providers have different tool messages. This narrow read_quote adapter is not universal schema conversion, complete streaming aggregation, concurrent scheduling or a paid model integration.

Strict structure does not establish object access, supported facts or completed business effects. Complete and validate streamed arguments before execution; partial JSON must not trigger writes.


References: [Official 1](https://developers.openai.com/api/docs/guides/function-calling), [Official 2](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)。
