#!/usr/bin/env python3
"""Unpack and repack Office Open XML packages (.docx .xlsx .pptx .dotx .potx .xlsm).

Usage:
  ooxml.py unpack IN.docx DIR [--force]    # safe extract; refuses traversal and symlinks
  ooxml.py pack DIR OUT.docx [--force]     # zip with [Content_Types].xml first
  ooxml.py list IN.docx                    # part names and sizes

Why not plain unzip/zip: files from other people are untrusted (path traversal,
symlink entries), and zipping from the wrong directory or over a stale archive
silently ships the wrong parts. XML is extracted byte-for-byte: never pretty-print
it, because whitespace inside <w:t>/<a:t> is document content.
"""
import argparse, os, shutil, stat, sys, zipfile
from pathlib import Path


def unpack(src, dest, force=False):
    dest = Path(dest)
    if dest.exists():
        if not force:
            sys.exit(f"error: {dest} exists (use --force to replace)")
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    root = dest.resolve()
    with zipfile.ZipFile(src) as z:
        for info in z.infolist():
            name = info.filename
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                print(f"skipped symlink entry: {name}", file=sys.stderr)
                continue
            target = (root / name).resolve()
            if root not in target.parents and target != root:
                print(f"skipped unsafe path: {name}", file=sys.stderr)
                continue
            if name.endswith("/"):
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as fsrc, open(target, "wb") as fdst:
                shutil.copyfileobj(fsrc, fdst)
    print(f"unpacked {src} -> {dest}")


def pack(src_dir, out, force=False):
    src_dir = Path(src_dir)
    out = Path(out)
    if not (src_dir / "[Content_Types].xml").exists():
        sys.exit(f"error: {src_dir} has no [Content_Types].xml - not an unpacked package root")
    if out.exists():
        if not force:
            sys.exit(f"error: {out} exists (use --force to overwrite)")
        out.unlink()  # start fresh, or deleted parts would survive
    files = sorted(p for p in src_dir.rglob("*") if p.is_file() and not p.is_symlink())
    rel = lambda p: p.relative_to(src_dir).as_posix()
    files.sort(key=lambda p: (rel(p) != "[Content_Types].xml", not rel(p).startswith("_rels/"), rel(p)))
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            info = zipfile.ZipInfo(rel(p), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, p.read_bytes())
    print(f"packed {src_dir} -> {out} ({len(files)} parts)")


def list_parts(src):
    with zipfile.ZipFile(src) as z:
        for i in z.infolist():
            print(f"{i.file_size:>10}  {i.filename}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    u = sub.add_parser("unpack"); u.add_argument("src"); u.add_argument("dest"); u.add_argument("--force", action="store_true")
    p = sub.add_parser("pack"); p.add_argument("src"); p.add_argument("out"); p.add_argument("--force", action="store_true")
    l = sub.add_parser("list"); l.add_argument("src")
    a = ap.parse_args()
    if a.cmd == "unpack":
        unpack(a.src, a.dest, a.force)
    elif a.cmd == "pack":
        pack(a.src, a.out, a.force)
    else:
        list_parts(a.src)


if __name__ == "__main__":
    main()
