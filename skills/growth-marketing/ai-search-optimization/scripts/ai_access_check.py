#!/usr/bin/env python3
"""Quick AI-search access check for a site (standard library only).

Usage:
  ai_access_check.py https://example.com [/path ...] [--agent NAME ...] [--timeout 15]

Reports:
  * robots.txt verdict per crawler token, grouped by purpose
  * whether each crawler's user-agent string gets an HTTP error/challenge (firewall/CDN check)
  * presence of /llms.txt, /llms-full.txt, /pricing.md, sitemap
  * per page: status, words in raw HTML (no JavaScript), H1 count, JSON-LD types,
    last-modified/updated hints, Markdown negotiation (Accept: text/markdown) and Link header

Add any other assistant vendors' tokens with --agent (search, user and training bots).
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser

AGENTS = {
    "classic search": ["Googlebot", "Bingbot"],
    "AI search discovery": ["OAI-SearchBot", "Claude-SearchBot", "PerplexityBot"],
    "user-triggered fetch": ["ChatGPT-User", "Claude-User", "Perplexity-User"],
    "training / product control": ["GPTBot", "ClaudeBot", "CCBot", "Google-Extended", "Applebot-Extended",
                                   "Meta-ExternalAgent", "Bytespider"],
}
BROWSER_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"


def fetch(url, ua=BROWSER_UA, accept=None, timeout=15):
    headers = {"User-Agent": ua}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(3_000_000).decode(r.headers.get_content_charset() or "utf-8", "replace")
            return r.status, dict(r.headers), body
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), ""
    except Exception as e:  # network errors
        return None, {}, str(e)


def visible_words(html):
    html = re.sub(r"(?is)<(script|style|noscript|svg|template)[^>]*>.*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    text = re.sub(r"&[a-z#0-9]+;", " ", text)
    return len(re.findall(r"[A-Za-z0-9\u00C0-\u024F]{2,}", text))


def jsonld_types(html):
    types = []
    for block in re.findall(r'(?is)<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html):
        try:
            data = json.loads(block.strip())
        except Exception:
            types.append("INVALID-JSON")
            continue
        stack = [data]
        while stack:
            d = stack.pop()
            if isinstance(d, list):
                stack.extend(d)
            elif isinstance(d, dict):
                t = d.get("@type")
                if t:
                    types.extend(t if isinstance(t, list) else [t])
                stack.extend(v for v in d.values() if isinstance(v, (dict, list)))
    return sorted(set(map(str, types)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("site")
    ap.add_argument("paths", nargs="*", default=["/"])
    ap.add_argument("--agent", action="append", default=[], help="extra crawler token to test")
    ap.add_argument("--timeout", type=int, default=15)
    a = ap.parse_args()

    base = a.site.rstrip("/")
    if not base.startswith("http"):
        base = "https://" + base
    agents = dict(AGENTS)
    if a.agent:
        agents["extra (user-supplied)"] = a.agent

    print(f"# AI access check: {base}\n")
    st, _, robots = fetch(base + "/robots.txt", timeout=a.timeout)
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(robots.splitlines() if st == 200 else [])
    print(f"## robots.txt (HTTP {st})")
    sitemaps = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", robots) if st == 200 else []
    test_paths = a.paths or ["/"]
    for purpose, toks in agents.items():
        print(f"- {purpose}:")
        for tok in toks:
            verdicts = ["allow" if rp.can_fetch(tok, base + p) else "BLOCK" for p in test_paths]
            named = "named" if re.search(rf"(?im)^\s*user-agent:\s*{re.escape(tok)}\s*$", robots or "") else "falls back to *"
            print(f"  - {tok}: {', '.join(f'{p}={v}' for p, v in zip(test_paths, verdicts))} ({named})")
    print()

    print("## Firewall / CDN response by user-agent (homepage)")
    for purpose, toks in agents.items():
        for tok in toks:
            s, h, body = fetch(base + "/", ua=f"Mozilla/5.0 (compatible; {tok}/1.0)", timeout=a.timeout)
            flag = ""
            if s is None or s >= 400:
                flag = "  <-- blocked or error"
            elif re.search(r"(?i)captcha|challenge|access denied|attention required", body[:5000]):
                flag = "  <-- looks like a bot challenge page"
            print(f"- {tok}: HTTP {s}{flag}")
    print("(Spoofed UA strings; real crawlers may be verified by IP. Treat as a smoke test.)\n")

    print("## Machine-readable files")
    for p in ["/llms.txt", "/llms-full.txt", "/pricing.md", "/sitemap.xml"]:
        s, h, body = fetch(base + p, timeout=a.timeout)
        size = len(body) if s == 200 else 0
        unfilled = s == 200 and re.search(r"\[[A-Z][^\]\n]{2,80}\](?!\()", body or "")
        print(f"- {p}: HTTP {s}{f', {size:,} chars' if size else ''}"
              + (f"  <-- still has template placeholder {unfilled.group(0)}" if unfilled else ""))
    for sm in sitemaps:
        print(f"- sitemap declared in robots: {sm}")
    print()

    print("## Pages")
    for p in test_paths:
        url = base + p if p.startswith("/") else p
        s, h, html = fetch(url, timeout=a.timeout)
        if not (200 <= int(s or 0) < 300):
            print(f"### {p}  (HTTP {s})\n- not analyzed: fix the status first (crawlers drop non-2xx pages)\n")
            continue
        words = visible_words(html) if html else 0
        h1 = len(re.findall(r"(?i)<h1[\s>]", html))
        types = jsonld_types(html)
        mod = re.search(r'(?i)"dateModified"\s*:\s*"([^"]+)"', html)
        canon = re.search(r'(?i)<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', html)
        noindex = re.search(r'(?i)<meta[^>]+name=["\']robots["\'][^>]+noindex', html) or \
            "noindex" in str({k.lower(): v for k, v in h.items()}.get("x-robots-tag", "")).lower()
        ms, mh, mbody = fetch(url, accept="text/markdown", timeout=a.timeout)
        md_ok = ms == 200 and "markdown" in str({k.lower(): v for k, v in mh.items()}.get("content-type", ""))
        link_hdr = {k.lower(): v for k, v in h.items()}.get("link", "")
        print(f"### {p}  (HTTP {s})")
        print(f"- words in raw HTML: {words:,}" + ("  <-- thin without JS; server-render main content" if words < 200 else ""))
        print(f"- H1 count: {h1}" + ("  <-- expected exactly 1" if h1 != 1 else ""))
        print(f"- JSON-LD types: {', '.join(types) if types else 'none'}")
        print(f"- dateModified: {mod.group(1) if mod else 'not found'}")
        print(f"- canonical: {canon.group(1) if canon else 'missing'}")
        print(f"- noindex: {'YES' if noindex else 'no'}")
        print(f"- Markdown via Accept header: {'yes' if md_ok else 'no'}; Link header: {link_hdr or 'none'}")
        print()


if __name__ == "__main__":
    sys.exit(main())
