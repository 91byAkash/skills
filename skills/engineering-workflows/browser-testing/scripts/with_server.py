#!/usr/bin/env python3
"""Start one or more servers, wait until their ports accept connections, run a
command, then stop the servers (always, even on failure).

Examples:
  with_server.py --server "npm run dev" --port 5173 -- python3 check.py
  with_server.py --server "cd api && python3 app.py" --port 8000 \
                 --server "cd web && npm run dev" --port 5173 -- npx playwright test
Options:
  --host HOST       host to probe (default: both 127.0.0.1 and ::1, since dev servers
                    bound to "localhost" often listen on IPv6 only)
  --timeout SEC     seconds to wait per port (default 60)
  --log DIR         write each server's output to DIR/server-N.log (default: discard)
  --reuse           if a port already answers before starting, use that server
                    instead of failing (default: fail, so a stale server is never tested)
Exit status is the command's exit status (or 3 if a server never came up).
"""
import argparse
import os
import signal
import socket
import subprocess
import sys
import time


def wait_for_port(hosts, port, timeout, proc):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            return None
        for host in hosts:
            try:
                with socket.create_connection((host, port), timeout=1):
                    return host
            except OSError:
                pass
        time.sleep(0.3)
    return None


def port_open(hosts, port):
    for host in hosts:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except OSError:
            pass
    return False


def stop(proc):
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        proc.wait(timeout=10)
    except (ProcessLookupError, subprocess.TimeoutExpired):
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def main():
    argv = sys.argv[1:]
    if "--" not in argv:
        print(__doc__)
        return 2
    split = argv.index("--")
    opts, command = argv[:split], argv[split + 1:]
    ap = argparse.ArgumentParser(add_help=True, description="see module docstring")
    ap.add_argument("--server", action="append", default=[])
    ap.add_argument("--port", action="append", type=int, default=[])
    ap.add_argument("--host", default=None)
    ap.add_argument("--timeout", type=float, default=60)
    ap.add_argument("--log")
    ap.add_argument("--reuse", action="store_true")
    a = ap.parse_args(opts)
    if not command or len(a.server) != len(a.port) or not a.server:
        print("need at least one --server/--port pair (same count) and a command after --", file=sys.stderr)
        return 2
    if a.log:
        os.makedirs(a.log, exist_ok=True)

    procs = []
    try:
        for i, (cmd, port) in enumerate(zip(a.server, a.port), 1):
            hosts = [a.host] if a.host else ["127.0.0.1", "::1"]
            if port_open(hosts, port):
                if a.reuse:
                    print(f"[with_server] :{port} already answering; reusing it (not starting: {cmd})", file=sys.stderr)
                    continue
                print(f"[with_server] :{port} is already in use by another process; stop it or pass --reuse", file=sys.stderr)
                return 3
            out = open(os.path.join(a.log, f"server-{i}.log"), "w") if a.log else subprocess.DEVNULL
            p = subprocess.Popen(cmd, shell=True, stdout=out, stderr=subprocess.STDOUT,
                                 start_new_session=True)
            procs.append(p)
            print(f"[with_server] started: {cmd} (pid {p.pid}), waiting for :{port}", file=sys.stderr)
            host = wait_for_port(hosts, port, a.timeout, p)
            if host:
                print(f"[with_server] :{port} answering on {host}", file=sys.stderr)
            else:
                why = f"exited with {p.returncode}" if p.poll() is not None else f"no answer after {a.timeout:.0f}s on {', '.join(hosts)}"
                print(f"[with_server] server on :{port} failed: {why}", file=sys.stderr)
                return 3
        print("[with_server] all servers ready; running: " + " ".join(command), file=sys.stderr)
        return subprocess.call(command)
    except KeyboardInterrupt:
        return 130
    finally:
        for p in reversed(procs):
            stop(p)


if __name__ == "__main__":
    sys.exit(main())
