#!/usr/bin/env python3
"""
ACY1 Troubleshooter — build script.

Injects admin/troubleshooter_data.json and admin/decision_trees.json into the
single-file HTML by full-line replacement of the `const DATA = [...]` and
`const TREES = [...]` lines, then syncs version.txt from the VERSION constant.

NEVER use a regex on the DATA/TREES array body — a `];` inside a step string
will match the wrong terminator (this happened once). Full-line replace only.

Usage:  python build.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "ACY1_Troubleshooter.html"
DATA_JSON = ROOT / "admin" / "troubleshooter_data.json"
TREES_JSON = ROOT / "admin" / "decision_trees.json"
VERSION_TXT = ROOT / "version.txt"


def replace_const_line(lines, const_name, compact_json):
    idx = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith(f"const {const_name}"):
            idx = i
            break
    if idx is None:
        sys.exit(f"ERROR: could not find 'const {const_name}' line in HTML")
    eol = "\n" if lines[idx].endswith("\n") else ""
    lines[idx] = f"const {const_name} = {compact_json};{eol}"
    return lines


def main():
    data = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        sys.exit("ERROR: data JSON is empty or not a list")
    data_compact = json.dumps(data, ensure_ascii=False, separators=(", ", ": "))

    trees = json.loads(TREES_JSON.read_text(encoding="utf-8"))
    if not isinstance(trees, list):
        sys.exit("ERROR: trees JSON is not a list")
    trees_compact = json.dumps(trees, ensure_ascii=False, separators=(", ", ": "))

    raw = HTML.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)

    lines = replace_const_line(lines, "DATA", data_compact)
    lines = replace_const_line(lines, "TREES", trees_compact)

    version = None
    for line in lines:
        m = re.search(r'const VERSION\s*=\s*"([^"]+)"', line)
        if m:
            version = m.group(1)
            break
    if not version:
        sys.exit("ERROR: could not find VERSION constant")

    out = "".join(lines)
    encoded = out.encode("utf-8")
    HTML.write_bytes((b"\xef\xbb\xbf" if has_bom else b"") + encoded)

    VERSION_TXT.write_text(version + "\n", encoding="utf-8")

    # Sanity re-parse of both injected lines
    for name, compact in (("DATA", data_compact), ("TREES", trees_compact)):
        injected = f"const {name} = {compact};"
        body = injected[len(f"const {name} = "):-1]
        json.loads(body)

    print("Built OK")
    print(f"  Version : {version}")
    print(f"  Entries : {len(data)}")
    kinds = {}
    for d in data:
        kinds[d.get("kind", "?")] = kinds.get(d.get("kind", "?"), 0) + 1
    print(f"  By kind : {kinds}")
    print(f"  Trees   : {len(trees)} ({', '.join(t['title'] for t in trees)})")


if __name__ == "__main__":
    main()
