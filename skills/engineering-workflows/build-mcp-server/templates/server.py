"""Skeleton MCP server (Python SDK, decorator style, stdio transport).

pip install "mcp>=2" httpx pydantic   (SDK 2.x "MCPServer", spec 2026-07-28; also runs on 1.x "FastMCP")
Run: ACME_API_KEY=... python3 server.py
"""
import json
import os
import sys
from typing import Literal, Optional

import httpx
from mcp.types import ToolAnnotations
from pydantic import Field

try:  # SDK 2.x renamed FastMCP to MCPServer
    from mcp.server.mcpserver import MCPServer as FastMCP
    from mcp.server.mcpserver.exceptions import ToolError
except ImportError:  # SDK 1.x
    from mcp.server.fastmcp import FastMCP
    from mcp.server.fastmcp.exceptions import ToolError

API_URL = os.environ.get("ACME_API_URL", "https://api.acme.example/v2")
API_KEY = os.environ.get("ACME_API_KEY")
CHARACTER_LIMIT = 25_000
if not API_KEY:
    print("ACME_API_KEY is not set", file=sys.stderr)  # never print to stdout in stdio mode
    sys.exit(1)

mcp = FastMCP("acme_tickets_mcp")


# ---------- shared helpers ----------
async def api(path: str, method: str = "GET", **kw):
    async with httpx.AsyncClient(base_url=API_URL, timeout=15,
                                 headers={"Authorization": f"Bearer {API_KEY}"}) as c:
        r = await c.request(method, path, **kw)
        r.raise_for_status()
        return r.json()


def tool_error(e: Exception, hint: str) -> ToolError:
    """Raise the result of this. Only ToolError text reaches the model (isError=true);
    in SDK 2.x any other exception is reported as a bare "Error executing tool"."""
    return ToolError(error_text(e, hint))


def error_text(e: Exception, hint: str) -> str:
    status = e.response.status_code if isinstance(e, httpx.HTTPStatusError) else 0
    if status == 404:
        return f"Not found. {hint}"
    if status in (401, 403):
        return "Not authorised with the configured key; check ACME_API_KEY."
    if status == 429:
        return "Rate limited; wait and retry, or lower `limit`."
    return f"Acme API unavailable ({status or type(e).__name__}). Try again shortly."


def truncate(text: str) -> str:
    if len(text) <= CHARACTER_LIMIT:
        return text
    return text[:CHARACTER_LIMIT] + "\n\n[truncated: narrow the query with filters or a lower limit]"


# ---------- tools ----------
@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False,
                                     idempotentHint=True, openWorldHint=True))
async def acme_search_tickets(
    query: Optional[str] = Field(None, max_length=200, description="Free text, e.g. 'refund'"),
    customer_email: Optional[str] = Field(None, description="e.g. li@corp.test"),
    status: Literal["open", "pending", "closed", "any"] = "any",
    limit: int = Field(20, ge=1, le=100),
    cursor: Optional[str] = Field(None, description="next_cursor from a previous call"),
    response_format: Literal["markdown", "json"] = "markdown",
) -> str:
    """Search support tickets by text, customer email, or status.

    Use to find ticket IDs. Returns id, title, status, customer, updated date. Example: customer_email="li@corp.test", status="open".
    """
    params = {"limit": limit}
    if query:
        params["q"] = query
    if customer_email:
        params["customer"] = customer_email
    if status != "any":
        params["status"] = status
    if cursor:
        params["cursor"] = cursor
    try:
        data = await api("/tickets", params=params)
    except Exception as e:  # map every failure to an actionable message
        raise tool_error(e, "Check filters.") from e
    page = {"items": data["items"], "count": len(data["items"]), "total": data["total"],
            "has_more": bool(data.get("next_cursor")), "next_cursor": data.get("next_cursor")}
    if response_format == "json":
        return truncate(json.dumps(page, indent=2))
    lines = [f"Found {page['total']} tickets (showing {page['count']})", ""]
    lines += [f"- **{t['title']}** ({t['id']}) · {t['status']} · {t['customer_email']} · {t['updated_at'][:10]}"
              for t in page["items"]]
    if page["has_more"]:
        lines.append(f'\nMore available: pass cursor="{page["next_cursor"]}"')
    return truncate("\n".join(lines))


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False,
                                     idempotentHint=False, openWorldHint=True))
async def acme_add_comment(
    ticket_id: str = Field(..., pattern=r"^T-\d+$", description="e.g. T-1043"),
    body: str = Field(..., min_length=1, max_length=5000),
    public: bool = False,
) -> str:
    """Add a comment to a ticket. Internal by default; public=True notifies the customer.

    Returns the new comment id.
    """
    try:
        c = await api(f"/tickets/{ticket_id}/comments", method="POST",
                      json={"body": body, "public": public})
    except Exception as e:
        raise tool_error(e, f"No ticket {ticket_id}. Use acme_search_tickets to find IDs.") from e
    return f"Comment {c['id']} added to {ticket_id}."


if __name__ == "__main__":
    mcp.run()  # stdio by default; use mcp.run(transport="streamable-http") for remote
