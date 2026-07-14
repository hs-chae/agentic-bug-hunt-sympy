#!/usr/bin/env python3
"""Scan release-facing files for private data and deprecated workflow traces."""

from __future__ import annotations

import sys
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS_ROOT))

from cas_harness.security import scan_paths


def main() -> int:
    targets = [
        HARNESS_ROOT / "README.md",
        HARNESS_ROOT / "AGENTS.md",
        HARNESS_ROOT / "docs",
        HARNESS_ROOT / ".agents",
        HARNESS_ROOT / "scripts",
        HARNESS_ROOT / "cas_harness",
        HARNESS_ROOT / "prompts",
    ]
    findings = scan_paths(targets)
    if findings:
        print("security scan failed")
        for item in findings:
            print(f"- {item}")
        return 1
    print("security scan passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
