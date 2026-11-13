"""Optional real official-SDK protocol checks; no model or network is needed."""

import importlib.util
import unittest

from examples.mcp_messages import PROTOCOL_VERSION, classify_response, request


class WireContractTests(unittest.TestCase):
    def test_version_metadata_and_correlation(self):
        message = request(
            7, "tools/call", {"name": "read_quote", "arguments": {"quote_id": "A"}}
        )
        self.assertEqual(
            PROTOCOL_VERSION,
            message["params"]["_meta"]["io.modelcontextprotocol/protocolVersion"],
        )
        self.assertEqual(7, message["id"])
        self.assertNotIn("operation_id", message["params"])

    def test_error_layers_are_not_success(self):
        self.assertEqual(
            "protocol_error", classify_response({"error": {"code": -32602}})
        )
        self.assertEqual(
            "tool_execution_error", classify_response({"result": {"isError": True}})
        )
        self.assertEqual(
            "result_requires_business_validation", classify_response({"result": {}})
        )


@unittest.skipUnless(
    importlib.util.find_spec("mcp"), "Optional mcp==2.3.0 dependency not installed"
)
class RealSDKTests(unittest.IsolatedAsyncioTestCase):
    async def test_stdio_transport_discovers_real_child_server(self):
        from examples.mcp_transports import list_local_tools

        self.assertIn("read_quote", await list_local_tools())

    async def test_discovery_exposes_typed_contract(self):
        from examples.mcp_overview import discover_capabilities

        result = await discover_capabilities()
        self.assertEqual(PROTOCOL_VERSION, result["protocol"])
        tool = next(t for t in result["tools"] if t["name"] == "read_quote")
        self.assertIn("quote_id", tool["input_schema"]["required"])

    async def test_three_primitives_have_distinct_results(self):
        from examples.mcp_primitives import inspect_primitives

        result = await inspect_primitives()
        self.assertEqual(180, result["quotation"]["unit_cents"])
        self.assertIsNone(result["quotation"]["shipping_cents"])
        self.assertIn("shipping unknown", result["context"][0])
        self.assertIn("Do not place an order", result["template"][0])

    async def test_server_rejects_scope_despite_valid_arguments(self):
        from mcp import Client

        from examples.mcp_server_example import build_server

        async with Client(build_server()) as client:
            result = await client.call_tool("read_quote", {"quote_id": "B"})
            self.assertTrue(result.is_error)
            self.assertIsNone(result.structured_content)
            self.assertNotIn("170", str(result.content))

    async def test_host_and_server_each_enforce_scope(self):
        from mcp import Client

        from examples.mcp_host_bridge import call_authorized
        from examples.mcp_server_example import build_server

        async with Client(build_server()) as client:
            with self.assertRaises(PermissionError):
                await call_authorized(
                    client,
                    "read_quote",
                    {"quote_id": "B"},
                    frozenset({"read_quote"}),
                    frozenset({"A"}),
                )
            result = await call_authorized(
                client,
                "read_quote",
                {"quote_id": "A"},
                frozenset({"read_quote"}),
                frozenset({"A"}),
            )
            self.assertEqual("A", result["quote_id"])
