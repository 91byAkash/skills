#!/usr/bin/env python3
"""Render a deck (pptx/odp/pdf) and tile the slides into labelled contact sheets
for visual QA or template analysis.

Usage:
  thumbnail_grid.py deck.pptx                    # -> <deck>-grid.png (or -grid-1.png, -2... when split)
  thumbnail_grid.py deck.pptx --cols 4 --max 12 --width 400 --prefix out/qa
  thumbnail_grid.py deck.pdf --slides 3-6

Each tile is labelled with its slide number (1-based, matching the deck), and
hidden slides are still rendered (LibreOffice exports them). Grids past --max
slides split into several images so each stays legible. Needs LibreOffice for
pptx (via office_convert.py) and pdftoppm or pypdfium2.
"""
import argparse, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent


def to_pdf(src, tmp):
    if src.suffix.lower() == ".pdf":
        return src
    r = subprocess.run([sys.executable, str(HERE / "office_convert.py"), str(src), "--to", "pdf", "--outdir", str(tmp)],
                       capture_output=True, text=True)
    pdf = Path(tmp) / (src.stem + ".pdf")
    if r.returncode or not pdf.exists():
        sys.exit(f"conversion failed: {r.stderr.strip() or r.stdout.strip()}")
    return pdf


def render(pdf, tmp, width):
    out = Path(tmp) / "pg"
    try:
        subprocess.run(["pdftoppm", "-png", "-scale-to-x", str(width), "-scale-to-y", "-1", str(pdf), str(out)],
                       check=True, capture_output=True)
        return sorted(Path(tmp).glob("pg-*.png"), key=lambda p: int(p.stem.split("-")[-1]))
    except (FileNotFoundError, subprocess.CalledProcessError):
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(str(pdf))
        files = []
        for i, page in enumerate(doc, 1):
            scale = width / page.get_width()
            f = Path(tmp) / f"pg-{i}.png"
            page.render(scale=scale).to_pil().save(f)
            files.append(f)
        return files


def font(size):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"):
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def sheet(tiles, cols, label_h=28, pad=12):
    w, h = tiles[0][1].size
    rows = (len(tiles) + cols - 1) // cols
    W = cols * w + (cols + 1) * pad
    H = rows * (h + label_h) + (rows + 1) * pad
    img = Image.new("RGB", (W, H), "#DADCE0")
    d = ImageDraw.Draw(img)
    f = font(18)
    for k, (num, t) in enumerate(tiles):
        r, c = divmod(k, cols)
        x = pad + c * (w + pad)
        y = pad + r * (h + label_h + pad)
        d.text((x, y + 4), f"Slide {num}", fill="#202124", font=f)
        img.paste(t.resize((w, h)) if t.size != (w, h) else t, (x, y + label_h))
        d.rectangle([x - 1, y + label_h - 1, x + w, y + label_h + h], outline="#9AA0A6")
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--max", type=int, default=12, help="slides per grid image before splitting")
    ap.add_argument("--width", type=int, default=480, help="tile width in px")
    ap.add_argument("--slides", help="e.g. 1,3-5")
    ap.add_argument("--prefix", help="output path prefix (default: next to the deck, <name>-grid)")
    a = ap.parse_args()
    src = Path(a.deck)
    if not src.exists():
        sys.exit(f"not found: {src}")
    prefix = Path(a.prefix) if a.prefix else src.with_name(src.stem + "-grid")
    prefix.parent.mkdir(parents=True, exist_ok=True)
    for old in prefix.parent.glob(prefix.name + "*.png"):
        old.unlink()  # never leave a stale grid that looks current
    with tempfile.TemporaryDirectory() as tmp:
        pages = render(to_pdf(src, tmp), tmp, a.width)
        nums = list(range(1, len(pages) + 1))
        if a.slides:
            want = set()
            for part in a.slides.split(","):
                lo, _, hi = part.partition("-")
                want.update(range(int(lo), int(hi or lo) + 1))
            nums = [n for n in nums if n in want]
        tiles = [(n, Image.open(pages[n - 1]).convert("RGB")) for n in nums]
        if not tiles:
            sys.exit("no slides rendered")
        chunks = [tiles[i:i + a.max] for i in range(0, len(tiles), a.max)]
        for ci, ch in enumerate(chunks, 1):
            out = Path(f"{prefix}.png") if len(chunks) == 1 else Path(f"{prefix}-{ci}.png")
            sheet(ch, min(a.cols, len(ch))).save(out)
            print(f"{out}  slides {ch[0][0]}-{ch[-1][0]}")


if __name__ == "__main__":
    main()
