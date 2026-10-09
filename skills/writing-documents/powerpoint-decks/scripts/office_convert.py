#!/usr/bin/env python3
"""Headless LibreOffice conversion that does not hang or collide with other runs.

Usage:
  office_convert.py INPUT --to pdf [--outdir DIR] [--timeout 120]
  office_convert.py INPUT --to xlsx --recalc      # recalc formulas on load, write values
  office_convert.py legacy.doc --to docx

Each run gets a throwaway LibreOffice profile (so a stuck or open instance
cannot block it), is killed after --timeout seconds, and prints the output path.
Exit 0 on success, 1 on failure.
"""
import argparse, os, shutil, subprocess, sys, tempfile
from pathlib import Path

RECALC_XCU = """<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="OOXMLRecalcMode" oor:op="fuse"><value>0</value></prop></item>
<item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="ODFRecalcMode" oor:op="fuse"><value>0</value></prop></item>
</oor:items>
"""

FILTERS = {  # explicit export filters keep LibreOffice from guessing
    "xlsx": "Calc MS Excel 2007 XML",
    "docx": "MS Word 2007 XML",
    "pptx": "Impress MS PowerPoint 2007 XML",
}


def find_soffice():
    for name in ("soffice", "libreoffice"):
        p = shutil.which(name)
        if p:
            return p
    for p in ("/usr/bin/soffice", "/opt/libreoffice/program/soffice",
              "/Applications/LibreOffice.app/Contents/MacOS/soffice"):
        if os.path.exists(p):
            return p
    return None


def convert(src, to, outdir=None, timeout=120, recalc=False):
    soffice = find_soffice()
    if not soffice:
        raise RuntimeError("LibreOffice (soffice) not found; install it or convert elsewhere")
    src = Path(src).resolve()
    if not src.exists():
        raise FileNotFoundError(src)
    outdir = Path(outdir or src.parent).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    profile = Path(tempfile.mkdtemp(prefix="lo-profile-"))
    staging = Path(tempfile.mkdtemp(prefix="lo-out-"))
    try:
        if recalc:
            user = profile / "user"
            user.mkdir(parents=True)
            (user / "registrymodifications.xcu").write_text(RECALC_XCU)
        target = to if to not in FILTERS else f"{to}:{FILTERS[to]}"
        cmd = [soffice, f"-env:UserInstallation=file://{profile}", "--headless",
               "--norestore", "--nolockcheck", "--nodefault", "--nologo",
               "--convert-to", target, "--outdir", str(staging), str(src)]
        env = dict(os.environ, SAL_USE_VCLPLUGIN="svp")
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"LibreOffice timed out after {timeout}s")
        produced = list(staging.glob(f"{src.stem}.{to.split(':')[0]}"))
        if not produced:
            msg = "conversion produced no file:\n" + proc.stdout + proc.stderr
            if "could not be loaded" in msg:
                msg += ("hint: the file may be corrupt, or this LibreOffice lacks the module for it "
                        "(e.g. Debian/Ubuntu 'libreoffice-writer-nogui' for .docx, '-calc-' for .xlsx, "
                        "'-impress-' for .pptx).\n")
            raise RuntimeError(msg)
        dest = outdir / produced[0].name
        shutil.move(str(produced[0]), dest)  # overwrites a same-named input on purpose
        return dest
    finally:
        shutil.rmtree(profile, ignore_errors=True)
        shutil.rmtree(staging, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("--to", required=True, help="pdf, docx, xlsx, pptx, odt, html, txt, csv ...")
    ap.add_argument("--outdir")
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--recalc", action="store_true", help="force formula recalculation on load")
    a = ap.parse_args()
    try:
        print(convert(a.input, a.to, a.outdir, a.timeout, a.recalc))
    except Exception as e:  # noqa: BLE001 - CLI boundary
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
