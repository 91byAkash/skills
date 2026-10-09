#!/usr/bin/env python3
"""Static QA for a .pptx before (and alongside) looking at rendered slides.

Usage:
  pptx_qa.py deck.pptx [--min-font 12] [--max-words 70] [--max-bullets 6] [--require-notes] [--json]

Per slide it reports:
  ERROR  shape outside the slide, likely text overflow (estimated), leftover
         placeholder/template text, empty placeholder, text under --min-font
  WARN   overlapping text boxes, low text/background contrast (solid fills only),
         too many words or bullets, missing title, missing speaker notes (with
         --require-notes), typed bullet characters, pictures without alt text, edges closer than 0.3 in to the slide edge
Overflow is an estimate from font size and box size (average glyph width
~0.5 em); confirm on the render. Exit 1 when any ERROR is found.
"""
import argparse, json, math, re, sys

from pptx import Presentation
from pptx.util import Emu, Pt

PLACEHOLDER_RE = re.compile(r"lorem|ipsum|\bx{3,}\b|\bTODO\b|\bTBD\b|\[insert|click to (add|edit)|your (text|title) here|placeholder", re.I)
EMU_PER_IN = 914400


def luminance(hexrgb):
    r, g, b = (int(hexrgb[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def solid_hex(fill):
    try:
        if fill.type == 1:  # MSO_FILL.SOLID
            return str(fill.fore_color.rgb)
    except Exception:  # theme colours etc. are not resolvable statically
        return None
    return None


def run_size(run, para, default=18):
    if run.font.size:
        return run.font.size.pt
    if para.font.size:
        return para.font.size.pt
    return default


def estimate_overflow(shape):
    tf = shape.text_frame
    w = shape.width - (tf.margin_left or 0) - (tf.margin_right or 0)
    h = shape.height - (tf.margin_top or 0) - (tf.margin_bottom or 0)
    if w <= 0 or h <= 0:
        return False, 0
    need = 0.0
    for p in tf.paragraphs:
        size = max([run_size(r, p) for r in p.runs] or [18])
        text = "".join(r.text for r in p.runs)
        indent = (p.level or 0) * 0.3 * EMU_PER_IN
        width_pt = max((w - indent) / 12700, 1)
        chars_per_line = max(int(width_pt / (size * 0.5)), 1)
        lines = max(1, math.ceil(len(text) / chars_per_line)) if text else 1
        spacing = (p.space_after.pt if p.space_after is not None else 0)
        need += lines * size * 1.2 + spacing
    have = h / 12700
    return need > have * 1.05, round(need / have, 2) if have else 0


def slide_bg(slide):
    try:
        f = slide.background.fill
        return solid_hex(f)
    except Exception:
        return None


def check(path, a):
    prs = Presentation(path)
    SW, SH = prs.slide_width, prs.slide_height
    report = []
    for idx, slide in enumerate(prs.slides, start=1):
        errs, warns = [], []
        bg = slide_bg(slide) or "FFFFFF"
        words, bullets, texts = 0, 0, []
        has_title = False
        painted = []  # (shape, hex) solid-filled shapes in z-order, for contrast behind text boxes
        for sh in slide.shapes:
            name = f"'{sh.name}'"
            if sh.left is not None and sh.width is not None:
                if sh.left < 0 or sh.top < 0 or sh.left + sh.width > SW + 9525 or sh.top + sh.height > SH + 9525:
                    errs.append(f"{name} extends beyond the slide")
                else:
                    edge = min(sh.left, sh.top, SW - sh.left - sh.width, SH - sh.top - sh.height) / EMU_PER_IN
                    if 0.001 < edge < 0.3 and sh.has_text_frame and sh.text_frame.text.strip():
                        warns.append(f"{name} text box only {edge:.2f} in from the slide edge")
            if sh.is_placeholder:
                pht = str(sh.placeholder_format.type)
                if "TITLE" in pht:
                    has_title = has_title or bool(sh.has_text_frame and sh.text_frame.text.strip())
                if sh.has_text_frame and not sh.text_frame.text.strip() and "PICTURE" not in pht:
                    errs.append(f"{name} empty placeholder (delete it or fill it)")
            if sh.shape_type == 13 and not (sh._element.nvPicPr.cNvPr.get("descr") or "").strip():
                warns.append(f"{name} picture has no alt text")
            try:
                hx = solid_hex(sh.fill) if hasattr(sh, "fill") else None
            except Exception:
                hx = None
            if hx and sh.width:
                painted.append((sh, hx))
            if not sh.has_text_frame:
                continue
            text = sh.text_frame.text
            if not text.strip():
                continue
            if sh.top is not None and sh.top < SH * 0.2 and any((r.font.size and r.font.size.pt >= 28) or r.font.bold for p in sh.text_frame.paragraphs for r in p.runs):
                has_title = True
            words += len(text.split())
            if PLACEHOLDER_RE.search(text):
                errs.append(f"{name} leftover placeholder text: {PLACEHOLDER_RE.search(text).group(0)!r}")
            if re.search(r"^\s*[•●▪◦]\s", text, re.M):
                warns.append(f"{name} typed bullet characters; use paragraph bullets")
            for p in sh.text_frame.paragraphs:
                if p._p.pPr is not None and (p._p.pPr.find("{http://schemas.openxmlformats.org/drawingml/2006/main}buChar") is not None):
                    bullets += 1
                for r in p.runs:
                    sz = run_size(r, p, default=None) if (r.font.size or p.font.size) else None
                    if sz and sz < a.min_font and r.text.strip():
                        errs.append(f"{name} {sz:g} pt text below {a.min_font} pt: {r.text[:40]!r}")
                        break
            over, ratio = estimate_overflow(sh)
            if over:
                errs.append(f"{name} likely overflows (needs ~{ratio}x its height)")
            fill = solid_hex(sh.fill) if hasattr(sh, "fill") else None
            back = fill
            if not back:
                cx, cy = sh.left + sh.width / 2, sh.top + sh.height / 2
                under = [hx for p_, hx in painted if p_.left <= cx <= p_.left + p_.width and p_.top <= cy <= p_.top + p_.height]
                back = under[-1] if under else bg
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    try:
                        col = str(r.font.color.rgb) if r.font.color and r.font.color.type is not None else None
                    except AttributeError:
                        col = None
                    need = 3.0 if run_size(r, p) >= 24 or (r.font.bold and run_size(r, p) >= 18.5) else 4.5  # WCAG AA
                    if col and back and contrast(col, back) < need:
                        warns.append(f"{name} low contrast {col} on {back} ({contrast(col, back):.1f}:1, need {need}:1)")
                        break
                else:
                    continue
                break
            texts.append(sh)
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                s1, s2 = texts[i], texts[j]
                ix = min(s1.left + s1.width, s2.left + s2.width) - max(s1.left, s2.left)
                iy = min(s1.top + s1.height, s2.top + s2.height) - max(s1.top, s2.top)
                if ix > 0.1 * EMU_PER_IN and iy > 0.1 * EMU_PER_IN:
                    warns.append(f"text boxes '{s1.name}' and '{s2.name}' overlap")
        if words > a.max_words:
            warns.append(f"{words} words on the slide (> {a.max_words}); move detail to notes or split")
        if bullets > a.max_bullets:
            warns.append(f"{bullets} bullets (> {a.max_bullets})")
        if not has_title and idx > 1:
            warns.append("no visible title")
        if a.require_notes and not (slide.has_notes_slide and slide.notes_slide.notes_text_frame.text.strip()):
            warns.append("no speaker notes")
        report.append({"slide": idx, "errors": errs, "warnings": warns})
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("--min-font", type=float, default=12)
    ap.add_argument("--max-words", type=int, default=70)
    ap.add_argument("--max-bullets", type=int, default=6)
    ap.add_argument("--require-notes", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rep = check(a.deck, a)
    if a.json:
        print(json.dumps(rep, indent=2))
    else:
        for s in rep:
            for e in s["errors"]:
                print(f"slide {s['slide']}: ERROR {e}")
            for w in s["warnings"]:
                print(f"slide {s['slide']}: WARN  {w}")
        ne = sum(len(s["errors"]) for s in rep)
        nw = sum(len(s["warnings"]) for s in rep)
        print(f"{len(rep)} slides, {ne} error(s), {nw} warning(s)")
    sys.exit(1 if any(s["errors"] for s in rep) else 0)


if __name__ == "__main__":
    main()
