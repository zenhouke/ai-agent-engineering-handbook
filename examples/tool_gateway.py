"""Protocol transport is separate from business authorization."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class ToolRequest:
    name: str
    document_id: str


def read_tool(
    request: ToolRequest,
    authorized_documents: set[str],
    readers: dict[str, Callable[[str], str]],
) -> str:
    if request.name not in readers:
        raise PermissionError("Tool is not available")
    if request.document_id not in authorized_documents:
        raise PermissionError("Document is not authorized")
    return readers[request.name](request.document_id)


# An MCP adapter can translate calls into ToolRequest, but cannot skip this check.
