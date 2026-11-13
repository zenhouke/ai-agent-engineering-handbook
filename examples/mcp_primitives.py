"""The three server primitives do different work; none needs a model to be tested."""


async def inspect_primitives() -> dict:
    from mcp import Client

    from .mcp_server_example import build_server

    async with Client(build_server()) as client:
        tool = await client.call_tool("read_quote", {"quote_id": "A"})
        resource = await client.read_resource("quote://approved/A")
        prompt = await client.get_prompt("compare_quote", {"quote_id": "A"})
        return {
            "quotation": tool.structured_content,
            "context": [item.text for item in resource.contents],
            "template": [message.content.text for message in prompt.messages],
        }


# tools/call executes a capability; resources/read reads context; prompts/get renders a template.
