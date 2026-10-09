#!/usr/bin/env python3
"""Reconnaissance for an unfamiliar page: full-page screenshot, list of
interactive elements (role, accessible name, suggested locator), and console
messages. Requires the Python automation package:  pip install playwright &&
python3 -m playwright install chromium

Usage: inspect_page.py URL [--out DIR] [--width 1280] [--height 800] [--channel chrome]
  --channel  use an installed browser (chrome, msedge) instead of a downloaded one
Names are computed like the accessibility tree does (aria-labelledby, aria-label,
<label>, alt/title, placeholder, text), so a suggested get_by_role(..., name=...)
matches what Playwright's role locator will find.
"""
import argparse
import json
import os

from playwright.sync_api import sync_playwright

ROLES = ["button", "link", "textbox", "checkbox", "radio", "combobox", "tab", "menuitem", "switch"]

# Simplified accessible-name computation (good enough to pick locators).
ACC_NAME_JS = """el => {
  const txt = n => (n ? n.textContent : "").replace(/\\s+/g, " ").trim();
  const by = el.getAttribute("aria-labelledby");
  if (by) return by.split(/\\s+/).map(id => txt(document.getElementById(id))).join(" ").trim();
  if (el.getAttribute("aria-label")) return el.getAttribute("aria-label").trim();
  if (el.labels && el.labels.length) return Array.from(el.labels).map(txt).join(" ").trim();
  if (el.getAttribute("alt")) return el.getAttribute("alt").trim();
  if (["INPUT", "TEXTAREA", "SELECT"].includes(el.tagName)) {
    if (["submit", "button", "reset"].includes(el.type) && el.value) return el.value;
    return (el.getAttribute("title") || el.getAttribute("placeholder") || "").trim();
  }
  return txt(el) || (el.getAttribute("title") || "").trim();
}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out", default=".artifacts/browser")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=800)
    ap.add_argument("--channel", default=None)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel=a.channel) if a.channel else p.chromium.launch()
        page = browser.new_page(viewport={"width": a.width, "height": a.height})
        console = []
        page.on("console", lambda m: console.append(f"{m.type}: {m.text}"))
        page.on("pageerror", lambda e: console.append(f"pageerror: {e}"))
        page.goto(a.url, wait_until="domcontentloaded")
        try:  # pages with polling/websockets never go idle; carry on after 10 s
            page.wait_for_load_state("networkidle", timeout=10_000)
        except Exception:
            console.append("note: network never went idle within 10 s; inspected anyway")
        shot = os.path.join(a.out, "inspect.png")
        page.screenshot(path=shot, full_page=True)

        found = []
        for role in ROLES:
            for el in page.get_by_role(role).all():
                if not el.is_visible():
                    continue
                name = (el.evaluate(ACC_NAME_JS) or "")[:60]
                tid = el.get_attribute("data-testid")
                loc = f'get_by_role("{role}", name={json.dumps(name)})' if name else (
                    f'get_by_test_id("{tid}")' if tid else f'get_by_role("{role}")  # unnamed: fix markup')
                found.append({"role": role, "name": name, "locator": loc})
        browser.close()

    print(f"screenshot: {shot}")
    print(f"interactive elements ({len(found)}):")
    for f in found:
        print(f"  {f['role']:<9} {f['name']!r:<40} {f['locator']}")
    print("console:" if console else "console: none")
    for c in console:
        print("  " + c)
    with open(os.path.join(a.out, "inspect.json"), "w") as fh:
        json.dump({"elements": found, "console": console}, fh, indent=2)


if __name__ == "__main__":
    main()
