"""Wire envelope examples, not a replacement for the official transport/SDK."""

PROTOCOL_VERSION = "2026-07-28"


def request(request_id: int, method: str, params: dict | None = None) -> dict:
    payload = dict(params or {})
    payload["_meta"] = {
        "io.modelcontextprotocol/protocolVersion": PROTOCOL_VERSION,
        "io.modelcontextprotocol/clientInfo": {
            "name": "teaching-client",
            "version": "1",
        },
    }
    return {"jsonrpc": "2.0", "id": request_id, "method": method, "params": payload}


def classify_response(message: dict) -> str:
    if "error" in message:
        return "protocol_error"
    result = message.get("result", {})
    if result.get("isError", False):
        return "tool_execution_error"
    if result.get("resultType") == "input_required":
        return "needs_follow_up"
    return "result_requires_business_validation"


# Request IDs correlate replies; they are not durable idempotency keys.
# 2025-11-25 and earlier used initialize + notifications/initialized instead.
