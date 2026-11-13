import importlib.util
import json
import unittest

from examples.function_calling import handle_proposal, quotation_tool


def proposal(quote_id="A"):
    return {
        "type": "function_call",
        "name": "read_quote",
        "arguments": json.dumps({"quote_id": quote_id}),
        "call_id": "provider-call-7",
    }


class FunctionCallingTests(unittest.IsolatedAsyncioTestCase):
    async def test_observation_preserves_provider_call_id(self):
        calls = []

        async def execute(name, args):
            calls.append((name, args))
            return {"quote_id": "A", "shipping_cents": None}

        result = await handle_proposal(proposal(), execute)
        self.assertEqual("provider-call-7", result["call_id"])
        self.assertIsNone(json.loads(result["output"])["shipping_cents"])
        self.assertEqual([("read_quote", {"quote_id": "A"})], calls)
        self.assertEqual(False, quotation_tool()["parameters"]["additionalProperties"])

    async def test_invalid_call_cannot_reach_executor(self):
        calls = []

        async def execute(*args):
            calls.append(args)

        bad = proposal()
        bad["arguments"] = '{"quote_id":"A","tenant":"other"}'
        with self.assertRaises(ValueError):
            await handle_proposal(bad, execute)
        bad = proposal()
        bad["name"] = "create_order"
        with self.assertRaises(ValueError):
            await handle_proposal(bad, execute)
        self.assertFalse(calls)


@unittest.skipUnless(importlib.util.find_spec("mcp"), "Optional MCP dependency missing")
class FunctionMCPTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_mcp_under_function_proposal(self):
        from examples.function_calling_mcp import resolve_via_mcp

        result = await resolve_via_mcp(proposal())
        self.assertEqual("provider-call-7", result["call_id"])
        self.assertEqual("A", json.loads(result["output"])["quote_id"])
        with self.assertRaises(PermissionError):
            await resolve_via_mcp(proposal("B"))

    @unittest.skipUnless(
        importlib.util.find_spec("yaml"), "Optional YAML dependency missing"
    )
    async def test_loaded_skill_still_cannot_read_out_of_scope_quote(self):
        from examples.skill_mcp_integration import review_quote

        self.assertEqual("A", (await review_quote("A"))["quote_id"])
        with self.assertRaises(PermissionError):
            await review_quote("B")
