#!/usr/bin/env python3
"""Check that the prototype makes no requests to external domains.

Scans every .html, .css, .js and .svg file in the repository for absolute URLs
(http://, https://, protocol-relative //host) and reports each one that is not
in a comment and is not an XML namespace identifier (xmlns="http://www.w3.org/...",
which is a name, never fetched).

Also flags CSS @import and url() that point outside the repository.

Usage:  python3 tools/check_external.py        (from the repository root)
Exit code 0 = clean, 1 = external references found.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTS = {".html", ".css", ".js", ".svg"}
SKIP_DIRS = {"node_modules", "tools"}  # plus every dot-directory

URL_RE = re.compile(r"""(?:https?:)?//[A-Za-z0-9.-]+\.[A-Za-z]{2,}""")
XMLNS_RE = re.compile(r"""xmlns(?::\w+)?\s*=\s*["']https?://www\.w3\.org/[^"']*["']""")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
LINE_COMMENT_RE = re.compile(r"(^|[^:\"'\\])//[^\n]*")


def blank(match):
    # keep line numbers stable: replace comment text by the same number of newlines
    return "\n" * match.group(0).count("\n")


def strip_comments(text, ext):
    if ext in (".html", ".svg"):
        text = HTML_COMMENT_RE.sub(blank, text)
    if ext in (".css", ".js", ".html"):
        text = BLOCK_COMMENT_RE.sub(blank, text)
    if ext == ".js":
        text = LINE_COMMENT_RE.sub(lambda m: m.group(1), text)
    return text


def main():
    findings = []
    scanned = 0
    for path in sorted(ROOT.rglob("*")):
        if path.suffix.lower() not in EXTS or not path.is_file():
            continue
        if any(part.startswith(".") or part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        scanned += 1
        text = strip_comments(path.read_text(encoding="utf-8"), path.suffix.lower())
        text = XMLNS_RE.sub("xmlns=\"\"", text)
        for lineno, line in enumerate(text.splitlines(), 1):
            for m in URL_RE.finditer(line):
                findings.append(f"{path.relative_to(ROOT)}:{lineno}: {m.group(0)}")

    print(f"Scanned {scanned} files (.html .css .js .svg).")
    if findings:
        print("External references found:")
        for f in findings:
            print("  " + f)
        return 1
    print("No external references: every asset is served from the repository.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
