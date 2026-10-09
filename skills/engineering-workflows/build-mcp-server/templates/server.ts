// src/index.ts: skeleton MCP server (TypeScript SDK v2, spec 2026-07-28, stdio transport).
// npm i @modelcontextprotocol/server zod && npm i -D typescript @types/node && npm pkg set type=module
// (SDK v1 used the single @modelcontextprotocol/sdk package, "/server/mcp.js" imports and a raw
//  object of Zod fields as inputSchema; v2 takes a full schema object, e.g. z.object({...}).)
// tsconfig.json (top-level await needs ES modules):
//   { "compilerOptions": { "target": "ES2022", "module": "Node16", "moduleResolution": "Node16",
//     "rootDir": "src", "outDir": "dist", "strict": true, "skipLibCheck": true, "types": ["node"] } }
// Build: npx tsc   Run: ACME_API_KEY=... node dist/index.js
import { McpServer } from "@modelcontextprotocol/server";
import { serveStdio } from "@modelcontextprotocol/server/stdio";
import * as z from "zod/v4";

const API_URL = process.env.ACME_API_URL ?? "https://api.acme.example/v2";
const API_KEY = process.env.ACME_API_KEY;
const CHARACTER_LIMIT = 25_000;
if (!API_KEY) {
  console.error("ACME_API_KEY is not set");   // stderr only: stdout is the protocol stream
  process.exit(1);
}

// ---------- shared helpers ----------
class ApiError extends Error { constructor(public status: number, msg: string) { super(msg); } }

async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { Authorization: `Bearer ${API_KEY}`, "Content-Type": "application/json", ...init.headers },
    signal: AbortSignal.timeout(15_000),
  });
  if (!res.ok) throw new ApiError(res.status, await res.text());
  return res.json() as Promise<T>;
}

function errorResult(e: unknown, hint: string) {
  const status = e instanceof ApiError ? e.status : 0;
  const text =
    status === 404 ? `Not found. ${hint}` :
    status === 401 || status === 403 ? "Not authorised with the configured key." :
    status === 429 ? "Rate limited; wait and retry, or lower `limit`." :
    `Acme API error${status ? ` (${status})` : ""}. Try again shortly.`;
  return { isError: true, content: [{ type: "text" as const, text }] };
}

function truncate(text: string) {
  return text.length <= CHARACTER_LIMIT ? text
    : text.slice(0, CHARACTER_LIMIT) + "\n\n[truncated: narrow the query with filters or a lower limit]";
}

type Ticket = { id: string; title: string; status: string; customer_email: string; updated_at: string };

// ---------- server ----------
// A factory, so serveStdio can pin one instance per connection and serve both protocol
// eras: 2026-07-28 clients (stateless, server/discover) and older initialize-handshake clients.
function buildServer(): McpServer {
  const server = new McpServer({ name: "acme-tickets-mcp-server", version: "0.1.0" });

  server.registerTool(
    "acme_search_tickets",
    {
      title: "Search tickets",
      description:
        "Search support tickets by text, customer email, or status. Use to find ticket IDs. " +
        "Returns id, title, status, customer, updated date. " +
        'Example: {"customer_email":"li@corp.test","status":"open"}',
      inputSchema: z.object({
        query: z.string().max(200).optional().describe("Free text, e.g. 'refund'"),
        customer_email: z.string().email().optional().describe("e.g. li@corp.test"),
        status: z.enum(["open", "pending", "closed", "any"]).default("any"),
        limit: z.number().int().min(1).max(100).default(20),
        cursor: z.string().optional().describe("next_cursor from a previous call"),
        response_format: z.enum(["markdown", "json"]).default("markdown"),
      }),
      annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: true },
    },
    async ({ query, customer_email, status, limit, cursor, response_format }) => {
      try {
        const qs = new URLSearchParams({ limit: String(limit) });
        if (query) qs.set("q", query);
        if (customer_email) qs.set("customer", customer_email);
        if (status !== "any") qs.set("status", status);
        if (cursor) qs.set("cursor", cursor);
        const data = await api<{ items: Ticket[]; total: number; next_cursor?: string }>(`/tickets?${qs}`);
        const page = { items: data.items, count: data.items.length, total: data.total,
                       has_more: Boolean(data.next_cursor), next_cursor: data.next_cursor ?? null };
        const text = response_format === "json" ? JSON.stringify(page, null, 2)
          : [`Found ${data.total} tickets (showing ${page.count})`, "",
             ...data.items.map(t => `- **${t.title}** (${t.id}) · ${t.status} · ${t.customer_email} · ${t.updated_at.slice(0, 10)}`),
             page.has_more ? `\nMore available: pass cursor="${page.next_cursor}"` : ""].join("\n");
        return { content: [{ type: "text", text: truncate(text) }], structuredContent: page };
      } catch (e) {
        return errorResult(e, "Check filters.");
      }
    },
  );

  server.registerTool(
    "acme_add_comment",
    {
      title: "Add comment",
      description:
        "Add a comment to a ticket. Internal by default; set public=true to notify the customer. " +
        'Returns the comment id. Example: {"ticket_id":"T-1043","body":"Escalated to billing"}',
      inputSchema: z.object({
        ticket_id: z.string().regex(/^T-\d+$/).describe("e.g. T-1043"),
        body: z.string().min(1).max(5000),
        public: z.boolean().default(false),
      }),
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: true },
    },
    async ({ ticket_id, body, public: isPublic }) => {
      try {
        const c = await api<{ id: string }>(`/tickets/${ticket_id}/comments`, {
          method: "POST", body: JSON.stringify({ body, public: isPublic }),
        });
        return { content: [{ type: "text", text: `Comment ${c.id} added to ${ticket_id}.` }] };
      } catch (e) {
        return errorResult(e, `No ticket ${ticket_id}. Use acme_search_tickets to find IDs.`);
      }
    },
  );

  return server;
}

serveStdio(buildServer);
console.error("acme-tickets-mcp-server running on stdio");
