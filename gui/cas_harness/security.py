"""Security/privacy scan for release-facing files."""

from __future__ import annotations

from pathlib import Path


BANNED_PATTERNS = (
    "codex exec",
    "scripts/run_harness.py",
    "CODEX_HOME",
    "rollout",
    "rate_limit",
    "subscription",
    "tokens used",
    "/ryu/",
    "/home/",
    "/Users/",
    "/tmp/",
    "OPENAI_API_KEY",
    "sk-",
)

DEFAULT_EXCLUDED_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "legacy",
    "internal",
}


def should_skip(path: Path) -> bool:
    if path.name in {"security.py", "security_scan.py"}:
        return True
    return any(part in DEFAULT_EXCLUDED_PARTS for part in path.parts)


def scan_paths(paths: list[Path]) -> list[str]:
    findings: list[str] = []
    for root in paths:
        if root.is_file():
            candidates = [root]
        elif root.is_dir():
            candidates = [p for p in root.rglob("*") if p.is_file()]
        else:
            continue
        for path in candidates:
            if should_skip(path):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for pattern in BANNED_PATTERNS:
                if pattern in text:
                    findings.append(f"{path}:{pattern}")
    return findings
