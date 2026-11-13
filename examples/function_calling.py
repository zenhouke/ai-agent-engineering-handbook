"""OpenAI Responses client-function shape, without a model request or credentials.

This adapter deliberately supports only the read_quote contract. It is not a
universal JSON Schema translator. Schema-valid arguments still need authorization.
"""

import json


def quotation_tool() -> dict:
    return {
        "type": "function",
        "name": "read_quote",
        "description": "Read an authorized quote.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {"quote_id": {"type": "string"}},
            "required": ["quote_id"],
            "additionalProperties": False,
        },
    }


def parse_proposal(item: dict) -> tuple[str, dict]:
    if item.get("type") != "function_call" or item.get("name") != "read_quote":
        raise ValueError("Unsupported client-function proposal")
    call_id = item.get("call_id")
    if not isinstance(call_id, str) or not call_id:
        raise ValueError("Missing provider call correlation ID")
    arguments = json.loads(item["arguments"])
    if (
        not isinstance(arguments, dict)
        or set(arguments) != {"quote_id"}
        or not isinstance(arguments["quote_id"], str)
    ):
        raise ValueError("Invalid read_quote arguments")
    return call_id, arguments


async def handle_proposal(item: dict, execute) -> dict:
    call_id, arguments = parse_proposal(item)
    result = await execute(
        "read_quote", arguments
    )  # Host gateway, not arbitrary getattr/exec.
    return {
        "type": "function_call_output",
        "call_id": call_id,
        "output": json.dumps(result, ensure_ascii=False, allow_nan=False),
    }


# Return this tool output alongside required conversation/reasoning items for the next turn.
# This example handles one client function; provider-managed tools may execute server-side.
