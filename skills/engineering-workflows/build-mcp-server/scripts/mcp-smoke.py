#!/usr/bin/env python3
"""Smoke-test a stdio MCP server with no dependencies.

Usage:
  mcp-smoke.py [--list] [--call TOOL JSON_ARGS] [--protocol auto|2026|legacy]
              [--timeout SEC] -- SERVER_COMMAND...
  (all options go BEFORE --; everything after -- is the server command)

Examples:
  mcp-smoke.py --list -- node dist/index.js
  mcp-smoke.py --call acme_search_tickets '{"query":"refund","limit":3}' -- python3 server.py

Protocol (default auto): first probes `server/discover` for the stateless 2026-07-28
revision (no handshake; protocol version and client capabilities ride in each
request's _meta). If the server does not support it, falls back to the legacy
initialize -> notifications/initialized handshake (2025-11-25 and earlier).
Then tools/list (always) -> tools/call (if --call). Prints a summary; exit 0 on success, 1 on protocol or tool error,
2 on usage error. Server stderr is passed through so you can see its logs.
"""
import json
import subprocess
import sys
import threading
import queue

STATELESS_VERSION = "2026-07-28"   # no initialize; per-request _meta
LEGACY_VERSION = "2025-11-25"      # last revision with the initialize handshake
CLIENT_INFO = {"name": "mcp-smoke", "version": "2.0"}


def usage(msg=None):
    if msg:
        print(f"error: {msg}", file=sys.stderr)
    print(__doc__, file=sys.stderr)
    sys.exit(2)


def parse(argv):
    if argv[:1] in (["-h"], ["--help"]):
        usage()
    if "--" not in argv:
        usage("missing -- before the server command")
    i = argv.index("--")
    opts, cmd = argv[:i], argv[i + 1:]
    if not cmd:
        usage("no server command")
    call, timeout, proto, j = None, 20.0, "auto", 0
    while j < len(opts):
        o = opts[j]
        if o == "--list":
            j += 1
        elif o == "--call":
            try:
                call = (opts[j + 1], json.loads(opts[j + 2]))
            except (IndexError, json.JSONDecodeError) as e:
                usage(f"--call needs TOOL and a JSON object ({e})")
            j += 3
        elif o == "--protocol":
            proto = opts[j + 1] if j + 1 < len(opts) else ""
            if proto not in ("auto", "2026", "legacy"):
                usage("--protocol must be auto, 2026 or legacy")
            j += 2
        elif o == "--timeout":
            timeout = float(opts[j + 1])
            j += 2
        elif o in ("-h", "--help"):
            usage()
        else:
            usage(f"unknown option {o}")
    return cmd, call, timeout, proto


class Client:
    def __init__(self, cmd, timeout):
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=None, text=True, bufsize=1)
        self.timeout = timeout
        self.q = queue.Queue()
        self.next_id = 1
        self.meta = None  # set for the stateless revision
        threading.Thread(target=self._reader, daemon=True).start()

    def _reader(self):
        for line in self.p.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                self.q.put(json.loads(line))
            except json.JSONDecodeError:
                self.q.put({"_bad": line})
        self.q.put(None)

    def send(self, method, params=None, notify=False):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None or (self.meta and not notify):
            msg["params"] = dict(params or {})
            if self.meta and not notify:
                msg["params"]["_meta"] = self.meta
        if not notify:
            msg["id"] = self.next_id
            self.next_id += 1
        self.p.stdin.write(json.dumps(msg) + "\n")
        self.p.stdin.flush()
        if notify:
            return None
        while True:
            try:
                m = self.q.get(timeout=self.timeout)
            except queue.Empty:
                raise RuntimeError(f"timeout waiting for {method}")
            if m is None:
                raise RuntimeError(f"server exited (code {self.p.poll()}) during {method}")
            if "_bad" in m:
                raise RuntimeError(f"non-JSON on stdout (log to stderr instead): {m['_bad'][:120]}")
            if m.get("id") == msg["id"]:
                if "error" in m:
                    raise RuntimeError(f"{method} error: {m['error']}")
                return m.get("result", {})
            # ignore notifications and server->client requests

    def close(self):
        try:
            self.p.stdin.close()
            self.p.wait(timeout=5)
        except Exception:
            self.p.kill()


def main():
    cmd, call, timeout, proto = parse(sys.argv[1:])
    c = Client(cmd, timeout)
    try:
        stateless = False
        if proto in ("auto", "2026"):
            meta = {"io.modelcontextprotocol/protocolVersion": STATELESS_VERSION,
                    "io.modelcontextprotocol/clientCapabilities": {},
                    "io.modelcontextprotocol/clientInfo": CLIENT_INFO}
            c.meta = meta
            try:
                disc = c.send("server/discover", {})
                if STATELESS_VERSION in disc.get("supportedVersions", []):
                    stateless = True
                    info = (disc.get("_meta") or {}).get("io.modelcontextprotocol/serverInfo") or {}
                    print(f"server/discover ok: {info.get('name', '?')} {info.get('version', '')} "
                          f"(protocol {STATELESS_VERSION}, stateless)")
            except RuntimeError as e:
                if proto == "2026" or "exited" in str(e) or "non-JSON" in str(e):
                    raise
            if not stateless:
                c.meta = None
                if proto == "2026":
                    raise RuntimeError(f"server does not support {STATELESS_VERSION}")
        if not stateless:
            init = c.send("initialize", {"protocolVersion": LEGACY_VERSION, "capabilities": {},
                                         "clientInfo": CLIENT_INFO})
            info = init.get("serverInfo", {})
            print(f"initialize ok: {info.get('name', '?')} {info.get('version', '')} "
                  f"(protocol {init.get('protocolVersion', '?')}, legacy handshake)")
            c.send("notifications/initialized", notify=True)
        tools = c.send("tools/list", {}).get("tools", [])
        print(f"tools/list ok: {len(tools)} tools")
        problems = 0
        for t in tools:
            desc = (t.get("description") or "").strip().splitlines()
            ann = t.get("annotations") or {}
            flags = ",".join(k.replace("Hint", "") for k, v in ann.items() if v) or "-"
            print(f"  {t['name']:<32} [{flags}] {desc[0][:70] if desc else '(no description!)'}")
            if not desc:
                problems += 1
        if call:
            name, args = call
            if name not in {t["name"] for t in tools}:
                print(f"FAIL: tool {name!r} not in tools/list", file=sys.stderr)
                return 1
            res = c.send("tools/call", {"name": name, "arguments": args})
            text = " ".join(x.get("text", "") for x in res.get("content", []) if x.get("type") == "text")
            status = "ERROR" if res.get("isError") else "ok"
            print(f"tools/call {name}: {status}\n{text[:2000]}")
            if res.get("isError"):
                return 1
        if problems:
            print(f"warning: {problems} tool(s) without a description", file=sys.stderr)
        return 0
    except RuntimeError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1
    finally:
        c.close()


if __name__ == "__main__":
    sys.exit(main())
