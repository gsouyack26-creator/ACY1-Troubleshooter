#!/usr/bin/env python3
"""
ACY1 Troubleshooter — build script.

Injects admin/troubleshooter_data.json and admin/decision_trees.json into the
single-file HTML by full-line replacement of the `const DATA = [...]` and
`const TREES = [...]` lines, then syncs version.txt from the VERSION constant.

Also injects diagnose.html (Nexus copy) when admin/diagnose_extras.json and
../nexus/diagnose.html both exist. diagnose DATA = 245 shared + 13 Nexus-only
entries; diagnose TREES = same 4 trees. Both serialized with ensure_ascii=True
to match diagnose.html's existing format.

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

# Nexus diagnose.html paths
DIAGNOSE = ROOT.parent / "nexus" / "diagnose.html"
EXTRAS_JSON = ROOT / "admin" / "diagnose_extras.json"


def replace_const_line(lines, const_name, compact_json):
    matches = [i for i, line in enumerate(lines)
               if line.lstrip().startswith(f"const {const_name}")]
    if not matches:
        sys.exit(f"ERROR: could not find 'const {const_name}' line in HTML")
    if len(matches) > 1:
        sys.exit(f"ERROR: {len(matches)} 'const {const_name}' lines found; "
                 "expected exactly 1 (a stray/commented const would corrupt the wrong line)")
    idx = matches[0]
    eol = ("\r\n" if lines[idx].endswith("\r\n")
           else "\n" if lines[idx].endswith("\n") else "")
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
    print(f"  Standalone entries : {len(data)}")
    kinds = {}
    for d in data:
        kinds[d.get("kind", "?")] = kinds.get(d.get("kind", "?"), 0) + 1
    print(f"  By kind : {kinds}")
    print(f"  Trees   : {len(trees)} ({', '.join(t['title'] for t in trees)})")

    # ── Nexus diagnose.html update ──────────────────────────────────────────
    if not EXTRAS_JSON.exists():
        print(f"\nWARN: {EXTRAS_JSON} not found — skipping diagnose.html update")
        return
    if not DIAGNOSE.exists():
        print(f"\nWARN: {DIAGNOSE} not found — skipping diagnose.html update")
        return

    extras = json.loads(EXTRAS_JSON.read_text(encoding="utf-8"))
    if not isinstance(extras, list):
        sys.exit("ERROR: diagnose_extras.json is not a list")

    diagnose_data = data + extras
    # diagnose.html uses ensure_ascii=True (unicode escapes) — match that format
    diag_data_compact = json.dumps(diagnose_data, ensure_ascii=True, separators=(", ", ": "))
    diag_trees_compact = json.dumps(trees, ensure_ascii=True, separators=(", ", ": "))

    diag_raw = DIAGNOSE.read_bytes()
    diag_has_bom = diag_raw.startswith(b"\xef\xbb\xbf")
    diag_text = diag_raw.decode("utf-8-sig")
    diag_lines = diag_text.splitlines(keepends=True)

    diag_lines = replace_const_line(diag_lines, "DATA", diag_data_compact)
    diag_lines = replace_const_line(diag_lines, "TREES", diag_trees_compact)

    diag_out = "".join(diag_lines)
    diag_encoded = diag_out.encode("utf-8")
    DIAGNOSE.write_bytes((b"\xef\xbb\xbf" if diag_has_bom else b"") + diag_encoded)

    # Sanity re-parse of both injected diagnose lines
    for name, compact in (("DATA", diag_data_compact), ("TREES", diag_trees_compact)):
        injected = f"const {name} = {compact};"
        body = injected[len(f"const {name} = "):-1]
        json.loads(body)

    print(f"\n  Diagnose entries   : {len(diagnose_data)} ({len(data)} shared + {len(extras)} extras)")
    print("  Diagnose re-parse  : OK")


if __name__ == "__main__":
    main()
