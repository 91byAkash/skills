#!/usr/bin/env python3
"""Render a document to page images for visual QA.

Usage:
  render_pages.py FILE [--outdir DIR] [--dpi 100] [--first N --last M] [--prefix page]

FILE may be .pdf or anything LibreOffice opens (.docx .pptx .xlsx .odt ...).
Old images with the same prefix are deleted first so you never inspect stale
renders. Prints absolute paths of the PNGs, one per line. Needs pdftoppm
(poppler-utils); falls back to pypdfium2 if pdftoppm is missing.
"""
import argparse, shutil, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from office_convert import convert  # noqa: E402


def to_pdf(src, workdir):
    src = Path(src)
    if src.suffix.lower() == ".pdf":
        return src
    return convert(src, "pdf", outdir=workdir)


def render(pdf, outdir, prefix, dpi, first=None, last=None):
    outdir.mkdir(parents=True, exist_ok=True)
    for old in outdir.glob(f"{prefix}-*.png"):
        old.unlink()
    if shutil.which("pdftoppm"):
        cmd = ["pdftoppm", "-png", "-r", str(dpi)]
        if first:
            cmd += ["-f", str(first)]
        if last:
            cmd += ["-l", str(last)]
        subprocess.run(cmd + [str(pdf), str(outdir / prefix)], check=True)
    else:
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(str(pdf))
        n = len(doc)
        lo, hi = (first or 1), (last or n)
        width = len(str(n))
        for i in range(lo - 1, hi):
            img = doc[i].render(scale=dpi / 72).to_pil()
            img.save(outdir / f"{prefix}-{str(i + 1).zfill(width)}.png")
    return sorted(outdir.glob(f"{prefix}-*.png"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--dpi", type=int, default=100)
    ap.add_argument("--first", type=int)
    ap.add_argument("--last", type=int)
    ap.add_argument("--prefix", default="page")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        try:
            pdf = to_pdf(a.file, tmp)
            pages = render(Path(pdf), Path(a.outdir), a.prefix, a.dpi, a.first, a.last)
        except (RuntimeError, OSError, subprocess.CalledProcessError) as e:
            sys.exit(f"error: {e}")
    for p in pages:
        print(p.resolve())
    if not pages:
        sys.exit("error: no pages rendered")


if __name__ == "__main__":
    main()
