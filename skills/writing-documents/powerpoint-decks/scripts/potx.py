#!/usr/bin/env python3
"""Switch a presentation between template (.potx) and deck (.pptx) form.

Only the main part's content type differs, but python-pptx refuses a .potx and
PowerPoint treats a renamed file oddly, so switch the content type properly.

Usage:
  potx.py to-pptx brand.potx brand.pptx     # then edit/build with the other scripts
  potx.py to-potx brand.pptx brand.potx     # hand a template back
"""
import argparse, sys, zipfile

DECK = "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"
TPL = "application/vnd.openxmlformats-officedocument.presentationml.template.main+xml"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("direction", choices=["to-pptx", "to-potx"])
    ap.add_argument("src")
    ap.add_argument("dst")
    a = ap.parse_args()
    if a.src == a.dst:
        sys.exit("dst must differ from src")
    old, new = (TPL, DECK) if a.direction == "to-pptx" else (DECK, TPL)
    with zipfile.ZipFile(a.src) as zin:
        names = zin.namelist()
        ct = zin.read("[Content_Types].xml").decode("utf-8")
        if old not in ct:
            state = "a template" if TPL in ct else "a deck" if DECK in ct else "not a presentation"
            sys.exit(f"{a.src} is already {state}; nothing to switch")
        with zipfile.ZipFile(a.dst, "w", zipfile.ZIP_DEFLATED) as zout:
            zout.writestr("[Content_Types].xml", ct.replace(old, new))
            for n in names:
                if n != "[Content_Types].xml":
                    zout.writestr(zin.getinfo(n), zin.read(n))
    print(f"wrote {a.dst} ({'deck' if new == DECK else 'template'})")


if __name__ == "__main__":
    main()
