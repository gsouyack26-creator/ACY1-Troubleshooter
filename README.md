# ACY1 Troubleshooter

**RME Maintenance Troubleshooting Tool** — A single-file HTML app for ACY1 Reliability Maintenance Engineering techs to quickly diagnose and fix equipment issues.

![Version](https://img.shields.io/badge/version-2.1.0-00cc99)
![Entries](https://img.shields.io/badge/fixes-172-blue)

## Features

- **172 troubleshooting entries** across 8 categories
- 🔍 Fuzzy search with keyword matching
- ⚡ Quick Fixes, 🔌 Device Checks, 🔬 Scope Diagnosis, 💻 Install/SSH, 📖 Escalation/FAQ, 🔄 Replacements, ⚡ VFD Faults, 🔌 MDR Blink Codes
- Sidebar navigation with live counters
- ⭐ Favorites & 🕐 Recent history (localStorage)
- 🏷️ Contributor badges (red ★ creator, purple, green)
- 📱 Print-friendly layout
- 🔄 Auto-update system (checks `version.txt` on network share)

## Categories

| Category | Count | Description |
|----------|-------|-------------|
| Quick Fixes | General | First-try solutions for common issues |
| Device Checks | Equipment-specific | Targeted device troubleshooting |
| Scope Diagnosis | Electrical | Oscilloscope-level diagnostics |
| Install / SSH | IT/Controls | Software & network setup |
| Escalation / FAQ | Process | When to escalate, who to call |
| Replacements | Procedures | Step-by-step part replacement guides |
| VFD Faults | 47 codes | PowerFlex 525 fault code reference (F002–F127) |
| MDR Blink Codes | 10 codes | MDR/ConveyLinx control card LED diagnostic (0–9) |

## Deployment

The tool is deployed to the ACY1 RME network share with an auto-update launcher:

```
\\ant\dept-na\ACY1\Support\RME\Troubleshooter\
├── ACY1_Troubleshooter.html    ← Main app (single file, all data embedded)
├── version.txt                  ← Current version for update checks
├── Troubleshooter Launcher.vbs  ← Auto-update launcher (copies latest + opens)
├── Install Troubleshooter.bat   ← Desktop shortcut installer
├── Submit My Fixes.bat          ← Opens submission form for contributors
├── Admin/
│   └── troubleshooter_data.json ← Master data (source of truth for rebuilds)
└── Submissions/                 ← Incoming fix submissions from techs
```

## Development

The app is a single self-contained HTML file with embedded CSS, JS, and data.

**To add/edit entries:**
1. Edit `admin/troubleshooter_data.json` (source of truth)
2. Run `python build.py` — safely injects data into the HTML and syncs `version.txt` from the VERSION constant
3. Bump `const VERSION` in the HTML before running the build if shipping a new version
4. Copy the rebuilt HTML, version.txt, and JSON to the RME share

Never hand-edit or regex the `const DATA = [...]` line — a `];` inside a step string can match the wrong terminator and corrupt the data. `build.py` does a full-line replace to avoid this.

**Data format:**
```json
{
  "equip": "PowerFlex 525",
  "device": "VFD Fault F007",
  "symptom": "F007 — Motor Overload",
  "steps": ["Trigger: ...", "Fix description...", "Reference: ..."],
  "keywords": ["F007", "motor overload", "vfd", "powerflex", "fault", "drive"],
  "kind": "vfd",
  "source": "Rockwell 520-UM001 / UTR Wiki",
  "difficulty": "intermediate",
  "time_est": "10-30 min",
  "author": "SOUYACKG"
}
```

## Author

Built by **SOUYACKG** — ACY1 RME MHE/CSE Tech
