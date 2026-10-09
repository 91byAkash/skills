#!/usr/bin/env python3
"""Build a standalone HTML page (inline SVG, light/dark theme, legend, notes)
from a small JSON spec of nodes on a grid, groups and labelled edges, then
check the layout geometrically. For architecture, data-flow and deployment
views where Mermaid's automatic layout tangles or you need consistent styling.

Usage:
  diagram_html.py spec.json -o diagram.html [--svg diagram.svg] [--png diagram.png] [--check-only] [--json]

Spec (see templates/diagram.json):
{
  "title": "Order platform: checkout path", "caption": "What happens when a customer pays",
  "nodes": [{"id": "web", "label": "Web app", "sub": "Next.js", "type": "service", "row": 0, "col": 1}, ...],
  "groups": [{"label": "VPC (eu-west-1)", "members": ["api", "db"], "kind": "trust"}],
  "edges": [{"from": "web", "to": "api", "label": "HTTPS JSON", "style": "sync|async|data|return",
             "route": "auto|hv|vh", "implied": false}],
  "notes": ["Payments are retried 3x with backoff."]
}
Optional "sources": ["app/db.py:5-7"] on nodes and edges records the evidence
for each claim; it shows as a hover tooltip and is verified by --repo-root.
Node types: actor, service, gateway, store, cache, queue, job, external, client.
Rows/cols are grid cells; widths and gaps are computed so every edge label fits.

Checks (exit 1 on any ERROR):
  ERROR overlap        two nodes share space
  ERROR through-node   an edge segment passes through an unrelated node
  ERROR label-gap      the gap a label sits in is narrower than the label (+8 px)
  ERROR label-collision  a label overlaps a node or another label
  ERROR unknown-id     edge/group refers to a node that doesn't exist
  WARN  label-on-frame  a label sits on a group's dashed frame
  WARN  label-on-route  a label covers part of another edge
  WARN  crossing       two edges cross (move the off-main-path endpoint)
  WARN  fan-out        a node side carries more edges than its length allows (32 + 14*(k-1) px)
  WARN  unlabeled      edge without label and not marked "implied"
  ERROR bad-source     (with --repo-root) a cited path or line range does not exist
  WARN  no-source      (with --repo-root) an internal node cites no source
  WARN  intruder       a non-member node sits inside a group's box
"""
import argparse, html, json, math, os, shutil, subprocess, sys, tempfile
from pathlib import Path

TYPES = {  # fill, stroke, text (light); dark theme handled in CSS
    "actor": ("#FFF4E5", "#B4590A", "#5A2D05"), "client": ("#FFF4E5", "#B4590A", "#5A2D05"),
    "service": ("#E8EEFB", "#2B4C9B", "#14275A"), "gateway": ("#EDE7FA", "#5B3CA8", "#2E1B63"),
    "store": ("#E6F4EC", "#24784A", "#0E3B22"), "cache": ("#E3F5F5", "#16797B", "#0A3C3D"),
    "queue": ("#FCEFF3", "#A63A5C", "#5A1830"), "job": ("#F1F3F5", "#4B5563", "#1F2933"),
    "external": ("#F6F6F6", "#7A7A7A", "#333333"),
}
STYLE = {"sync": "", "async": "6 4", "data": "", "return": "2 4"}
LABEL_H, NODE_H, NODE_H_SUB = 18, 58, 72
PAD = 40


def text_w(s, px=6.5):
    units = sum(2 if ord(ch) > 0x2E80 else 1 for ch in s)  # CJK counts double
    return px * units


def label_box_w(s):
    return text_w(s) + 13


class Diagram:
    def __init__(self, spec):
        self.s = spec
        self.issues = []
        self.nodes = {n["id"]: dict(n) for n in spec.get("nodes", [])}
        self.edges = [dict(e) for e in spec.get("edges", [])]
        for e in self.edges:
            for k in ("from", "to"):
                if e[k] not in self.nodes:
                    self.err("unknown-id", f"edge {e['from']}->{e['to']}: no node {e[k]!r}")
        for g in spec.get("groups", []):
            for m in g.get("members", []):
                if m not in self.nodes:
                    self.err("unknown-id", f"group {g.get('label')!r}: no node {m!r}")

    def check_sources(self, root):
        """Every cited 'path:line' or 'path:start-end' must exist in the repository checkout."""
        items = [("node " + n["id"], n) for n in self.nodes.values()] + [(f"edge {e['from']}->{e['to']}", e) for e in self.edges]
        cited = 0
        for what, item in items:
            for ref in item.get("sources", []):
                cited += 1
                path, _, lines = ref.partition(":")
                f = Path(root) / path
                if not f.is_file():
                    self.err("bad-source", f"{what}: {path} does not exist under {root}")
                    continue
                n = len(f.read_text(encoding="utf-8", errors="replace").splitlines())
                lo, _, hi = lines.partition("-")
                try:
                    lo, hi = int(lo or 1), int(hi or lo or 1)
                except ValueError:
                    self.err("bad-source", f"{what}: cannot read line range in {ref!r}")
                    continue
                if not (1 <= lo <= hi <= n):
                    self.err("bad-source", f"{what}: {ref} is outside the file (1-{n})")
        for what, item in items:
            if what.startswith("node") and item.get("type") not in ("actor", "external") and not item.get("sources"):
                self.warn("no-source", f"{what} has no source reference")
        return cited

    def err(self, code, msg):
        if ("ERROR", code, msg) not in self.issues:
            self.issues.append(("ERROR", code, msg))

    def warn(self, code, msg):
        if ("WARN", code, msg) not in self.issues:
            self.issues.append(("WARN", code, msg))

    # ---------------- layout
    def layout(self):
        N = self.nodes
        for n in N.values():
            n["w"] = n.get("w") or max(140, math.ceil(max(text_w(n["label"], 7.4), text_w(n.get("sub", ""), 5.8)) + 36))
            n["h"] = NODE_H_SUB if n.get("sub") else NODE_H
        cols = sorted({n["col"] for n in N.values()})
        rows = sorted({n["row"] for n in N.values()})
        colw = {c: max(n["w"] for n in N.values() if n["col"] == c) for c in cols}
        rowh = {r: max(n["h"] for n in N.values() if n["row"] == r) for r in rows}
        # gap budget: a label on a horizontal run between adjacent columns needs 6.5px*units + 21px of clear gap
        colgap = {c: 70 for c in cols}
        rowgap = {r: 64 for r in rows}
        for e in self.edges:
            if e["from"] not in N or e["to"] not in N or not e.get("label"):
                continue
            a, b = N[e["from"]], N[e["to"]]
            need = label_box_w(e["label"]) + 8 + 8
            ga = {i for i, g in enumerate(self.s.get("groups", [])) if a["id"] in g.get("members", [])}
            gb = {i for i, g in enumerate(self.s.get("groups", [])) if b["id"] in g.get("members", [])}
            need += 24 * len(ga ^ gb)  # each group frame crossed takes 18 px of the gap
            if a["row"] == b["row"] or e.get("route") == "hv":
                lo, hi = sorted((a["col"], b["col"]))
                span = [c for c in cols if lo <= c < hi]
                if span:  # spread the requirement over the gaps the label could use; it sits in the widest one
                    c = span[len(span) // 2] if a["row"] == b["row"] else (span[-1] if a["col"] < b["col"] else span[0])
                    colgap[c] = max(colgap[c], need)
            else:
                lo, hi = sorted((a["row"], b["row"]))
                for r in rows:  # room for a label beside the line plus a group frame and its title
                    if lo <= r < hi:
                        rowgap[r] = max(rowgap[r], 96)
        top = PAD + 56 + (22 if self.s.get("caption") else 0)
        x = PAD + 20
        self.colx = {}
        for c in cols:
            self.colx[c] = x
            x += colw[c] + colgap[c]
        self.width = x - colgap[cols[-1]] + PAD + 20
        y = top + 26
        self.rowy = {}
        for r in rows:
            self.rowy[r] = y
            y += rowh[r] + rowgap[r]
        self.height = y - rowgap[rows[-1]] + PAD
        for n in N.values():
            n["x"] = self.colx[n["col"]] + (colw[n["col"]] - n["w"]) / 2
            n["y"] = self.rowy[n["row"]] + (rowh[n["row"]] - n["h"]) / 2
        self.colw, self.rowh, self.colgap, self.rowgap = colw, rowh, colgap, rowgap
        self.route()
        # groups
        self.groups = []
        for g in self.s.get("groups", []):
            ms = [N[m] for m in g.get("members", []) if m in N]
            if not ms:
                continue
            x0 = min(m["x"] for m in ms) - 18
            y0 = min(m["y"] for m in ms) - 34
            x1 = max(m["x"] + m["w"] for m in ms) + 18
            y1 = max(m["y"] + m["h"] for m in ms) + 18
            self.groups.append({**g, "box": (x0, y0, x1, y1)})
            self.height = max(self.height, y1 + PAD)
            for n in N.values():
                if n["id"] not in g["members"] and rect_overlap((n["x"], n["y"], n["x"] + n["w"], n["y"] + n["h"]), (x0, y0, x1, y1)):
                    self.warn("intruder", f"{n['id']} sits inside group {g.get('label')!r} but is not a member")
        notes = self.s.get("notes", [])
        for note in notes:  # notes are single SVG lines; widen the canvas rather than clip them
            self.width = max(self.width, PAD * 2 + text_w("• " + note, 6.3))
        self.notes_y = self.height
        if notes:
            self.height += 24 + 22 * len(notes)
        self.height += 34  # legend

    def port(self, n, side, idx, k):
        """Point on a node side; k edges on one side are spread evenly with a 16 px corner gutter."""
        if side in ("left", "right"):
            span = n["h"] - 32
            y = n["y"] + n["h"] / 2 if k == 1 else n["y"] + 16 + span * idx / (k - 1)
            return (n["x"] + (n["w"] if side == "right" else 0), y)
        span = n["w"] - 32
        x = n["x"] + n["w"] / 2 if k == 1 else n["x"] + 16 + span * idx / (k - 1)
        return (x, n["y"] + (n["h"] if side == "bottom" else 0))

    def route(self):
        N = self.nodes
        plans = []
        for e in self.edges:
            if e["from"] not in N or e["to"] not in N:
                continue
            a, b = N[e["from"]], N[e["to"]]
            r = e.get("route", "auto")
            if r == "auto":
                r = "h" if a["row"] == b["row"] else "v" if a["col"] == b["col"] else "hvh"
            if r == "h":
                fs, ts = ("right", "left") if a["col"] < b["col"] else ("left", "right")
            elif r == "v":
                fs, ts = ("bottom", "top") if a["row"] < b["row"] else ("top", "bottom")
            elif r == "hv":
                fs = "right" if a["col"] < b["col"] else "left"
                ts = "top" if a["row"] < b["row"] else "bottom"
            elif r == "vh":
                fs = "bottom" if a["row"] < b["row"] else "top"
                ts = "left" if a["col"] < b["col"] else "right"
            else:
                fs, ts = ("right", "left") if a["col"] < b["col"] else ("left", "right")
            fs, ts = e.get("from_side", fs), e.get("to_side", ts)
            plans.append((e, a, b, r, fs, ts))
        # port spread: group by (node, side), order by the other end's position to avoid self-crossing
        side_use = {}
        for i, (e, a, b, r, fs, ts) in enumerate(plans):
            side_use.setdefault((a["id"], fs), []).append((i, b))
            side_use.setdefault((b["id"], ts), []).append((i, a))
        slot = {}
        for (nid, side), lst in side_use.items():
            key = (lambda o: o[1]["y"]) if side in ("left", "right") else (lambda o: o[1]["x"])
            lst.sort(key=key)
            n = N[nid]
            length = n["h"] if side in ("left", "right") else n["w"]
            k = len(lst)
            if k > 1 and length < 32 + 14 * (k - 1):
                self.warn("fan-out", f"{nid} {side} side carries {k} edges in {length:.0f}px (needs {32 + 14 * (k - 1)}px); spread to other sides or enlarge")
            for j, (i, _) in enumerate(lst):
                slot[(i, nid, side)] = (j, k)
        for i, (e, a, b, r, fs, ts) in enumerate(plans):
            p0 = self.port(a, fs, *slot[(i, a["id"], fs)])
            p1 = self.port(b, ts, *slot[(i, b["id"], ts)])
            if r == "h" and abs(p0[1] - p1[1]) >= 1:  # spread ports disagree: share one y if both sides allow it
                lo, hi = max(a["y"], b["y"]) + 8, min(a["y"] + a["h"], b["y"] + b["h"]) - 8
                if lo <= hi:
                    y = min(max(p0[1], lo), hi)
                    p0, p1 = (p0[0], y), (p1[0], y)
            if r == "v" and abs(p0[0] - p1[0]) >= 1:
                lo, hi = max(a["x"], b["x"]) + 8, min(a["x"] + a["w"], b["x"] + b["w"]) - 8
                if lo <= hi:
                    x = min(max(p0[0], lo), hi)
                    p0, p1 = (x, p0[1]), (x, p1[1])
            if r in ("h", "v") and (abs(p0[1] - p1[1]) < 1 or abs(p0[0] - p1[0]) < 1):
                pts = [p0, p1]
            elif r == "hv" or (fs in ("left", "right") and ts in ("top", "bottom")):
                pts = [p0, (p1[0], p0[1]), p1]
            elif r == "vh" or (fs in ("top", "bottom") and ts in ("left", "right")):
                pts = [p0, (p0[0], p1[1]), p1]
            elif fs in ("left", "right"):  # h-v-h through the gap next to the target column
                gx = (self.colx[b["col"]] - self.colgap.get(b["col"] - 1, self.colgap.get(a["col"], 70)) / 2) if a["col"] < b["col"] \
                    else self.colx[b["col"]] + self.colw[b["col"]] + self.colgap[b["col"]] / 2
                pts = [p0, (gx, p0[1]), (gx, p1[1]), p1]
            else:
                gy = (p0[1] + p1[1]) / 2
                pts = [p0, (p0[0], gy), (p1[0], gy), p1]
            e["pts"] = pts
            # label on the longest segment
            if e.get("label"):
                segs = list(zip(pts, pts[1:]))
                s0, s1 = max(segs, key=lambda s: abs(s[0][0] - s[1][0]) + abs(s[0][1] - s[1][1]))
                w = label_box_w(e["label"])
                mx, my = (s0[0] + s1[0]) / 2, (s0[1] + s1[1]) / 2
                if abs(s0[0] - s1[0]) < 1:  # vertical run: put the label beside the line, not on it
                    vy = min(s0[1], s1[1]) + min(30, abs(s0[1] - s1[1]) / 2)  # near the source end, clear of group frames
                    e["lab"] = (mx + 6, vy - LABEL_H / 2, mx + 6 + w, vy + LABEL_H / 2)
                else:
                    e["lab"] = (mx - w / 2, my - LABEL_H / 2, mx + w / 2, my + LABEL_H / 2)
                if abs(s0[1] - s1[1]) < 1:  # horizontal: the clear run must hold the label
                    run = abs(s0[0] - s1[0])
                    if run < w + 8:
                        self.err("label-gap", f"{e['from']}->{e['to']} label {e['label']!r} needs {w + 8:.0f}px, run is {run:.0f}px")
            elif not e.get("implied"):
                self.warn("unlabeled", f"{e['from']}->{e['to']} has no label (say what flows, or set \"implied\": true)")

    # ---------------- checks
    def check(self):
        N = list(self.nodes.values())
        boxes = {n["id"]: (n["x"], n["y"], n["x"] + n["w"], n["y"] + n["h"]) for n in N}
        for i in range(len(N)):
            for j in range(i + 1, len(N)):
                if rect_overlap(boxes[N[i]["id"]], boxes[N[j]["id"]]):
                    self.err("overlap", f"{N[i]['id']} and {N[j]['id']} overlap (same grid cell?)")
        E = [e for e in self.edges if "pts" in e]
        for e in E:
            for p, q in zip(e["pts"], e["pts"][1:]):
                for nid, b in boxes.items():
                    if nid in (e["from"], e["to"]):
                        continue
                    if seg_hits_rect(p, q, inflate(b, 4)):
                        self.err("through-node", f"{e['from']}->{e['to']} passes through {nid}")
            if "lab" in e:
                for nid, b in boxes.items():
                    if rect_overlap(e["lab"], b):
                        self.err("label-collision", f"label {e['label']!r} overlaps node {nid}")
                for o in E:
                    if o is e or {o["from"], o["to"]} & {e["from"], e["to"]} == {o["from"], o["to"]}:
                        continue
                    if any(seg_hits_rect(p, q, e["lab"]) for p, q in zip(o["pts"], o["pts"][1:])):
                        self.warn("label-on-route", f"label {e['label']!r} sits on edge {o['from']}->{o['to']}")
        for g in getattr(self, "groups", []):
            x0, y0, x1, y1 = g["box"]
            title = (x0, y0, x0 + 24 + text_w(g.get("label", ""), 6.4), y0 + 24)
            for e in E:
                if "lab" not in e:
                    continue
                if rect_overlap(e["lab"], title):
                    self.err("label-collision", f"label {e['label']!r} overlaps the title of group {g.get('label')!r}")
                elif any(seg_hits_rect(p, q, e["lab"]) for p, q in (((x0, y0), (x1, y0)), ((x0, y1), (x1, y1)), ((x0, y0), (x0, y1)), ((x1, y0), (x1, y1)))):
                    self.warn("label-on-frame", f"label {e['label']!r} sits on the frame of group {g.get('label')!r}")
        for i in range(len(E)):
            for j in range(i + 1, len(E)):
                a, b = E[i], E[j]
                if "lab" in a and "lab" in b and rect_overlap(a["lab"], b["lab"]):
                    self.err("label-collision", f"labels {a['label']!r} and {b['label']!r} overlap")
                shared = {a["from"], a["to"]} & {b["from"], b["to"]}
                if shared:
                    continue
                if any(seg_cross(p, q, r, s) for p, q in zip(a["pts"], a["pts"][1:]) for r, s in zip(b["pts"], b["pts"][1:])):
                    self.warn("crossing", f"{a['from']}->{a['to']} crosses {b['from']}->{b['to']}")

    # ---------------- output
    def svg(self):
        W, H = math.ceil(self.width), math.ceil(self.height)
        o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
             f'aria-labelledby="t d" font-family="Inter, Segoe UI, Helvetica, Arial, sans-serif">',
             f'<title id="t">{esc(self.s.get("title", "Diagram"))}</title><desc id="d">{esc(self.s.get("caption", ""))}</desc>',
             "<defs>" + "".join(
                 f'<marker id="arrow-{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" markerUnits="userSpaceOnUse" orient="auto-start-reverse">'
                 f'<path d="M0,0 L10,5 L0,10 z" class="arrowhead {k}"/></marker>' for k in STYLE) + "</defs>",
             f'<rect class="bg" x="0" y="0" width="{W}" height="{H}"/>',
             f'<text class="title" x="{PAD}" y="{PAD + 14}">{esc(self.s.get("title", ""))}</text>']
        if self.s.get("caption"):
            o.append(f'<text class="caption" x="{PAD}" y="{PAD + 38}">{esc(self.s["caption"])}</text>')
        for g in self.groups:
            x0, y0, x1, y1 = g["box"]
            o.append(f'<g class="group {g.get("kind", "boundary")}"><rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" rx="10"/>'
                     f'<text x="{x0 + 12:.1f}" y="{y0 + 18:.1f}">{esc(g.get("label", ""))}</text></g>')
        for e in self.edges:
            if "pts" not in e:
                continue
            st = e.get("style", "sync")
            d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in e["pts"])
            dash = f' stroke-dasharray="{STYLE.get(st, "")}"' if STYLE.get(st) else ""
            o.append(f'<path class="edge {st}" d="{d}"{dash} marker-end="url(#arrow-{st})"/>')
        for e in self.edges:
            if "lab" in e:
                x0, y0, x1, y1 = e["lab"]
                o.append(f'<g class="elabel"><rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" rx="4"/>'
                         f'<text x="{(x0 + x1) / 2:.1f}" y="{y1 - 5:.1f}" text-anchor="middle">{esc(e["label"])}</text></g>')
        # the label's own route must not be hidden by its mask: masks are drawn under nodes, over edges
        for n in self.nodes.values():
            t = n.get("type", "service")
            shape = (f'<path d="{cylinder(n)}"/>' if t == "store" else
                     f'<rect x="{n["x"]:.1f}" y="{n["y"]:.1f}" width="{n["w"]:.1f}" height="{n["h"]:.1f}" rx="{n["h"] / 2 if t in ("actor", "client") else 8}"/>')
            cy = n["y"] + n["h"] / 2 + (-4 if n.get("sub") else 5)
            tip = f'<title>{esc(n["label"])}' + (" — " + esc(", ".join(n["sources"])) if n.get("sources") else "") + "</title>"
            o.append(f'<g class="node {t}" id="n-{esc(n["id"])}">{tip}{shape}'
                     f'<text class="nlabel" x="{n["x"] + n["w"] / 2:.1f}" y="{cy + (4 if t == "store" else 0):.1f}" text-anchor="middle">{esc(n["label"])}</text>'
                     + (f'<text class="nsub" x="{n["x"] + n["w"] / 2:.1f}" y="{cy + 17 + (4 if t == "store" else 0):.1f}" text-anchor="middle">{esc(n["sub"])}</text>' if n.get("sub") else "")
                     + "</g>")
        y = self.notes_y + 6
        for note in self.s.get("notes", []):
            y += 22
            o.append(f'<text class="note" x="{PAD}" y="{y:.1f}">• {esc(note)}</text>')
        # legend: only the types and edge styles actually used
        lx, ly = PAD, self.height - 18
        for t in sorted({n.get("type", "service") for n in self.nodes.values()}):
            o.append(f'<g class="node {t}"><rect x="{lx}" y="{ly - 11}" width="14" height="14" rx="3"/></g><text class="legend" x="{lx + 20}" y="{ly}">{t}</text>')
            lx += 30 + text_w(t, 6.6)
        for st in sorted({e.get("style", "sync") for e in self.edges}):
            dash = f' stroke-dasharray="{STYLE[st]}"' if STYLE.get(st) else ""
            o.append(f'<path class="edge {st}" d="M{lx},{ly - 4} L{lx + 28},{ly - 4}"{dash}/><text class="legend" x="{lx + 34}" y="{ly}">{st}</text>')
            lx += 44 + text_w(st, 6.6)
        o.append("</svg>")
        return "\n".join(o)

    def css(self):
        rules = []
        for t, (f, s, tx) in TYPES.items():
            rules.append(f".node.{t} rect,.node.{t} path{{fill:{f};stroke:{s}}} .node.{t} text{{fill:{tx}}}")
        return """
:root{color-scheme:light dark}
body{margin:0;background:var(--page);font-family:Inter,Segoe UI,Helvetica,Arial,sans-serif}
main{max-width:min(100vw,1800px);margin:0 auto;padding:16px;box-sizing:border-box}
svg{width:100%;height:auto;display:block}
.bg{fill:var(--bg)} .title{font-size:20px;font-weight:700;fill:var(--ink)} .caption{font-size:13px;fill:var(--muted)}
.node rect,.node path{stroke-width:1.6} .nlabel{font-size:13.5px;font-weight:600} .nsub{font-size:10.5px;opacity:.85}
.edge{fill:none;stroke:var(--edge);stroke-width:1.6} .edge.return{stroke:var(--muted)} .edge.data{stroke-width:2.6}
.arrowhead{fill:var(--edge)} .arrowhead.return{fill:var(--muted)}
.elabel rect{fill:var(--bg);opacity:.94} .elabel text{font-size:11px;fill:var(--ink)}
.group rect{fill:none;stroke:var(--muted);stroke-dasharray:5 4;stroke-width:1.2} .group.trust rect{stroke:#B42318}
.group text{font-size:11.5px;font-weight:600;fill:var(--muted)} .note,.legend{font-size:11.5px;fill:var(--muted)}
button{position:fixed;top:10px;right:10px;font:12px sans-serif;padding:4px 8px}
:root{--page:#F3F4F6;--bg:#FFFFFF;--ink:#111827;--muted:#4B5563;--edge:#374151}
:root[data-theme=dark]{--page:#0B0F14;--bg:#111827;--ink:#F3F4F6;--muted:#AEB6C2;--edge:#CBD5E1}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--page:#0B0F14;--bg:#111827;--ink:#F3F4F6;--muted:#AEB6C2;--edge:#CBD5E1}}
@media print{button{display:none}}
""" + "\n".join(rules)

    def html(self):
        return f"""<!doctype html>
<html lang="{esc(self.s.get('lang', 'en'))}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(self.s.get('title', 'Diagram'))}</title><style>{self.css()}</style></head>
<body><button onclick="var r=document.documentElement;r.dataset.theme=(r.dataset.theme==='dark'?'light':'dark')">Theme</button>
<main>{self.svg()}</main></body></html>
"""


def esc(s):
    return html.escape(str(s), quote=True)


def cylinder(n):
    x, y, w, h, ry = n["x"], n["y"], n["w"], n["h"], 7
    return (f"M{x:.1f},{y + ry:.1f} a{w / 2:.1f},{ry} 0 0,1 {w:.1f},0 v{h - 2 * ry:.1f} a{w / 2:.1f},{ry} 0 0,1 {-w:.1f},0 z "
            f"M{x:.1f},{y + ry:.1f} a{w / 2:.1f},{ry} 0 0,0 {w:.1f},0")


def inflate(b, d):
    return (b[0] - d, b[1] - d, b[2] + d, b[3] + d)


def rect_overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def seg_hits_rect(p, q, r):
    x0, x1 = sorted((p[0], q[0]))
    y0, y1 = sorted((p[1], q[1]))
    return x0 < r[2] and r[0] < x1 + 0.01 and y0 < r[3] and r[1] < y1 + 0.01 and not (x1 - x0 < 0.01 and (x0 <= r[0] or x0 >= r[2])) \
        and not (y1 - y0 < 0.01 and (y0 <= r[1] or y0 >= r[3]))


def seg_cross(p, q, r, s):
    """Proper crossing of two axis-aligned (or general) segments, ignoring shared endpoints."""
    def orient(a, b, c):
        v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        return 0 if abs(v) < 1e-6 else (1 if v > 0 else -1)
    o1, o2, o3, o4 = orient(p, q, r), orient(p, q, s), orient(r, s, p), orient(r, s, q)
    return o1 * o2 < 0 and o3 * o4 < 0


def chrome():
    for c in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        if shutil.which(c):
            return shutil.which(c)
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("-o", "--out")
    ap.add_argument("--svg")
    ap.add_argument("--png")
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--repo-root", help="check every node/edge 'sources' entry (path:line or path:a-b) against this checkout")
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    d = Diagram(spec)
    if not any(i[0] == "ERROR" and i[1] == "unknown-id" for i in d.issues):
        d.layout()
        d.check()
        if a.repo_root:
            d.check_sources(a.repo_root)
    if a.json:
        print(json.dumps([{"level": l, "code": c, "message": m} for l, c, m in d.issues], indent=2))
    else:
        for l, c, m in d.issues:
            print(f"{l:<5} {c:<16} {m}")
        print(f"{len(d.nodes)} nodes, {len(d.edges)} edges, {sum(i[0] == 'ERROR' for i in d.issues)} error(s), "
              f"{sum(i[0] == 'WARN' for i in d.issues)} warning(s); canvas {getattr(d, 'width', 0):.0f}x{getattr(d, 'height', 0):.0f}px")
    if not a.check_only and hasattr(d, "width"):
        out = a.out or str(Path(a.spec).with_suffix(".html"))
        Path(out).write_text(d.html(), encoding="utf-8")
        print("wrote", out)
        if a.svg:
            svg = d.svg().replace("<svg ", "<svg ", 1)
            style = "<style>" + d.css().replace(":root[data-theme=dark]", ":root.__never") + "</style>"
            Path(a.svg).write_text(svg.replace("</title>", "</title>" + style, 1), encoding="utf-8")
            print("wrote", a.svg)
        if a.png:
            c = chrome()
            if not c:
                print("no Chrome/Chromium found; skipped PNG", file=sys.stderr)
            else:
                w, h = math.ceil(d.width) + 32, math.ceil(d.height) + 32
                with tempfile.TemporaryDirectory() as tmp:
                    # screenshot a copy without the on-screen theme toggle
                    shot = os.path.join(tmp, "export.html")
                    Path(shot).write_text(d.html().replace("</head>", "<style>button{display:none}</style></head>", 1), encoding="utf-8")
                    subprocess.run([c, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={tmp}",
                                    f"--window-size={w},{h}", "--force-device-scale-factor=2", f"--screenshot={os.path.abspath(a.png)}",
                                    "file://" + shot], capture_output=True, timeout=90)
                print("wrote", a.png if os.path.exists(a.png) else "(PNG failed)")
    sys.exit(1 if any(i[0] == "ERROR" for i in d.issues) else 0)


if __name__ == "__main__":
    main()
