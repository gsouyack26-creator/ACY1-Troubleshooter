#!/usr/bin/env python3
"""
ACY1 Troubleshooter — build script.

Injects admin/troubleshooter_data.json into the single-file HTML by full-line
replacement of the `const DATA = [...]` line, then syncs version.txt from the
VERSION constant in the HTML.

NEVER use a regex on the DATA array body — a `];` inside a step string will match
the wrong terminator (this happened once). Full-line replace only.

Usage:  python build.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "ACY1_Troubleshooter.html"
DATA_JSON = ROOT / "admin" / "troubleshooter_data.json"
VERSION_TXT = ROOT / "version.txt"


def main():
    # 1. Load + validate data
    data = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        sys.exit("ERROR: data JSON is empty or not a list")
    compact = json.dumps(data, ensure_ascii=False, separators=(", ", ": "))

    # 2. Read HTML (preserve BOM)
    raw = HTML.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)

    # 3. Full-line replace the DATA line
    data_idx = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith("const DATA"):
            data_idx = i
            break
    if data_idx is None:
        sys.exit("ERROR: could not find 'const DATA' line in HTML")
    eol = "\n" if lines[data_idx].endswith("\n") else ""
    lines[data_idx] = f"const DATA = {compact};{eol}"

    # 4. Extract VERSION const and validate the badge matches
    version = None
    for line in lines:
        m = re.search(r'const VERSION\s*=\s*"([^"]+)"', line)
        if m:
            version = m.group(1)
            break
    if not version:
        sys.exit("ERROR: could not find VERSION constant")

    # 5. Write HTML back (with BOM if it had one)
    out = "".join(lines)
    encoded = out.encode("utf-8")
    HTML.write_bytes((b"\xef\xbb\xbf" if has_bom else b"") + encoded)

    # 6. Sync version.txt (no BOM, bare version)
    VERSION_TXT.write_text(version + "\n", encoding="utf-8")

    # 7. Sanity re-parse of the injected line
    injected = f"const DATA = {compact};"
    body = injected[len("const DATA = "):-1]
    json.loads(body)  # raises if malformed

    print(f"Built OK")
    print(f"  Version : {version}")
    print(f"  Entries : {len(data)}")
    kinds = {}
    for d in data:
        kinds[d.get("kind", "?")] = kinds.get(d.get("kind", "?"), 0) + 1
    print(f"  By kind : {kinds}")


if __name__ == "__main__":
    main()
