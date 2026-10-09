#!/usr/bin/env python3
"""Find, extract, validate and image-swap the Mermaid diagrams in a Markdown file.

Usage:
  extract_mermaid.py doc.md --list
  extract_mermaid.py doc.md --extract [--outdir diagrams]          # write each block as .mmd
  extract_mermaid.py doc.md --validate                             # lint + real render check of every block
  extract_mermaid.py doc.md --replace -o doc.images.md [--format png|svg] [--outdir diagrams] [--keep-source]

File names follow  <outdir>/<doc-stem>_<NN>_<type>_<title>.mmd|png|svg , where
title comes from a `%% title: ...` comment in the block, a `title:` front-matter
line, or the nearest heading above it (slugified). Stable names mean re-running
after an edit overwrites the right files instead of piling up copies.

--replace renders every block (a block that fails to render stops the run, so a
broken diagram never reaches the doc) and writes a new Markdown file where each
fence is replaced by ![alt](path). --keep-source adds an HTML comment under the
image pointing at the saved .mmd, so the next editor knows where the source is. Use this for platforms
that don't render Mermaid (Confluence, Word, PDF, most wikis other than
GitHub/GitLab). The input file is never modified.
"""
import argparse, os, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FENCE_OPEN = re.compile(r"^(\s*)(`{3,}|~{3,})\s*mermaid\s*$")


def slug(s, n=40):
    s = re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
    return s[:n].rstrip("_") or "diagram"


def dtype(src):
    """Diagram keyword of a block, skipping front matter, comments and init directives."""
    in_front = False
    for line in src.splitlines():
        t = line.strip()
        if t == "---":
            in_front = not in_front
            continue
        if in_front or not t or t.startswith("%%"):
            continue
        w = t.split()[0]
        return {"graph": "flowchart", "stateDiagram-v2": "state", "stateDiagram": "state", "sequenceDiagram": "sequence",
                "classDiagram": "class", "erDiagram": "er"}.get(w, slug(w.replace("-beta", ""), 20))
    return "diagram"


def parse(md_text):
    blocks, heading, cur = [], "", None
    lines = md_text.splitlines()
    for i, line in enumerate(lines):
        if cur is None:
            m = re.match(r"^#{1,6}\s+(.*)", line)
            if m:
                heading = m.group(1).strip()
            m = FENCE_OPEN.match(line)
            if m:
                cur = {"start": i, "fence": m.group(2), "indent": m.group(1), "src": [], "heading": heading}
        else:
            if line.strip().startswith(cur["fence"][0] * len(cur["fence"])) and line.strip().strip(cur["fence"][0]) == "":
                cur["end"] = i
                cur["src"] = "\n".join(l[len(cur["indent"]):] if l.startswith(cur["indent"]) else l for l in cur["src"])
                blocks.append(cur)
                cur = None
            else:
                cur["src"].append(line)
    if cur is not None:
        sys.exit(f"unclosed mermaid fence starting at line {cur['start'] + 1}")
    return blocks, lines


def title_of(b):
    m = re.search(r"^\s*%%\s*title:\s*(.+)$", b["src"], re.M) or re.search(r"^\s*title:\s*(.+)$", b["src"], re.M)
    return (m.group(1).strip() if m else b["heading"]) or "diagram"


def names(doc, blocks, outdir):
    stem = slug(Path(doc).stem, 30)
    return [Path(outdir) / f"{stem}_{i:02d}_{dtype(b['src'])}_{slug(title_of(b))}" for i, b in enumerate(blocks, 1)]


def render(mmd, out=None, check=False):
    cmd = [str(HERE / "render_mermaid.sh")] + (["--check", str(mmd)] if check else [str(mmd), str(out)])
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("doc")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true")
    g.add_argument("--extract", action="store_true")
    g.add_argument("--validate", action="store_true")
    g.add_argument("--replace", action="store_true")
    ap.add_argument("--outdir", default="diagrams")
    ap.add_argument("--format", choices=["png", "svg"], default="png")
    ap.add_argument("-o", "--out")
    ap.add_argument("--keep-source", action="store_true")
    a = ap.parse_args()
    text = Path(a.doc).read_text(encoding="utf-8")
    blocks, lines = parse(text)
    paths = names(a.doc, blocks, a.outdir)
    if a.list:
        for i, (b, p) in enumerate(zip(blocks, paths), 1):
            n = len(b["src"].splitlines())
            print(f"{i:>2}  lines {b['start'] + 1}-{b['end'] + 1}  {dtype(b['src']):<10} {n:>3} lines  title={title_of(b)!r}  -> {p.name}")
        print(f"{len(blocks)} mermaid block(s)")
        return
    if not blocks:
        sys.exit("no mermaid blocks found")
    if a.validate:
        import tempfile
        bad = 0
        lint = subprocess.run([sys.executable, str(HERE / "lint_mermaid.py"), a.doc], capture_output=True, text=True)
        print(lint.stdout.strip())
        bad += lint.returncode != 0
        with tempfile.TemporaryDirectory() as tmp:
            for i, b in enumerate(blocks, 1):
                f = Path(tmp) / f"b{i}.mmd"
                f.write_text(b["src"] + "\n", encoding="utf-8")
                rc, msg = render(f, check=True)
                status = "OK  " if rc == 0 else "FAIL"
                print(f"{status} block {i} (line {b['start'] + 1}, {dtype(b['src'])})" + ("" if rc == 0 else "\n    " + msg.replace("\n", "\n    ")))
                bad += rc != 0
        sys.exit(1 if bad else 0)
    Path(a.outdir).mkdir(parents=True, exist_ok=True)
    for b, p in zip(blocks, paths):
        p.with_suffix(".mmd").write_text(b["src"] + "\n", encoding="utf-8")
    if a.extract:
        for p in paths:
            print(p.with_suffix(".mmd"))
        return
    # replace
    if not a.out:
        sys.exit("--replace needs -o OUT.md (the input is never overwritten)")
    if Path(a.out).resolve() == Path(a.doc).resolve():
        sys.exit("-o must differ from the input")
    for b, p in zip(blocks, paths):
        rc, msg = render(p.with_suffix(".mmd"), p.with_suffix("." + a.format))
        if rc:
            sys.exit(f"block at line {b['start'] + 1} failed to render; nothing written\n{msg}")
    out_lines, cursor = [], 0
    for b, p in zip(blocks, paths):
        out_lines += lines[cursor:b["start"]]
        rel = Path(os.path.relpath(p.with_suffix("." + a.format), Path(a.out).resolve().parent))
        out_lines.append(f"{b['indent']}![{title_of(b)}]({rel.as_posix()})")
        if a.keep_source:  # HTML comments can't hold "--", so point at the saved .mmd instead of inlining it
            src_rel = Path(os.path.relpath(p.with_suffix(".mmd"), Path(a.out).resolve().parent)).as_posix()
            out_lines.append(f"{b['indent']}<!-- diagram source: {src_rel} (edit it, then re-run extract_mermaid.py --replace) -->")
        cursor = b["end"] + 1
    out_lines += lines[cursor:]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("\n".join(out_lines) + ("\n" if text.endswith("\n") else ""), encoding="utf-8")
    print(f"wrote {a.out} with {len(blocks)} image(s) in {a.outdir}/")


if __name__ == "__main__":
    main()
