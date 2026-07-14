#!/usr/bin/env python3
"""Codex harness for SymPy bug discovery, deduplication, artifacts, and reporting."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


HARNESS_ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = HARNESS_ROOT / "prompts"
SHARED_BUG_POLICY = PROMPTS_DIR / "shared_bug_policy.md"
HUNTER_PROMPT = PROMPTS_DIR / "hunter_candidate.md"
VERIFY_PROMPT = PROMPTS_DIR / "verify_agent.md"
DIAGNOSIS_PROMPT = PROMPTS_DIR / "diagnosis_agent.md"
DEDUP_PROMPT = PROMPTS_DIR / "dedup_agent.md"
ARTIFACT_PROMPT = PROMPTS_DIR / "artifact_agent.md"
# The write-up phase keeps only the maintainer-facing technical report: a per-bug
# agent writes each detailed bug report, the harness assembles them into the
# standalone technical_report.tex, and a finalize agent compiles it cleanly.
WRITEUP_BUG_PROMPT = PROMPTS_DIR / "writeup_bug.md"
WRITEUP_FINALIZE_PROMPT = PROMPTS_DIR / "writeup_finalize.md"

# Codex sometimes fails not because of anything in our prompt but because the
# upstream model is transiently unavailable ("Selected model is at capacity",
# rate limits, 5xx/gateway errors). A single such blip used to abort an entire
# run (e.g. a capacity error in the dedup gate). Retry these transient failures
# a few times with backoff before giving up. The error must come back from the
# model/server -- we never retry a clean non-zero exit that produced real work.
CODEX_MAX_RETRIES = 5
CODEX_RETRY_BASE_DELAY_SECONDS = 30.0
CODEX_RETRY_MAX_DELAY_SECONDS = 300.0
# Substrings (matched case-insensitively) that, on their own, unambiguously mark
# a transient server-side failure worth retrying. These phrases do not occur in
# ordinary SymPy/bug-hunt output, so they are safe to match anywhere in the log.
CODEX_RETRYABLE_STRONG_MARKERS = (
    "at capacity",
    "please try a different model",
    "rate limit",
    "rate_limit",
    "too many requests",
    "internal server error",
    "service unavailable",
    "bad gateway",
    "gateway timeout",
    "temporarily unavailable",
    "error sending request",
    "stream error",
    "stream disconnected",
    "connection reset",
)
# Markers that DO plausibly appear in normal output (bare HTTP status numbers, the
# word "overloaded", generic timeouts). We only treat these as retryable when they
# appear on a line that also looks like an error/status line, to avoid retrying a
# genuinely-failed phase whose log merely printed e.g. the number 503.
CODEX_RETRYABLE_WEAK_MARKERS = (
    "429",
    "500",
    "502",
    "503",
    "504",
    "server error",
    "overloaded",
    "timed out",
    "timeout",
)
# A weak marker only counts when its line also carries one of these error signals.
CODEX_ERROR_LINE_SIGNALS = ("error", "failed", "retry", "status", "exception")


def log_tail_text(log_path: Path, max_bytes: int = 8192) -> str:
    """Return the tail of a Codex log as lowercase text for error matching."""
    try:
        with log_path.open("rb") as handle:
            try:
                handle.seek(-max_bytes, os.SEEK_END)
            except OSError:
                handle.seek(0)
            data = handle.read()
    except OSError:
        return ""
    return data.decode("utf-8", errors="replace").lower()


def is_retryable_codex_failure(log_path: Path) -> bool:
    """True if the Codex log tail shows a transient server-side error.

    Strong markers match anywhere; weak/ambiguous markers (bare HTTP numbers,
    generic timeouts) only count on a line that also reads like an error line,
    so we never retry a real failure just because its output contained "503".
    """
    tail = log_tail_text(log_path)
    if not tail:
        return False
    if any(marker in tail for marker in CODEX_RETRYABLE_STRONG_MARKERS):
        return True
    for line in tail.splitlines():
        if not any(signal in line for signal in CODEX_ERROR_LINE_SIGNALS):
            continue
        if any(marker in line for marker in CODEX_RETRYABLE_WEAK_MARKERS):
            return True
    return False

# API list prices (USD per 1,000,000 tokens) used to impute an API-equivalent
# dollar cost from the measured token usage. These are *list API prices*, not
# what you actually pay on a ChatGPT/Codex subscription -- the README spells
# that out. Override any of them with the --price-* flags.
# GPT-5.6 is a three-tier family (Sol / Terra / Luna); Sol is the flagship
# frontier-reasoning tier the harness defaults to, and its list rates match the
# older single-model flagship. Cached-input rates reflect the standard 90%
# cache-read discount. See https://openai.com/index/gpt-5-6/ .
DEFAULT_PRICE_BASIS = "OpenAI gpt-5.6 Sol (Codex) API list price (2026-07)"
DEFAULT_PRICE_INPUT = 5.0
DEFAULT_PRICE_CACHED_INPUT = 0.5
DEFAULT_PRICE_OUTPUT = 30.0

MODEL_PRICE_PRESETS = {
    "gpt-5.6": (
        DEFAULT_PRICE_INPUT,
        DEFAULT_PRICE_CACHED_INPUT,
        DEFAULT_PRICE_OUTPUT,
        DEFAULT_PRICE_BASIS,
    ),
    "gpt-5.6-sol": (
        DEFAULT_PRICE_INPUT,
        DEFAULT_PRICE_CACHED_INPUT,
        DEFAULT_PRICE_OUTPUT,
        DEFAULT_PRICE_BASIS,
    ),
    "gpt-5.6-terra": (
        2.5,
        0.25,
        15.0,
        "OpenAI gpt-5.6 Terra API list price (2026-07)",
    ),
    "gpt-5.6-luna": (
        1.0,
        0.1,
        6.0,
        "OpenAI gpt-5.6 Luna API list price (2026-07)",
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a Codex SymPy bug-hunting harness with final reporting."
    )
    parser.add_argument(
        "--sympy-dir",
        required=True,
        type=Path,
        help="Path to the local SymPy checkout to investigate.",
    )
    parser.add_argument("--max-bugs", type=int, default=10)
    parser.add_argument("--hours", type=float, default=4.0)
    parser.add_argument("--max-empty-passes", type=int, default=3)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help=(
            "Directory where the timestamped cas-bug-results-* run directory is "
            "created. Defaults to the current working directory."
        ),
    )
    parser.add_argument("--model", default=None, help="Optional Codex model.")
    parser.add_argument(
        "--sandbox",
        default="workspace-write",
        choices=["read-only", "workspace-write", "danger-full-access"],
    )
    parser.add_argument(
        "--ask-for-approval",
        default="never",
        choices=["untrusted", "on-failure", "on-request", "never"],
    )
    parser.add_argument(
        "--no-dedup-search",
        action="store_true",
        help="Do not pass --search to the dedup agent.",
    )
    parser.add_argument(
        "--skip-git-repo-check",
        action="store_true",
        help="Pass --skip-git-repo-check to Codex.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned Codex commands without executing them.",
    )
    parser.add_argument(
        "--writeup-report-name",
        default="technical_report.tex",
        help=(
            "Filename for the standalone technical report under final-report/. "
            "Default: technical_report.tex."
        ),
    )
    parser.add_argument(
        "--artifact-repo-url",
        default="",
        help=(
            "Base URL of the public repository where the bug-report bundles are "
            "published (e.g. https://github.com/your-org/your-repo). Each bug "
            "card's 'Artifact' field links to <url>/tree/main/bug-report/<slug>. "
            "When omitted, the card shows the bundle path as plain text instead "
            "of a link, so an unconfigured run never emits a broken URL."
        ),
    )
    parser.add_argument(
        "--skip-pdf",
        action="store_true",
        help="Do not compile the LaTeX reports to PDF after the write-up phase.",
    )
    parser.add_argument(
        "--latex-engine",
        default="auto",
        help=(
            "Engine used to compile the final report to PDF. 'auto' picks the "
            "first available of tectonic, latexmk, pdflatex. You may also pass an "
            "engine name or a full path to a binary (e.g. a dedicated conda env: "
            "~/miniconda3/envs/cas-tex/bin/tectonic), so no activation is needed. "
            "Default: auto."
        ),
    )
    parser.add_argument(
        "--price-input",
        type=float,
        default=DEFAULT_PRICE_INPUT,
        help=(
            "USD per 1,000,000 input (prompt) tokens, used to impute an "
            "equivalent API cost from the measured token usage. Defaults to the "
            f"{DEFAULT_PRICE_BASIS} (${DEFAULT_PRICE_INPUT}/1M)."
        ),
    )
    parser.add_argument(
        "--price-cached-input",
        type=float,
        default=DEFAULT_PRICE_CACHED_INPUT,
        help=(
            "USD per 1,000,000 cached input tokens. Defaults to the "
            f"{DEFAULT_PRICE_BASIS} (${DEFAULT_PRICE_CACHED_INPUT}/1M)."
        ),
    )
    parser.add_argument(
        "--price-output",
        type=float,
        default=DEFAULT_PRICE_OUTPUT,
        help=(
            "USD per 1,000,000 output tokens (output already includes hidden "
            "reasoning tokens). Defaults to the "
            f"{DEFAULT_PRICE_BASIS} (${DEFAULT_PRICE_OUTPUT}/1M)."
        ),
    )
    parser.add_argument(
        "--price-basis",
        default=DEFAULT_PRICE_BASIS,
        help=(
            "Human-readable label for where the prices come from, recorded in the "
            "run summary and README so the dollar figure is reproducible. Override "
            "this when you pass custom --price-* values for a different model."
        ),
    )
    args = parser.parse_args()
    explicit_price_input = any(
        arg == "--price-input" or arg.startswith("--price-input=")
        for arg in sys.argv[1:]
    )
    explicit_price_cached = any(
        arg == "--price-cached-input" or arg.startswith("--price-cached-input=")
        for arg in sys.argv[1:]
    )
    explicit_price_output = any(
        arg == "--price-output" or arg.startswith("--price-output=")
        for arg in sys.argv[1:]
    )
    explicit_price_basis = any(
        arg == "--price-basis" or arg.startswith("--price-basis=")
        for arg in sys.argv[1:]
    )
    if args.model:
        preset = MODEL_PRICE_PRESETS.get(args.model.lower())
        if preset:
            input_price, cached_price, output_price, basis = preset
            if not explicit_price_input:
                args.price_input = input_price
            if not explicit_price_cached:
                args.price_cached_input = cached_price
            if not explicit_price_output:
                args.price_output = output_price
            if not explicit_price_basis:
                args.price_basis = basis
    return args


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def as_list(value: object) -> list:
    return value if isinstance(value, list) else []


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:60] or "untitled"


def filesystem_token(value: str | None, fallback: str = "unknown") -> str:
    if not value:
        return fallback
    token = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip())
    token = re.sub(r"-+", "-", token).strip("-")
    return token or fallback


def format_prompt(template_path: Path, **values: object) -> str:
    template = read_text(template_path)
    for key, value in values.items():
        template = template.replace("{" + key + "}", str(value))
    return template


def codex_base_cmd(
    args: argparse.Namespace,
    workdir: Path,
    output_path: Path,
    *,
    enable_search: bool = False,
) -> list[str]:
    cmd = [
        "codex",
        "--ask-for-approval",
        args.ask_for_approval,
    ]
    if enable_search:
        cmd.append("--search")
    cmd.extend(
        [
            "exec",
            "-C",
            str(workdir),
            "--sandbox",
            args.sandbox,
            "-o",
            str(output_path),
        ]
    )
    if args.model:
        cmd.extend(["--model", args.model])
    if args.skip_git_repo_check:
        cmd.append("--skip-git-repo-check")
    return cmd


def display_cmd(cmd: list[str]) -> str:
    return " ".join(cmd)


# ---------------------------------------------------------------------------
# Codex token-usage accounting
#
# Every model call in the harness funnels through run_codex(), so usage is
# captured there once and aggregated into the run summary. Codex does not print
# usage on stdout in a stable, parseable format, but it persists a per-session
# "rollout" JSONL under $CODEX_HOME/sessions (default ~/.codex/sessions) that
# records cumulative token_count events with the input/cached/output/reasoning
# split -- and it does so whether the CLI is authenticated by API key or by a
# ChatGPT subscription. For each call we locate the rollout written by that call
# (the newest session file touched after the call started) and read the final
# cumulative usage from it, falling back to a "tokens used" total scraped from
# the stdout log. Capture is best-effort: a call with no recoverable usage is
# still recorded (source="unavailable") and accounting never fails a run.
# ---------------------------------------------------------------------------

USAGE_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
)

# Filled in by run_codex; one entry per model call, tagged with its phase.
CODEX_USAGE_RECORDS: list[dict] = []

# Subscription rate-limit reading captured once, before the first model call, so
# the run's plan consumption can be measured as (final - baseline). None when no
# prior rollout exists (e.g. a fresh CODEX_HOME) -- the within-run delta is used
# as a fallback in that case.
RATE_LIMIT_BASELINE: dict | None = None


def codex_sessions_dir() -> Path:
    home = os.environ.get("CODEX_HOME")
    base = Path(home) if home else Path.home() / ".codex"
    return base / "sessions"


def default_codex_home() -> Path:
    home = os.environ.get("CODEX_HOME")
    return Path(home).expanduser() if home else Path.home() / ".codex"


def prepare_isolated_codex_home(path: Path, source_home: Path) -> dict[str, object]:
    """Create a run-private CODEX_HOME with isolated sessions.

    Codex stores token rollouts under ``$CODEX_HOME/sessions``. Using the user's
    normal CODEX_HOME makes accounting vulnerable to concurrent Codex sessions.
    This function gives the harness its own sessions directory while symlinking
    existing non-session config/auth files from the real Codex home, avoiding a
    copy of credentials into the result tree.
    """
    path.mkdir(parents=True, exist_ok=True)
    (path / "sessions").mkdir(exist_ok=True)
    linked: list[str] = []
    skipped: list[str] = []
    if source_home.exists():
        for child in source_home.iterdir():
            if child.name == "sessions":
                skipped.append(child.name)
                continue
            dest = path / child.name
            if dest.exists() or dest.is_symlink():
                skipped.append(child.name)
                continue
            os.symlink(child, dest, target_is_directory=child.is_dir())
            linked.append(child.name)
    return {
        "path": str(path),
        "source_home": str(source_home),
        "sessions_isolated": True,
        "linked_entries": sorted(linked),
        "skipped_entries": sorted(skipped),
    }


def _coerce_usage(info: object) -> dict | None:
    if not isinstance(info, dict):
        return None
    out: dict[str, int] = {}
    for key in USAGE_FIELDS:
        value = info.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        out[key] = int(value)
    return out or None


def _usage_total(usage: dict) -> int:
    if "total_tokens" in usage:
        return usage["total_tokens"]
    return usage.get("input_tokens", 0) + usage.get("output_tokens", 0)


def _find_cumulative_usage(obj: object) -> dict | None:
    """Best token-usage block reachable from a parsed rollout line.

    Prefers an explicit ``total_token_usage`` block, then any nested dict that
    itself carries both input and output token counts. The richest (largest
    total) match wins, which for a cumulative rollout is the latest snapshot.
    """
    best: dict | None = None
    best_total = -1
    stack = [obj]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            for key in ("total_token_usage", "token_usage", "usage"):
                cand = _coerce_usage(cur.get(key))
                if cand and _usage_total(cand) >= best_total:
                    best, best_total = cand, _usage_total(cand)
            if "input_tokens" in cur and "output_tokens" in cur:
                cand = _coerce_usage(cur)
                if cand and _usage_total(cand) >= best_total:
                    best, best_total = cand, _usage_total(cand)
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)
    return best


def extract_usage_from_rollout(path: Path) -> dict | None:
    latest: dict | None = None
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                if "token" not in line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                found = _find_cumulative_usage(obj)
                if found:
                    latest = found
    except OSError:
        return None
    return latest


def _coerce_window(info: object) -> dict | None:
    """Normalise one Codex rate-limit window (primary/secondary) to a flat dict."""
    if not isinstance(info, dict):
        return None
    used = info.get("used_percent")
    if isinstance(used, bool) or not isinstance(used, (int, float)):
        return None
    out: dict[str, object] = {"used_percent": float(used)}
    for key in ("window_minutes", "resets_at"):
        value = info.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            out[key] = int(value)
    return out


def _find_rate_limits(obj: object) -> dict | None:
    """Best ``rate_limits`` snapshot reachable from a parsed rollout line.

    Codex records a cumulative rate-limit block per token_count event:
    ``primary`` is the short (5-hour) window and ``secondary`` the long
    (weekly) window, each with a ``used_percent`` and ``resets_at``. We keep the
    snapshot with the highest weekly used_percent, which for a within-window
    rollout is the latest reading.
    """
    best: dict | None = None
    best_key = -1.0
    stack = [obj]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            raw = cur.get("rate_limits")
            if isinstance(raw, dict):
                primary = _coerce_window(raw.get("primary"))
                secondary = _coerce_window(raw.get("secondary"))
                if primary or secondary:
                    snap: dict[str, object] = {}
                    if primary:
                        snap["primary"] = primary
                    if secondary:
                        snap["secondary"] = secondary
                    plan = raw.get("plan_type")
                    if isinstance(plan, str):
                        snap["plan_type"] = plan
                    rank = float(
                        (secondary or {}).get("used_percent",
                        (primary or {}).get("used_percent", 0.0))
                    )
                    if rank >= best_key:
                        best, best_key = snap, rank
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)
    return best


def extract_rate_limits_from_rollout(path: Path) -> dict | None:
    latest: dict | None = None
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                if "rate_limit" not in line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                found = _find_rate_limits(obj)
                if found:
                    latest = found
    except OSError:
        return None
    return latest


def capture_rate_limit_baseline() -> dict | None:
    """Read the newest existing rollout's rate-limit snapshot as a pre-run baseline.

    Called once before the first model call. The returned snapshot reflects the
    plan usage Codex last saw, so subtracting it from the final reading yields
    this run's own consumption -- provided no window reset happened in between
    (the caller checks ``resets_at`` to detect that).
    """
    global RATE_LIMIT_BASELINE
    try:
        rollout = newest_rollout_since(0.0)
        if rollout is not None:
            RATE_LIMIT_BASELINE = extract_rate_limits_from_rollout(rollout)
    except Exception:  # noqa: BLE001 - accounting must never break the harness
        RATE_LIMIT_BASELINE = None
    return RATE_LIMIT_BASELINE


def newest_rollout_since(since: float) -> Path | None:
    sessions = codex_sessions_dir()
    if not sessions.is_dir():
        return None
    newest: Path | None = None
    newest_mtime = since - 2.0  # small slack for clock/filesystem granularity
    try:
        candidates = list(sessions.rglob("rollout-*.jsonl"))
    except OSError:
        return None
    for path in candidates:
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        if mtime >= newest_mtime:
            newest, newest_mtime = path, mtime
    return newest


def rollout_candidates_between(since: float, until: float) -> list[Path]:
    """Rollout files touched during one Codex subprocess interval.

    A single harness-owned Codex call should normally touch exactly one rollout.
    If another Codex session runs concurrently under the same CODEX_HOME, this
    can return multiple candidates; callers should treat that as ambiguous
    rather than silently charging the newest unrelated session to the harness.
    """
    sessions = codex_sessions_dir()
    if not sessions.is_dir():
        return []
    start = since - 2.0  # small slack for clock/filesystem granularity
    end = until + 2.0
    try:
        candidates = list(sessions.rglob("rollout-*.jsonl"))
    except OSError:
        return []
    touched: list[tuple[float, Path]] = []
    for path in candidates:
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        if start <= mtime <= end:
            touched.append((mtime, path))
    return [path for _, path in sorted(touched)]


_LOG_TOTAL_RE = re.compile(r"(?:tokens used|total tokens)\D{0,12}([\d,]+)", re.IGNORECASE)


def extract_total_from_log(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    matches = _LOG_TOTAL_RE.findall(text)
    if not matches:
        return None
    try:
        return int(matches[-1].replace(",", ""))
    except ValueError:
        return None


def capture_codex_usage(since: float, until: float, log_path: Path) -> dict:
    record: dict[str, object] = {"source": "unavailable"}
    try:
        candidates = rollout_candidates_between(since, until)
        if len(candidates) > 1:
            record["source"] = "ambiguous_rollout"
            record["rollout_candidates"] = [str(path) for path in candidates]
        else:
            rollout = candidates[0] if candidates else None
            if rollout is not None:
                usage = extract_usage_from_rollout(rollout)
                if usage:
                    record.update(usage)
                    record["source"] = "rollout"
                    record["rollout"] = str(rollout)
                # Codex stamps each call's rollout with the cumulative subscription
                # rate-limit usage (5-hour and weekly windows); capture the latest
                # reading so we can report real plan consumption, not a token guess.
                limits = extract_rate_limits_from_rollout(rollout)
                if limits:
                    record["rate_limit"] = limits
    except Exception:  # noqa: BLE001 - accounting must never break the harness
        record["source"] = "error"

    if record["source"] not in ("rollout",):
        total = extract_total_from_log(log_path)
        if total is not None:
            if record["source"] == "ambiguous_rollout":
                record["rollout_source"] = "ambiguous_rollout"
            record["total_tokens"] = total
            record["source"] = "log_text"

    if "input_tokens" in record:
        cached = int(record.get("cached_input_tokens", 0) or 0)
        record["fresh_input_tokens"] = max(0, int(record["input_tokens"]) - cached)
        if "total_tokens" not in record and "output_tokens" in record:
            record["total_tokens"] = (
                int(record["input_tokens"]) + int(record["output_tokens"])
            )
    return record


def run_codex(
    args: argparse.Namespace,
    *,
    prompt: str,
    workdir: Path,
    output_path: Path,
    log_path: Path,
    phase: str = "unknown",
    enable_search: bool = False,
) -> int:
    cmd = codex_base_cmd(args, workdir, output_path, enable_search=enable_search)
    cmd.append("-")

    display = display_cmd(cmd)
    print(f"\n[run] {display}")
    print(f"[log] {log_path}")

    if args.dry_run:
        write_text(log_path, f"DRY RUN\n{display}\n\nPROMPT:\n{prompt}\n")
        CODEX_USAGE_RECORDS.append(
            {"phase": phase, "returncode": 0, "source": "dry_run"}
        )
        return 0

    log_path.parent.mkdir(parents=True, exist_ok=True)
    # Codex does not create the parent of its -o last-message file; create it here
    # so the captured last message is actually written.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    started_at = time.time()

    # Retry transient upstream failures (capacity/rate-limit/5xx). Each attempt
    # overwrites the log, so on a retryable failure we preserve a copy of the
    # failed log alongside the final one for debugging. Usage capture only trusts
    # a uniquely identifiable rollout touched during this subprocess interval.
    proc = None
    for attempt in range(1, CODEX_MAX_RETRIES + 1):
        with log_path.open("w", encoding="utf-8") as log:
            proc = subprocess.run(
                cmd,
                input=prompt,
                text=True,
                stdout=log,
                stderr=subprocess.STDOUT,
                cwd=str(workdir),
                check=False,
            )
        print(f"[exit] {proc.returncode}")

        if proc.returncode == 0 or attempt >= CODEX_MAX_RETRIES:
            break
        if not is_retryable_codex_failure(log_path):
            break

        # Preserve the failed attempt's log before the next attempt overwrites it.
        failed_log = log_path.with_name(
            f"{log_path.stem}.attempt-{attempt}-failed{log_path.suffix}"
        )
        try:
            shutil.copyfile(log_path, failed_log)
        except OSError:
            failed_log = None

        delay = min(
            CODEX_RETRY_BASE_DELAY_SECONDS * (2 ** (attempt - 1)),
            CODEX_RETRY_MAX_DELAY_SECONDS,
        )
        saved = f" (saved {failed_log.name})" if failed_log else ""
        print(
            f"[retry] phase={phase} transient Codex failure on attempt "
            f"{attempt}/{CODEX_MAX_RETRIES}{saved}; waiting {delay:.0f}s before retry"
        )
        time.sleep(delay)

    finished_at = time.time()
    usage = capture_codex_usage(started_at, finished_at, log_path)
    usage_record = {"phase": phase, "returncode": proc.returncode, **usage}
    CODEX_USAGE_RECORDS.append(usage_record)
    if usage.get("source") in ("rollout", "log_text"):
        print(
            f"[usage] phase={phase} in={usage.get('input_tokens', '?')} "
            f"cached={usage.get('cached_input_tokens', '?')} "
            f"out={usage.get('output_tokens', '?')} "
            f"total={usage.get('total_tokens', '?')} (source={usage['source']})"
        )
    else:
        print(f"[usage] phase={phase} usage unavailable")
    return proc.returncode


def parse_dedup_front_matter(path: Path) -> tuple[str, int | None, str]:
    text = read_text(path)
    verdict = "unclear"
    confidence = None
    recommendation = "continue_but_mark_unclear"

    front = re.search(r"^---\n(.*?)\n---", text, re.DOTALL)
    if front:
        for line in front.group(1).splitlines():
            if line.startswith("verdict:"):
                verdict = line.split(":", 1)[1].strip()
            elif line.startswith("confidence:"):
                raw = line.split(":", 1)[1].strip()
                try:
                    confidence = int(raw)
                except ValueError:
                    confidence = None

    recommendation_text = text
    section = re.search(
        r"^## Recommendation\s*\n(.*?)(?=^## |\Z)",
        text,
        re.DOTALL | re.MULTILINE,
    )
    if section:
        recommendation_text = section.group(1)

    for candidate in (
        "reject_as_duplicate",
        "continue_to_artifact_generation",
        "continue_but_mark_unclear",
    ):
        if candidate in recommendation_text:
            recommendation = candidate
            break

    return verdict, confidence, recommendation


def parse_verify_front_matter(path: Path) -> tuple[str, int | None, str]:
    text = read_text(path)
    verdict = "unclear"
    confidence = None
    recommendation = ""

    front = re.search(r"^---\n(.*?)\n---", text, re.DOTALL)
    if front:
        for line in front.group(1).splitlines():
            if line.startswith("verdict:"):
                verdict = line.split(":", 1)[1].strip()
            elif line.startswith("confidence:"):
                raw = line.split(":", 1)[1].strip()
                try:
                    confidence = int(raw)
                except ValueError:
                    confidence = None

    recommendation_text = text
    section = re.search(
        r"^## Recommendation\s*\n(.*?)(?=^## |\Z)",
        text,
        re.DOTALL | re.MULTILINE,
    )
    if section:
        recommendation_text = section.group(1)

    for candidate in (
        "reject_as_false_positive",
        "continue_to_dedup",
        "continue_but_mark_unclear",
    ):
        if candidate in recommendation_text:
            recommendation = candidate
            break

    if not recommendation:
        # Fail open: only an explicit refutation drops a candidate. A missing or
        # ambiguous recommendation keeps it (marked unclear) so a verifier glitch
        # never silently discards a real bug.
        recommendation = {
            "confirmed": "continue_to_dedup",
            "refuted": "reject_as_false_positive",
        }.get(verdict, "continue_but_mark_unclear")

    return verdict, confidence, recommendation


def parse_diagnosis_front_matter(path: Path) -> tuple[str, int | None, str]:
    text = read_text(path)
    status = "inconclusive"
    confidence = None
    location = ""

    front = re.search(r"^---\n(.*?)\n---", text, re.DOTALL)
    if front:
        for line in front.group(1).splitlines():
            if line.startswith("diagnosis_status:"):
                status = line.split(":", 1)[1].strip()
            elif line.startswith("confidence:"):
                raw = line.split(":", 1)[1].strip()
                try:
                    confidence = int(raw)
                except ValueError:
                    confidence = None
            elif line.startswith("location:"):
                location = line.split(":", 1)[1].strip()

    return status, confidence, location


def existing_artifact_count(root: Path) -> int:
    if not root.exists():
        return 0
    return sum(1 for child in root.iterdir() if child.is_dir() and child.name.startswith("bug-"))


def run_command_json(cmd: list[str], *, cwd: Path | None = None) -> dict:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        return {
            "ok": False,
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        data = {"stdout": proc.stdout.strip()}
    data["ok"] = True
    return data


def collect_sympy_metadata(sympy_dir: Path) -> dict:
    probe = (
        "import json, pathlib, sys\n"
        f"checkout = pathlib.Path({str(sympy_dir)!r}).resolve()\n"
        "sys.path.insert(0, str(checkout))\n"
        "import sympy\n"
        "sympy_file = pathlib.Path(sympy.__file__).resolve()\n"
        "print(json.dumps({\n"
        "    'sympy_version': sympy.__version__,\n"
        "    'sympy_file': str(sympy_file),\n"
        "    'sympy_imports_from_checkout': str(sympy_file).startswith(str(checkout)),\n"
        "    'python_executable': sys.executable,\n"
        "    'python_version': sys.version,\n"
        "}))\n"
    )
    metadata = run_command_json([sys.executable, "-c", probe])
    if not metadata.get("ok"):
        metadata.update(
            {
                "sympy_version": None,
                "sympy_file": None,
                "sympy_imports_from_checkout": False,
                "python_executable": sys.executable,
                "python_version": sys.version,
            }
        )

    commit_proc = subprocess.run(
        ["git", "-C", str(sympy_dir), "rev-parse", "HEAD"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    metadata["sympy_commit"] = (
        commit_proc.stdout.strip() if commit_proc.returncode == 0 else None
    )
    return metadata


def first_markdown_heading(path: Path) -> str:
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return ""


def read_limited(path: Path, limit: int = 800) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "\n..."


def collect_bug_dirs(*bug_roots: Path) -> list[Path]:
    seen: set[Path] = set()
    bug_dirs: list[Path] = []
    for bug_root in bug_roots:
        if not bug_root.exists():
            continue
        for child in sorted(bug_root.iterdir()):
            if child.is_dir() and child.name.startswith("bug-") and child not in seen:
                bug_dirs.append(child)
                seen.add(child)
    return bug_dirs


def display_path(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def collect_local_collision_context(
    sympy_dir: Path,
    run_root: Path,
    bug_report_root: Path,
    candidates_root: Path,
) -> str:
    lines = [
        "## Local collision-avoidance context",
        "",
        "Use the duplicate criterion for local collision avoidance: a new candidate "
        "duplicates an earlier local bug only if resolving the earlier bug would "
        "automatically resolve the new candidate. Do not discard a candidate merely "
        "because it has similar symptoms, the same subsystem, or the same broad "
        "mathematical family.",
        "",
    ]

    legacy_bug_root = sympy_dir / "bug-report"
    bug_dirs = collect_bug_dirs(bug_report_root, legacy_bug_root)

    if bug_dirs:
        lines.append("### Existing confirmed local bug artifacts")
        for bug_dir in bug_dirs[-20:]:
            readme = bug_dir / "README.md"
            title = first_markdown_heading(readme) or bug_dir.name
            reproducer = bug_dir / "reproduce_bug.py"
            if not reproducer.is_file():
                # Fall back to the legacy filename so collision context still shows
                # a reproducer excerpt for bundles created before the rename.
                reproducer = bug_dir / "minimal_reproducer.py"
            minimal = read_limited(reproducer, 600)
            lines.extend(
                [
                    "",
                    f"- `{display_path(bug_dir, run_root)}`: {title}",
                ]
            )
            if minimal:
                lines.extend(["", "  Minimal reproducer excerpt:", "", "  ```python"])
                lines.extend(f"  {line}" for line in minimal.splitlines())
                lines.append("  ```")
        if len(bug_dirs) > 20:
            lines.append(f"\n- Omitted {len(bug_dirs) - 20} older local bug artifacts from this prompt.")
    else:
        lines.append("### Existing confirmed local bug artifacts\n\nNone found.")

    candidate_jsons = sorted(candidates_root.glob("candidate-*/candidate_minimized.json"))
    prior_candidates: list[dict] = []
    for path in candidate_jsons[-20:]:
        try:
            data = load_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        if data.get("status") == "candidate":
            prior_candidates.append(
                {
                    "path": path,
                    "title": data.get("title", ""),
                    "subsystem": data.get("subsystem", ""),
                    "error_signature": data.get("error_signature", ""),
                }
            )

    if prior_candidates:
        lines.extend(["", "### Prior minimized candidates in this harness run"])
        for item in prior_candidates:
            rel = display_path(item["path"], run_root)
            lines.append(
                f"- `{rel}`: {item['title']} | subsystem={item['subsystem']} | "
                f"signature={item['error_signature']}"
            )
    else:
        lines.extend(["", "### Prior minimized candidates in this harness run", "", "None found."])

    return "\n".join(lines).rstrip() + "\n"


def build_target_context(
    sympy_dir: Path, run_root: Path, scratch_dir: Path, metadata: dict
) -> str:
    return "\n".join(
        [
            "## Harness target context",
            "",
            f"- SYMPY_CHECKOUT_PATH: `{sympy_dir}`",
            f"- RESULT_DIR: `{run_root}`",
            f"- SCRATCH_DIR: `{scratch_dir}`",
            f"- SymPy version: `{metadata.get('sympy_version')}`",
            f"- SymPy file: `{metadata.get('sympy_file')}`",
            f"- SymPy commit: `{metadata.get('sympy_commit')}`",
            f"- Python executable: `{metadata.get('python_executable')}`",
            "",
            "All runnable scripts you create must read SYMPY_CHECKOUT_PATH from the "
            "environment (the harness exports it for you) and prepend it to "
            "`sys.path` before importing `sympy` -- do NOT hardcode the absolute "
            "path into the file, so the published artifact stays portable. Each "
            "script must print `sympy.__version__`, `sympy.__file__`, and "
            "`sys.executable`.",
            "",
            "SCRATCH_DIR is your private scratch directory for this phase; it "
            "already exists. Put every throwaway exploration, instrumentation, or "
            "experiment script there (for example `SCRATCH_DIR/bug_hunt.py`) "
            "instead of at the top of RESULT_DIR. Your Codex working directory is "
            "RESULT_DIR, but you must keep it clean: write structured outputs only "
            "to the absolute paths the harness gives you, and scratch only under "
            "SCRATCH_DIR. Do not write loose scripts directly under RESULT_DIR.",
        ]
    )


def build_candidate_prompt(
    candidate_batch: Path,
    sympy_dir: Path,
    run_root: Path,
    scratch_dir: Path,
    bug_report_root: Path,
    candidates_root: Path,
    metadata: dict,
) -> str:
    shared = read_text(SHARED_BUG_POLICY)
    target_context = build_target_context(sympy_dir, run_root, scratch_dir, metadata)
    local_context = collect_local_collision_context(
        sympy_dir,
        run_root,
        bug_report_root,
        candidates_root,
    )
    phase = format_prompt(HUNTER_PROMPT, candidate_batch_path=candidate_batch)
    return (
        f"{shared}\n\n"
        "-----\n\n"
        f"{target_context}\n\n"
        "-----\n\n"
        f"{local_context}\n\n"
        "-----\n\n"
        "## Harness phase override: minimized candidate discovery\n\n"
        f"{phase}\n"
    )


def build_dedup_prompt(candidate_batch: Path, scratch_dir: Path) -> str:
    return format_prompt(
        DEDUP_PROMPT,
        candidate_batch_path=candidate_batch,
        scratch_dir=scratch_dir,
    )


def build_verify_prompt(
    verify_batch: Path,
    sympy_dir: Path,
    run_root: Path,
    scratch_dir: Path,
    metadata: dict,
) -> str:
    target_context = build_target_context(sympy_dir, run_root, scratch_dir, metadata)
    phase = format_prompt(VERIFY_PROMPT, verify_batch_path=verify_batch)
    return (
        f"{target_context}\n\n"
        "-----\n\n"
        "## Harness phase override: independent candidate verification\n\n"
        f"{phase}\n"
    )


def build_diagnosis_prompt(
    diagnosis_batch: Path,
    sympy_dir: Path,
    run_root: Path,
    scratch_dir: Path,
    metadata: dict,
) -> str:
    target_context = build_target_context(sympy_dir, run_root, scratch_dir, metadata)
    phase = format_prompt(DIAGNOSIS_PROMPT, diagnosis_batch_path=diagnosis_batch)
    return (
        f"{target_context}\n\n"
        "-----\n\n"
        "## Harness phase override: source-level root-cause diagnosis\n\n"
        f"{phase}\n"
    )


def build_artifact_prompt(
    artifact_batch: Path,
    sympy_dir: Path,
    run_root: Path,
    scratch_dir: Path,
    metadata: dict,
) -> str:
    shared = read_text(SHARED_BUG_POLICY)
    target_context = build_target_context(sympy_dir, run_root, scratch_dir, metadata)
    phase = format_prompt(
        ARTIFACT_PROMPT,
        artifact_batch_path=artifact_batch,
    )
    return (
        f"{shared}\n\n"
        "-----\n\n"
        f"{target_context}\n\n"
        "-----\n\n"
        "## Harness phase override: artifact generation after dedup\n\n"
        f"{phase}\n"
    )


def build_writeup_bug_prompt(
    bug_folder_path: Path,
    bug_id: int,
    bug_title: str,
    detailed_tex_path: Path,
    card_tex_path: Path,
    artifact_slug: str,
    scratch_dir: Path,
    detailed_compile_section: str,
    card_compile_section: str,
    artifact_repo_url: str,
) -> str:
    return format_prompt(
        WRITEUP_BUG_PROMPT,
        bug_folder_path=bug_folder_path,
        bug_id=bug_id,
        bug_title=bug_title,
        detailed_tex_path=detailed_tex_path,
        card_tex_path=card_tex_path,
        artifact_slug=artifact_slug,
        scratch_dir=scratch_dir,
        detailed_compile_section=detailed_compile_section,
        card_compile_section=card_compile_section,
        # Trailing slash stripped so \artifactrepo/tree/... never doubles the
        # slash; empty stays empty so the card degrades to a plain bundle path.
        artifact_repo_url=artifact_repo_url.rstrip("/"),
    )


def build_writeup_finalize_prompt(
    report_tex_path: Path,
    finalize_status_path: Path,
    scratch_dir: Path,
    latex_compile_section: str,
) -> str:
    return format_prompt(
        WRITEUP_FINALIZE_PROMPT,
        report_tex_path=report_tex_path,
        finalize_status_path=finalize_status_path,
        scratch_dir=scratch_dir,
        latex_compile_section=latex_compile_section,
    )


REQUIRED_ARTIFACT_FILES = (
    "README.md",
    "reproduce_bug.py",
    # numerical_evidence.py is folded into related_bugs.py: the single
    # checkout-pinned test carries both the independent numerical cross-check and
    # the parametrized assertions.
    "related_bugs.py",
    "dedup_report.md",
    "pr/README.md",
)

RUNNABLE_ARTIFACT_FILES = (
    "reproduce_bug.py",
    "related_bugs.py",
)

MISPLACED_ARTIFACT_NAMES = {
    "README.md",
    "reproduce_bug.py",
    "numerical_evidence.py",
    "independent_verification.py",
    "related_bugs.py",
    "test_error.py",
    "dedup_report.md",
    "pr_message.md",
}


def validate_artifact_bundle(
    run_root: Path,
    bug_report_root: Path,
    artifact_status: dict,
) -> tuple[bool, list[str], str]:
    errors: list[str] = []
    artifact_dir_raw = artifact_status.get("artifact_dir")
    if not isinstance(artifact_dir_raw, str) or not artifact_dir_raw.strip():
        return False, ["artifact_status.json missing non-empty artifact_dir"], ""

    artifact_dir = Path(artifact_dir_raw)
    if not artifact_dir.is_absolute():
        artifact_dir = run_root / artifact_dir
    artifact_dir = artifact_dir.resolve()

    try:
        artifact_dir.relative_to(bug_report_root.resolve())
    except ValueError:
        errors.append(f"artifact_dir is not under bug-report: {artifact_dir}")

    if not artifact_dir.is_dir():
        errors.append(f"artifact_dir does not exist: {artifact_dir}")
    else:
        for rel in REQUIRED_ARTIFACT_FILES:
            if not (artifact_dir / rel).is_file():
                errors.append(f"missing required artifact file: {rel}")
        for rel in RUNNABLE_ARTIFACT_FILES:
            path = artifact_dir / rel
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for token in (
                "SYMPY_CHECKOUT_PATH",
                "sys.path.insert",
                "sympy.__version__",
                "sympy.__file__",
                "sys.executable",
            ):
                if token not in text:
                    errors.append(f"{rel} missing checkout-pinned import token: {token}")
        pr_tests = artifact_dir / "pr" / "tests"
        if not pr_tests.is_dir() or not any(pr_tests.glob("*.py")):
            errors.append("missing proposed regression test under pr/tests/*.py")

    for root in (run_root, bug_report_root):
        if root.exists():
            for name in MISPLACED_ARTIFACT_NAMES:
                if (root / name).exists():
                    errors.append(f"misplaced per-bug artifact at {root / name}")

    return not errors, errors, display_path(artifact_dir, run_root)


def finalize_artifact_bundle_metadata(
    run_root: Path,
    artifact_status: dict,
    candidate_json: Path,
) -> None:
    # The hunter's candidate_minimized.json and the artifact agent's
    # artifact_status.json stay in candidates/candidate-NNN/ as run scratch; they
    # are no longer copied into the published bundle. Here we only graft in the
    # diagnosis report, which the agent does not write itself.
    artifact_dir_raw = artifact_status.get("artifact_dir")
    if not isinstance(artifact_dir_raw, str) or not artifact_dir_raw.strip():
        return
    artifact_dir = Path(artifact_dir_raw)
    if not artifact_dir.is_absolute():
        artifact_dir = run_root / artifact_dir
    if not artifact_dir.is_dir():
        return
    # The diagnosis agent writes root_cause.md next to the candidate JSON; copy it
    # into the bundle when present (absent when diagnosis was skipped or failed).
    root_cause = candidate_json.parent / "root_cause.md"
    if root_cause.is_file():
        shutil.copyfile(root_cause, artifact_dir / "root_cause.md")


def extract_dedup_verdict_from_artifact(artifact_dir: Path) -> str:
    dedup_report = artifact_dir / "dedup_report.md"
    if not dedup_report.exists():
        return ""
    text = read_limited(dedup_report, 4000)
    front = re.search(r"^---\n(.*?)\n---", text, re.DOTALL)
    if front:
        for line in front.group(1).splitlines():
            if line.startswith("verdict:"):
                return line.split(":", 1)[1].strip()
    match = re.search(
        r"Deduplication verdict\s*\n\s*(novel|family_known_specific_new|likely_duplicate|unclear)",
        text,
        re.IGNORECASE,
    )
    return match.group(1).lower() if match else ""


def read_json_if_present(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return load_json(path)
    except (OSError, json.JSONDecodeError):
        return {}


def normalize_hunter_batch(batch: dict) -> tuple[str, list[dict], list[str]]:
    """Accept the batch contract and the legacy single-candidate shape."""
    status = str(batch.get("status", "unknown"))
    if status == "candidate":
        return "candidates", [batch], as_list(batch.get("commands_run"))
    if status == "candidates":
        candidates = [item for item in as_list(batch.get("candidates")) if isinstance(item, dict)]
        commands = as_list(batch.get("commands_run"))
        if not commands:
            for candidate in candidates:
                commands.extend(as_list(candidate.get("commands_run")))
        return status, candidates, commands
    return status, [], as_list(batch.get("commands_run"))


def candidate_iteration_item(
    *,
    candidate_number: int,
    candidate_dir: Path,
    run_root: Path,
    batch_number: int,
    hunter_rc: int,
    candidate: dict,
) -> dict[str, object]:
    return {
        "candidate_number": candidate_number,
        "candidate_dir": str(candidate_dir.relative_to(run_root)),
        "candidate_json": display_path(candidate_dir / "candidate_minimized.json", run_root),
        "batch_number": batch_number,
        "status": "candidate",
        "title": candidate.get("title", ""),
        "subsystem": candidate.get("subsystem", ""),
        "confidence": candidate.get("confidence", ""),
        "commands_run": as_list(candidate.get("commands_run")),
        "hunter_exit": hunter_rc,
    }


def write_candidate_batch_for_dedup(
    path: Path,
    run_root: Path,
    candidate_entries: list[dict],
) -> None:
    payload = {
        "result_dir": str(run_root),
        "duplicate_criterion": (
            "Reject as duplicate only when resolving an existing public "
            "issue/PR/discussion would automatically resolve the candidate, "
            "or when the exact candidate bug is already publicly described."
        ),
        "candidates": candidate_entries,
    }
    write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_verify_batch(
    path: Path,
    run_root: Path,
    candidate_entries: list[dict],
) -> None:
    payload = {
        "result_dir": str(run_root),
        "verification_criterion": (
            "Confirm a candidate only when its minimal reproducer, run against "
            "the supplied SymPy checkout, reproduces the claimed wrong output AND "
            "at least one independent check (high-precision numerical evaluation, "
            "direct substitution, or a hand derivation) shows the result is "
            "genuinely mathematically wrong. Refute candidates that do not "
            "reproduce, or that turn out to be correct-but-surprising output, a "
            "branch/domain/assumption misunderstanding, or a misjudged expected "
            "value."
        ),
        "candidates": candidate_entries,
    }
    write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_diagnosis_batch(
    path: Path,
    run_root: Path,
    candidate_entries: list[dict],
) -> None:
    payload = {
        "result_dir": str(run_root),
        "diagnosis_instruction": (
            "For each verified candidate, read the SymPy checkout (do not modify "
            "it) and locate the source-level root cause: trace the call path from "
            "the public API call in the reproducer down to the specific code that "
            "produces the wrong result, and identify the file, line, and faulty "
            "logic or missing condition. This is a non-blocking analysis phase; a "
            "candidate without a confidently located cause is still a real bug."
        ),
        "candidates": candidate_entries,
    }
    write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_artifact_batch_plan(
    path: Path,
    run_root: Path,
    bug_report_root: Path,
    items: list[dict],
) -> None:
    payload = {
        "result_dir": str(run_root),
        "bug_report_root": str(bug_report_root),
        "items": items,
    }
    write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def collect_rejected_duplicate_candidates(
    run_root: Path,
    iterations: list[dict],
) -> list[dict]:
    rejected: list[dict] = []
    for item in iterations:
        if item.get("dedup_recommendation") != "reject_as_duplicate":
            continue
        candidate_dir_raw = item.get("candidate_dir", "")
        if not isinstance(candidate_dir_raw, str) or not candidate_dir_raw:
            continue
        candidate_dir = run_root / candidate_dir_raw
        candidate_json = candidate_dir / "candidate_minimized.json"
        dedup_report = candidate_dir / "dedup_report.md"
        candidate = read_json_if_present(candidate_json)
        rejected.append(
            {
                "candidate_number": item.get("candidate_number"),
                "candidate_dir": candidate_dir_raw,
                "candidate_json": display_path(candidate_json, run_root),
                "dedup_report": display_path(dedup_report, run_root),
                "title": candidate.get("title", item.get("title", "")),
                "subsystem": candidate.get("subsystem", item.get("subsystem", "")),
                "suspected_function_or_module": candidate.get(
                    "suspected_function_or_module", ""
                ),
                "error_signature": candidate.get("error_signature", ""),
                "why_wrong": candidate.get("why_wrong", ""),
                "expected_output": candidate.get("expected_output", ""),
                "actual_output": candidate.get("actual_output", ""),
                "dedup_verdict": item.get("dedup_verdict", ""),
                "dedup_confidence": item.get("dedup_confidence"),
                "dedup_recommendation": item.get("dedup_recommendation", ""),
            }
        )
    return rejected


def bug_artifact_deliverable_paths(run_root: Path, artifact_dir_raw: str) -> dict:
    """Resolved relative paths to each per-bug deliverable inside an artifact dir.

    Folded directly into each ``bug_artifacts`` entry in ``run.json`` so the single
    run record points at every per-bug file without a separate manifest.
    """
    if not artifact_dir_raw:
        return {key: "" for key in (
            "readme", "reproduce_bug", "related_bugs",
            "dedup_report", "pr_readme",
        )}
    artifact_dir = run_root / artifact_dir_raw
    return {
        "readme": display_path(artifact_dir / "README.md", run_root),
        "reproduce_bug": display_path(artifact_dir / "reproduce_bug.py", run_root),
        "related_bugs": display_path(
            artifact_dir / "related_bugs.py", run_root
        ),
        "dedup_report": display_path(artifact_dir / "dedup_report.md", run_root),
        "pr_readme": display_path(artifact_dir / "pr" / "README.md", run_root),
    }


# Per-bug section headings every per-bug report must contain (see writeup_bug.md).
BUG_REPORT_SECTIONS = (
    "Minimal Reproducer",
    "Observed Behavior",
    "Expected Behavior",
    "Mathematical Explanation",
    "Source-Level Diagnosis",
    "Additional Failing Instances",
    "Related Issues Assessment",
    "Proposed SymPy Regression Test",
)


def validate_bug_tex(tex_path: Path) -> list[str]:
    """Check that a per-bug report .tex is a self-contained, on-template document."""
    errors: list[str] = []
    if not tex_path.is_file():
        return [f"per-bug tex does not exist: {tex_path}"]
    text = tex_path.read_text(encoding="utf-8", errors="replace")
    for token in ("\\documentclass", "\\begin{document}", "\\end{document}"):
        if token not in text:
            errors.append(f"missing required token: {token}")
    if "\\section{Bug" not in text:
        errors.append("missing \\section{Bug ...} heading")
    for heading in BUG_REPORT_SECTIONS:
        if heading not in text:
            errors.append(f"missing required section: {heading}")
    return errors


# Bold field labels every compact bug card must carry (see the card template in
# writeup_bug.md). These mirror the counterexample cards in the paper's bug catalog.
BUG_CARD_FIELDS = (
    "Task",
    "SymPy's answer",
    "Correct answer",
    "Explanation",
    "Likely root cause",
)


def validate_bug_card(tex_path: Path) -> list[str]:
    """Check that a per-bug card .tex is a self-contained counterexample card."""
    errors: list[str] = []
    if not tex_path.is_file():
        return [f"per-bug card does not exist: {tex_path}"]
    text = tex_path.read_text(encoding="utf-8", errors="replace")
    for token in ("\\documentclass", "\\begin{document}", "\\end{document}"):
        if token not in text:
            errors.append(f"card missing required token: {token}")
    if "\\begin{counterexamplebox}" not in text:
        errors.append("card missing counterexamplebox environment")
    for field in BUG_CARD_FIELDS:
        if field not in text:
            errors.append(f"card missing required field: {field}")
    return errors


DOCUMENT_WRAPPER_TOKENS = ("\\documentclass", "\\begin{document}", "\\end{document}")


def validate_standalone_tex(
    tex_path: Path,
    *,
    label: str,
    required_headings: tuple[str, ...] = (),
) -> list[str]:
    """A standalone document (technical_report.tex) must have the
    document wrapper and any required headings."""
    if not tex_path.is_file():
        return [f"{label} does not exist: {tex_path}"]
    text = tex_path.read_text(encoding="utf-8", errors="replace")
    errors = [
        f"{label} missing required token: {token}"
        for token in DOCUMENT_WRAPPER_TOKENS
        if token not in text
    ]
    errors += [
        f"{label} missing required heading: {heading}"
        for heading in required_headings
        if heading not in text
    ]
    return errors


def _latex_search_dirs() -> list[Path]:
    """User-space locations a no-sudo TeX engine is commonly installed into.

    Covers conda (next to the running Python and $CONDA_PREFIX/bin) and the
    typical TinyTeX / TeX Live user-prefix layouts, so the engine is found even
    when its directory is not on PATH (e.g. conda base not activated).
    """
    dirs: list[Path] = [Path(sys.executable).resolve().parent]
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix:
        dirs.append(Path(conda_prefix) / "bin")
    home = Path.home()
    dirs += [home / ".local" / "bin", home / "bin"]
    tinytex = home / ".TinyTeX" / "bin"
    if tinytex.is_dir():
        dirs += [p for p in tinytex.glob("*") if p.is_dir()]
    return dirs


def find_latex_executable(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    for directory in _latex_search_dirs():
        candidate = directory / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def _engine_kind(name_or_path: str) -> str:
    """Map an engine name or binary path to a known command style."""
    base = Path(name_or_path).name.lower()
    for kind in ("tectonic", "latexmk", "pdflatex"):
        if kind in base:
            return kind
    # Unknown engine name (e.g. xelatex/lualatex): drive it like pdflatex, which
    # accepts the same -interaction / -output-directory flags.
    return "pdflatex"


def resolve_latex_engine(preference: str) -> tuple[str | None, str | None]:
    """Return (engine_kind, executable_path), or (None, None) if none found.

    `preference` may be 'auto', an engine name, or a full path to a binary (which
    lets you keep the engine in a dedicated env without activating it).
    """
    if preference and preference != "auto" and (os.sep in preference or Path(preference).is_absolute()):
        exe = preference if (Path(preference).is_file() and os.access(preference, os.X_OK)) else shutil.which(preference)
        return (_engine_kind(preference), str(exe)) if exe else (None, None)

    order = (
        ["tectonic", "latexmk", "pdflatex"]
        if preference in ("auto", "", None)
        else [preference]
    )
    for engine in order:
        exe = find_latex_executable(engine)
        if exe:
            return _engine_kind(engine), exe
    return None, None


def latex_engine_commands(engine: str, exe: str, tex_path: Path, outdir: Path) -> list[list[str]]:
    tex = str(tex_path)
    out = str(outdir)
    if engine == "tectonic":
        return [[exe, "--keep-logs", "--outdir", out, tex]]
    if engine == "latexmk":
        return [
            [exe, "-pdf", "-interaction=nonstopmode", "-halt-on-error",
             f"-outdir={out}", tex],
        ]
    # pdflatex: run twice so cross-references/labels resolve.
    cmd = [exe, "-interaction=nonstopmode", "-halt-on-error",
           f"-output-directory={out}", tex]
    return [cmd, cmd]


def latex_compile_command(engine: str, exe: str, tex_path: Path, outdir: Path) -> str:
    """Shell command string an agent can run to compile `tex_path` into `outdir`."""
    cmds = latex_engine_commands(engine, exe, tex_path, outdir)
    return " && ".join(
        " ".join(shlex.quote(str(part)) for part in cmd) for cmd in cmds
    )


def build_latex_compile_section(
    engine: str | None,
    exe: str | None,
    tex_path: Path,
    outdir: Path,
    *,
    doc_label: str,
) -> str:
    """Prompt block telling an agent to compile `doc_label` and fix until clean.

    When no engine is available, returns a self-review instruction instead so the
    agent does not try to run a compiler that is not installed.
    """
    if not engine or not exe:
        return (
            "No LaTeX engine is available in this environment, so you cannot "
            f"compile {doc_label}. Instead, carefully self-review the LaTeX before "
            "finishing: balanced environments, escaped special characters "
            "(`_`, `%`, `&`, `#`, `$`), tables and lines that stay within the page "
            "margins, and no undefined commands. Do not try to run a compiler."
        )
    cmd = latex_compile_command(engine, exe, tex_path, outdir)
    return (
        f"A LaTeX engine ({engine}) is available, and you MUST compile {doc_label} "
        "and fix every problem the compiler reports before you finish. Loop:\n\n"
        f"1. Compile by running exactly:\n\n        {cmd}\n\n"
        f"   All auxiliary/output files (`.aux`, `.log`, `.pdf`) go under "
        f"`{outdir}`, keeping the deliverable directory clean.\n"
        "2. Read the compiler's console output and the `.log` file written under "
        "that output directory.\n"
        "3. Fix EVERY error and EVERY warning by editing the `.tex` file only — "
        "never change the report's meaning or delete content. Typical fixes: "
        "escape special characters, wrap or shrink overfull lines/tables, repair "
        "unbalanced or misspelled environments, and make sure every command you "
        "use is provided by the existing preamble (do not add packages that need "
        "shell-escape).\n"
        "4. Recompile and repeat until the compile reports no errors and no "
        "warnings.\n\n"
        "You must run at least one compile pass. If after about 6 passes only a "
        "benign, genuinely unavoidable warning remains (for example a tiny "
        "overfull \\hbox that cannot be removed without harming content), you may "
        "stop — but every error and every fixable warning must be gone first. "
        "Never finish while the document still fails to compile."
    )


def compile_tex_to_pdf(
    tex_path: Path,
    preference: str,
    log_path: Path,
    timeout: int = 600,
    outdir: Path | None = None,
) -> tuple[str, str, Path | None]:
    """Compile a .tex file to PDF without sudo, using a user-space engine.

    Auxiliary/output files (.aux, .log, .pdf) are written under ``outdir``,
    defaulting to the .tex file's own directory. Pass a separate ``outdir`` to
    keep the engine's byproducts out of a deliverable directory.

    Returns (status, engine, pdf_path). status is one of:
    no_engine, compiled, failed, error.
    """
    tex_path = tex_path.resolve()
    engine, exe = resolve_latex_engine(preference)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if engine is None or exe is None:
        write_text(
            log_path,
            "No LaTeX engine found (looked for tectonic, latexmk, pdflatex on "
            f"PATH and in user-space dirs; preference={preference}).\n"
            "Install one without sudo, e.g. `conda install -c conda-forge "
            "tectonic`, then re-run, or compile final-report/*.tex manually.\n",
        )
        return "no_engine", "", None

    outdir = (outdir or tex_path.parent).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    pdf_path = outdir / (tex_path.stem + ".pdf")
    commands = latex_engine_commands(engine, exe, tex_path, outdir)
    with log_path.open("w", encoding="utf-8") as log:
        log.write(f"[compile] engine={engine} exe={exe} tex={tex_path}\n")
        for cmd in commands:
            log.write(f"[compile] {' '.join(cmd)}\n")
            log.flush()
            try:
                proc = subprocess.run(
                    cmd,
                    cwd=str(outdir),
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    timeout=timeout,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                log.write(f"\n[compile] TIMEOUT after {timeout}s\n")
                return "failed", engine, (pdf_path if pdf_path.is_file() else None)
            except OSError as exc:
                log.write(f"\n[compile] error launching {engine}: {exc!r}\n")
                return "error", engine, None
            log.write(f"[compile] exit {proc.returncode}\n")
            if proc.returncode != 0:
                return "failed", engine, (pdf_path if pdf_path.is_file() else None)
    if pdf_path.is_file():
        return "compiled", engine, pdf_path
    return "failed", engine, None


# Shared LaTeX preamble for the combined report. It is a superset of the per-bug
# template preamble in prompts/writeup_bug.md: it provides the bugpython listing
# style and booktabs/array used by the per-bug bodies, plus enumitem for the
# run-level metadata and outcome tables and the bug-families list. The current
# per-bug template renders every section as plain prose/tables (no colored
# callouts), so the bugbannerbox/bugsummarybox/diagnosisbox/relatedbox tcolorbox
# environments below are retained only so older, reused per-bug bodies still
# compile when spliced in.
FINAL_REPORT_PREAMBLE = r"""\documentclass[11pt]{article}

\usepackage[margin=1in]{geometry}
\usepackage{amsmath, amssymb}
\usepackage{xcolor}
\usepackage[most]{tcolorbox}
\usepackage{listings}
\usepackage{hyperref}
\usepackage{array}
\usepackage{booktabs}
\usepackage{enumitem}
% Provides \FloatBarrier (used between the per-bug reports) and keeps floats from
% migrating across a section boundary.
\usepackage[section]{placeins}

\hypersetup{
    colorlinks=true,
    linkcolor=blue!60!black,
    urlcolor=blue!60!black,
    citecolor=blue!60!black
}

\lstdefinestyle{bugpython}{
  language=Python,
  basicstyle=\ttfamily\small,
  keywordstyle=\color{blue!60!black},
  stringstyle=\color{green!40!black},
  commentstyle=\color{gray!70!black},
  showstringspaces=false,
  breaklines=true,
  frame=single,
  rulecolor=\color{gray!30},
  columns=fullflexible,
  keepspaces=true
}

% Display heading with extra post-title space for per-bug sections that are
% immediately followed by code/listing blocks.
\newcommand{\bugblockheading}[1]{%
  \par\addvspace{1.1ex plus 0.4ex minus 0.2ex}%
  \noindent{\normalfont\normalsize\bfseries #1}\par\nobreak%
  \vspace{0.5\baselineskip}%
}

\newtcolorbox{bugbannerbox}{
  enhanced,
  colback=yellow!7,
  colframe=orange!75!black,
  title={\textbf{Bug Summary}},
  fonttitle=\bfseries,
  arc=2mm,
  boxrule=0.9pt,
  left=4mm,
  right=4mm,
  top=3mm,
  bottom=3mm
}

\newtcolorbox{bugsummarybox}{
  colback=red!3,
  colframe=red!45!black,
  title=\textbf{Bug Summary},
  fonttitle=\bfseries,
  arc=2mm,
  boxrule=0.7pt
}

\newtcolorbox{relatedbox}{
  colback=gray!4,
  colframe=gray!55!black,
  title=\textbf{Related Issues Assessment},
  fonttitle=\bfseries,
  arc=2mm,
  boxrule=0.7pt
}

\newtcolorbox{diagnosisbox}{
  colback=blue!3,
  colframe=blue!45!black,
  title=\textbf{Source-Level Diagnosis},
  fonttitle=\bfseries,
  arc=2mm,
  boxrule=0.7pt
}
"""


def latex_escape(text: str) -> str:
    """Escape LaTeX special characters in a plain string (e.g. metadata values)."""
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def extract_tex_body(text: str) -> str:
    """Return the document body of a standalone per-bug .tex, ready to splice.

    Keeps everything between \\begin{document} and \\end{document} and drops the
    title machinery so the body starts at its \\section{Bug ...} heading.
    """
    match = re.search(r"\\begin\{document\}(.*?)\\end\{document\}", text, re.DOTALL)
    body = match.group(1) if match else text
    body = re.sub(r"\\maketitle", "", body)
    body = re.sub(r"\\title\{.*?\}", "", body, flags=re.DOTALL)
    body = re.sub(r"\\date\{.*?\}", "", body, flags=re.DOTALL)
    return body.strip()


def derive_bug_outcomes(summary: dict) -> dict:
    """Return the bug_outcomes meta-summary, reconstructing it from the flat
    counts when a summary predates the bug_outcomes block (e.g. an older run used
    as a write-up fixture). Also accepts the pre-rename
    `bugs_confidently_not_duplicates` key."""
    existing = summary.get("bug_outcomes")
    if isinstance(existing, dict) and existing:
        out = dict(existing)
        # Migrate the older `no_public_duplicate_found` novelty key to the
        # canonical `completely_novel` if a run recorded the previous name.
        novelty = dict(existing.get("artifacted_by_novelty", {}))
        if "completely_novel" not in novelty and "no_public_duplicate_found" in novelty:
            novelty["completely_novel"] = novelty.pop("no_public_duplicate_found")
        out["artifacted_by_novelty"] = novelty
        # Migrate the older `candidates_total` key to `candidates_resolved`.
        if "candidates_resolved" not in out and "candidates_total" in out:
            out["candidates_resolved"] = out.pop("candidates_total")
        return out
    artifacted = summary.get("bugs_total_artifacted") or 0
    dupes = summary.get("candidates_rejected_as_duplicates") or 0
    false_positives = summary.get("candidates_rejected_as_false_positives") or 0
    # Accept the two pre-bug_outcomes flat names for this count.
    novel = summary.get("bugs_no_public_duplicate_found")
    if novel is None:
        novel = summary.get("bugs_confidently_not_duplicates")
    return {
        "candidates_resolved": artifacted + dupes + false_positives,
        "artifacted": artifacted,
        "discarded_total": dupes + false_positives,
        "discarded_by_reason": {
            "rejected_as_duplicate": dupes,
            "rejected_as_false_positive": false_positives,
        },
        "artifacted_by_novelty": {
            "completely_novel": novel,
            "family_known_specific_new": summary.get("bugs_family_known_specific_new"),
            "unclear_duplicate_status": summary.get("bugs_unclear_duplicate_status"),
        },
    }


# Human-readable labels for the dedup agent's raw verdict strings, so the same
# wording is used everywhere a verdict is shown. The labels deliberately avoid a
# novelty "ladder": both new-finding verdicts read as new, unreported witnesses,
# differing only on whether the failure mode itself was already documented.
DEDUP_VERDICT_LABELS = {
    "novel": "new failure mode with no public precedent",
    "family_known_specific_new": "new instance of a known failure mode",
    "likely_duplicate": "likely duplicate",
    "unclear": "duplicate status undetermined",
}


def dedup_verdict_label(verdict: str) -> str:
    key = (verdict or "").strip()
    return DEDUP_VERDICT_LABELS.get(key, key)


def _python_version_token(raw: object) -> str:
    text = str(raw or "").strip()
    return text.split()[0] if text else ""


def render_version_anchor(summary: dict) -> str:
    """A one-sentence version anchor for community-facing fragments.

    The main paper and the technical-report header anchor on the SymPy and Python
    versions as inline prose rather than a wall-clock run-metadata table: the
    timestamps and configured limits are operational provenance with no value to
    a reader and, for a curated multi-run bug set, no single true value."""
    version = latex_escape(str(summary.get("sympy_version") or "unknown"))
    python = _python_version_token(summary.get("python_version"))
    python_tex = f" under CPython~{latex_escape(str(python))}" if python else ""
    return (
        f"All findings below were confirmed against \\SymPy{{}}~{version}{python_tex}. "
        "Each is a silent correctness failure---a definite, well-formed answer that "
        "is mathematically wrong---witnessed by an independent oracle (a "
        "substitution residual, a differentiation check, a high-precision numerical "
        "evaluation, or a definition-level comparison) on a minimal input."
    )


def render_bug_outcomes_table(summary: dict, caption: str, *, detailed: bool) -> str:
    """A bug-outcomes `table` (no surrounding heading).

    detailed=False gives the two-row confirmed/discarded summary; detailed=True
    adds the by-reason discard split and the novelty breakdown."""
    outcomes = derive_bug_outcomes(summary)
    discarded = outcomes.get("discarded_by_reason", {}) or {}
    novelty = outcomes.get("artifacted_by_novelty", {}) or {}

    def count(value: object) -> int:
        return int(value or 0)

    lines = [
        "\\begin{table}[h]",
        "\\centering",
        "\\begin{tabular}{@{}p{0.55\\linewidth}r@{}}",
        "\\toprule",
        "\\textbf{Outcome} & \\textbf{Count} \\\\",
        "\\midrule",
    ]
    if detailed:
        resolved = outcomes.get("candidates_resolved")
        if resolved is not None:
            lines.append(f"Candidates resolved & {count(resolved)} \\\\")
        lines += [
            f"Confirmed bugs with artifacts & {count(outcomes.get('artifacted'))} \\\\",
            f"Rejected as false positive & {count(discarded.get('rejected_as_false_positive'))} \\\\",
            f"Rejected as duplicate & {count(discarded.get('rejected_as_duplicate'))} \\\\",
            "\\midrule",
            f"New instance of a known failure mode & {count(novelty.get('family_known_specific_new'))} \\\\",
            f"New failure mode (no public precedent) & {count(novelty.get('completely_novel'))} \\\\",
            f"Duplicate status undetermined & {count(novelty.get('unclear_duplicate_status'))} \\\\",
        ]
    else:
        lines += [
            f"Confirmed bugs with artifacts & {count(outcomes.get('artifacted'))} \\\\",
            f"Discarded bugs & {count(outcomes.get('discarded_total'))} \\\\",
        ]
    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        f"\\caption{{{latex_escape(caption)}}}",
        "\\end{table}",
    ]
    return "\n".join(lines)


def demote_headings_twice(body: str) -> str:
    """Demote a standalone per-bug body by two levels for the technical-report
    appendix: \\section{Bug N} becomes \\subsubsection and its \\subsection{...}
    parts become \\paragraph, so each bug sits under
    \\subsection{Detailed Per-Bug Reports}. Demote subsection first so the bug
    heading is not double-demoted."""
    spaced_headings = (
        "Minimal Reproducer",
        "Observed Behavior",
        "Proposed SymPy Regression Test",
    )
    for heading in spaced_headings:
        body = body.replace(
            f"\\subsection{{{heading}}}",
            f"\\bugblockheading{{{heading}}}",
        )
    body = re.sub(r"\\subsection\b", r"\\paragraph", body)
    body = re.sub(r"\\section\b", r"\\subsubsection", body)
    return body


def build_technical_report_fragment(summary: dict, bug_bodies: list[str]) -> str:
    """Audit-ready maintainer report as a LaTeX *fragment* (no preamble).

    It sits under the paper's `\\section{Technical Report}` (or the standalone
    wrapper's). Structure: a version-anchored scope line, Bug Outcomes, then the
    detailed per-bug reports spliced in verbatim and demoted two heading levels.
    Exact run provenance (timestamps, configured limits) lives per bug in the
    detailed reports, not in a single global run table that a curated multi-run
    bug set could not honestly fill."""
    parts = [
        "\\subsection{Scope}",
        "",
        render_version_anchor(summary),
        "",
        "\\subsection{Bug Outcomes}",
        "",
        render_bug_outcomes_table(summary, "Aggregate outcomes.", detailed=True),
        # Flush the metadata/outcomes tables so they cannot float down into the
        # first per-bug report.
        "\\FloatBarrier",
        "",
        "\\subsection{Detailed Per-Bug Reports}",
        "",
    ]
    if bug_bodies:
        for index, body in enumerate(bug_bodies):
            if index:
                parts.append("\\clearpage")
            parts.extend([demote_headings_twice(body.strip()), ""])
    else:
        parts.append("No confirmed bug artifacts were produced in this run.\n")
    return "\n".join(parts) + "\n"


def build_standalone_technical_report(summary: dict, fragment: str) -> str:
    """Wrap the technical-report fragment as a complete, compilable document.

    This is the standalone `technical_report.tex`: a maintainer/audit bundle using
    the same detailed per-bug content as the paper's technical appendix."""
    version = latex_escape(str(summary.get("sympy_version") or "unknown"))
    parts = [
        FINAL_REPORT_PREAMBLE,
        f"\\title{{SymPy Correctness Bug Report --- Technical Report (Version {version})}}",
        "\\author{}",
        "\\date{}",
        "",
        "\\begin{document}",
        "\\maketitle",
        "",
        "\\begin{abstract}",
        "This is the maintainer-facing technical report for the SymPy "
        "bug-discovery harness. It anchors on the SymPy and Python versions and "
        "the aggregate outcomes, then gives a detailed, self-contained report for "
        "each confirmed bug, including reproducers, observed and expected behavior, "
        "source-level diagnosis, and a proposed regression test. The companion "
        "paper presents the same findings as a compact counterexample atlas.",
        "\\end{abstract}",
        "",
        "\\tableofcontents",
        "\\newpage",
        "",
        "\\section{Technical Report for One Harness Run}",
        "",
        fragment.strip(),
        "",
        "\\end{document}",
    ]
    return "\n".join(parts) + "\n"


def run_writeup_agent(
    args: argparse.Namespace,
    run_root: Path,
    summary: dict,
    *,
    reuse_bug_reports: bool = False,
) -> dict:
    report_root = run_root / "final-report"
    bugs_dir = report_root / "bugs"
    for directory in (report_root, bugs_dir):
        directory.mkdir(parents=True, exist_ok=True)
    # Deliverables live under final-report/; all intermediate work (codex logs,
    # captured last messages, agent scratch) lives under _work/writeup/.
    work_dir = run_root / "_work" / "writeup"
    log_dir = work_dir / "logs"
    output_dir = work_dir / "messages"
    scratch_dir = work_dir / "scratch"
    scratch_dir.mkdir(parents=True, exist_ok=True)

    # writeup_status.json is an intermediate phase-completion marker, not a
    # maintainer-facing deliverable, so it lives under _work/writeup/.
    report_status_path = work_dir / "writeup_status.json"
    # The sole deliverable is the standalone, maintainer-facing technical report.
    report_tex_path = report_root / args.writeup_report_name

    accepted = summary.get("bug_artifacts", [])

    # Resolve the LaTeX engine once so every write-up agent can compile-and-fix its
    # own document (per-bug reports and the paper) until it is clean.
    latex_engine, latex_exe = resolve_latex_engine(args.latex_engine)
    latex_available = bool(latex_engine and latex_exe)

    result: dict[str, object] = {
        "tex_path": display_path(report_tex_path, run_root),
        "status_path": display_path(report_status_path, run_root),
        "bugs_dir": display_path(bugs_dir, run_root),
        "bug_count": len(accepted),
        "reuse_bug_reports": reuse_bug_reports,
        "latex_engine": latex_engine or "none",
    }

    # Phase 1: for each confirmed artifact, a dedicated folder under
    # final-report/bugs/<name>/ holding two deliverables: a compact paper-style
    # bug card (bug-card.tex) and the full detailed analysis (detailed-analysis.tex).
    # The detailed analyses are the maintainer-ready material spliced into the
    # technical report. With reuse_bug_reports the per-bug agents are skipped and
    # the existing files under final-report/bugs/<name>/ are taken as-is.
    bug_entries: list[dict] = []
    bug_texs: list[Path] = []
    for index, bug in enumerate(accepted, start=1):
        artifact_dir_rel = str(bug.get("artifact_dir", "") or "")
        bug_folder = run_root / artifact_dir_rel if artifact_dir_rel else run_root
        name = Path(artifact_dir_rel).name if artifact_dir_rel else f"bug-{index:03d}"
        bug_out_dir = bugs_dir / name
        bug_out_dir.mkdir(parents=True, exist_ok=True)
        detailed_tex = bug_out_dir / "detailed-analysis.tex"
        card_tex = bug_out_dir / "bug-card.tex"
        entry: dict[str, object] = {
            "bug_id": index,
            "name": name,
            "title": bug.get("title", ""),
            "artifact_dir": artifact_dir_rel,
            "dir": display_path(bug_out_dir, run_root),
            "detailed_tex_path": display_path(detailed_tex, run_root),
            "card_tex_path": display_path(card_tex, run_root),
        }
        if reuse_bug_reports:
            entry["source"] = "reused"
            if not args.dry_run:
                errors = validate_bug_tex(detailed_tex) + validate_bug_card(card_tex)
                entry["validation"] = "passed" if not errors else "failed"
                if errors:
                    entry["validation_errors"] = errors
        else:
            bug_scratch = scratch_dir / name
            bug_scratch.mkdir(parents=True, exist_ok=True)
            detailed_compile_dir = bug_scratch / "latex"
            card_compile_dir = bug_scratch / "latex-card"
            detailed_compile_dir.mkdir(parents=True, exist_ok=True)
            card_compile_dir.mkdir(parents=True, exist_ok=True)
            bug_prompt = build_writeup_bug_prompt(
                bug_folder,
                index,
                str(bug.get("title", "")),
                detailed_tex,
                card_tex,
                name,
                bug_scratch,
                build_latex_compile_section(
                    latex_engine,
                    latex_exe,
                    detailed_tex,
                    detailed_compile_dir,
                    doc_label="the detailed analysis (detailed-analysis.tex)",
                ),
                build_latex_compile_section(
                    latex_engine,
                    latex_exe,
                    card_tex,
                    card_compile_dir,
                    doc_label="the bug card (bug-card.tex)",
                ),
                args.artifact_repo_url,
            )
            bug_rc = run_codex(
                args,
                prompt=bug_prompt,
                workdir=run_root,
                output_path=output_dir / f"{name}.txt",
                log_path=log_dir / f"writeup_bug_{index:03d}.log",
                phase="writeup_bug",
            )
            entry["source"] = "generated"
            entry["exit"] = bug_rc
            if not args.dry_run:
                errors = validate_bug_tex(detailed_tex) + validate_bug_card(card_tex)
                entry["validation"] = (
                    "passed" if bug_rc == 0 and not errors else "failed"
                )
                if errors:
                    entry["validation_errors"] = errors
        bug_entries.append(entry)
        bug_texs.append(detailed_tex)
    result["per_bug"] = bug_entries

    if args.dry_run:
        status = {
            "status": "dry_run",
            "tex_path": display_path(report_tex_path, run_root),
            "notes": "per-bug write-up agent commands were recorded but not executed",
        }
        write_text(report_status_path, json.dumps(status, indent=2, sort_keys=True) + "\n")
        result["writeup_status"] = "dry_run"
        result["writeup_validation"] = "skipped"
        return result

    # Phase 2: extract each per-bug body for the technical report. A body that
    # still carries its document wrapper cannot be spliced, so it is dropped.
    bug_bodies: list[str] = []
    for entry, bug_tex in zip(bug_entries, bug_texs):
        if not bug_tex.is_file():
            entry["validation"] = "missing"
            continue
        body = extract_tex_body(read_text(bug_tex))
        if "\\documentclass" in body or "\\begin{document}" in body:
            entry["validation"] = "failed"
            entry.setdefault("validation_errors", []).append(
                "could not extract a clean document body; excluded from technical report"
            )
            continue
        bug_bodies.append(body)
    result["bug_reports"] = len(bug_bodies)

    # Phase 3: assemble the standalone technical report from the per-bug bodies.
    write_text(
        report_tex_path,
        build_standalone_technical_report(
            summary, build_technical_report_fragment(summary, bug_bodies)
        ),
    )

    # Phase 4: a finalize agent compiles the standalone technical report and fixes
    # every LaTeX error/warning until clean (the same compile-and-fix loop, up to
    # ~6 passes before stopping on a benign warning). Runs only when an engine
    # exists.
    if latex_available:
        tech_finalize_scratch = work_dir / "finalize_technical_report"
        tech_compile_dir = tech_finalize_scratch / "latex"
        tech_compile_dir.mkdir(parents=True, exist_ok=True)
        tech_finalize_status_path = work_dir / "finalize_technical_report_status.json"
        tech_finalize_rc = run_codex(
            args,
            prompt=build_writeup_finalize_prompt(
                report_tex_path,
                tech_finalize_status_path,
                tech_finalize_scratch,
                build_latex_compile_section(
                    latex_engine,
                    latex_exe,
                    report_tex_path,
                    tech_compile_dir,
                    doc_label="the standalone technical report (technical_report.tex)",
                ),
            ),
            workdir=run_root,
            output_path=output_dir / "finalize_technical_report.txt",
            log_path=log_dir / "writeup_finalize_technical_report.log",
            phase="writeup_finalize",
        )
        result["technical_report_finalize_exit"] = tech_finalize_rc
        result["technical_report_finalize_status"] = read_json_if_present(
            tech_finalize_status_path
        ).get("status", "unknown")
    else:
        result["technical_report_finalize_status"] = "skipped_no_engine"

    # Phase 5: validate the deliverable. technical_report.tex must be a complete
    # document with the expected top-level structure.
    validation_errors: list[str] = []
    validation_errors += validate_standalone_tex(
        report_tex_path,
        label="technical_report.tex",
        required_headings=("\\subsection{Scope}", "\\subsection{Bug Outcomes}"),
    )

    status = {
        "status": "report_created",
        "tex_path": display_path(report_tex_path, run_root),
        "bug_reports": len(bug_bodies),
        "notes": (
            f"technical report assembled from {len(bug_bodies)} per-bug report(s)"
        ),
    }
    write_text(report_status_path, json.dumps(status, indent=2, sort_keys=True) + "\n")
    result["writeup_status"] = "report_created"
    result["writeup_validation"] = "passed" if not validation_errors else "failed"
    if validation_errors:
        result["writeup_validation_errors"] = validation_errors

    # Phase 6: compile the standalone technical report to PDF when an engine is
    # available.
    if args.skip_pdf:
        result["pdf_status"] = "skipped"
    else:
        compile_log = log_dir / "technical_report_compile.log"
        # Compile into a work-space dir so the engine's .aux/.log byproducts stay
        # out of the deliverable directory; only the resulting PDF is copied back
        # into final-report/ alongside the .tex.
        compile_outdir = work_dir / "compile"
        pdf_status, engine, pdf_path = compile_tex_to_pdf(
            report_tex_path,
            args.latex_engine,
            compile_log,
            outdir=compile_outdir,
        )
        if pdf_path is not None and pdf_path.is_file():
            deliverable_pdf = report_root / pdf_path.name
            shutil.copy2(pdf_path, deliverable_pdf)
            pdf_path = deliverable_pdf
        result["pdf_status"] = pdf_status
        result["pdf_engine"] = engine
        result["pdf_compile_log"] = display_path(compile_log, run_root)
        if pdf_path is not None:
            result["pdf_path"] = display_path(pdf_path, run_root)

    # Phase 7: record the deliverable paths on the write-up result so they land in
    # run.json under "writeup" (no separate manifest file).
    result["deliverables"] = {
        "technical_report_tex": display_path(report_tex_path, run_root),
        "technical_report_pdf": result.get("pdf_path"),
        "per_bug_dir": [
            display_path(bugs_dir / e["name"], run_root) for e in bug_entries
        ],
        "per_bug_detailed_tex": [
            display_path(t, run_root) for t in bug_texs if t.is_file()
        ],
        "per_bug_card_tex": [
            display_path(bugs_dir / e["name"] / "bug-card.tex", run_root)
            for e in bug_entries
            if (bugs_dir / e["name"] / "bug-card.tex").is_file()
        ],
    }
    return result


# Codex window labels keyed by the rollout's primary/secondary fields. The
# nominal minutes match what Codex reports (300 = 5h, 10080 = 1 week).
_RATE_LIMIT_WINDOWS = (
    ("primary", "5-hour", 300),
    ("secondary", "weekly", 10080),
)


def build_subscription_usage(
    records: list[dict], baseline: dict | None
) -> dict | None:
    """Summarise how much of the Codex *subscription* plan this run consumed.

    Reads Codex's own rate-limit telemetry (captured per call from the session
    rollouts): for each window we report the standing usage after the run and,
    when a same-window reference reading exists, how many percentage points this
    run added. Preference order for the reference reading:

      1. the pre-run baseline (``final - baseline``) -> the run's full cost, or
      2. the first captured call (``final - first``) -> excludes the first
         call's own usage, so it is a slight underestimate (flagged as such).

    Returns None when no rate-limit telemetry was captured (e.g. an API-key
    login, which has no subscription window).
    """
    snaps = [r["rate_limit"] for r in records if isinstance(r.get("rate_limit"), dict)]
    if not snaps:
        return None
    first, final = snaps[0], snaps[-1]
    plan = final.get("plan_type") or first.get("plan_type")
    windows: dict[str, dict] = {}
    for key, label, nominal in _RATE_LIMIT_WINDOWS:
        fw = final.get(key)
        if not isinstance(fw, dict) or "used_percent" not in fw:
            continue
        entry: dict[str, object] = {
            "window_minutes": fw.get("window_minutes", nominal),
            "final_used_percent": round(float(fw["used_percent"]), 3),
            "resets_at": fw.get("resets_at"),
        }
        resets = fw.get("resets_at")
        consumed = None
        basis = None
        base_w = (baseline or {}).get(key) if isinstance(baseline, dict) else None
        if (
            isinstance(base_w, dict)
            and "used_percent" in base_w
            and base_w.get("resets_at") == resets
        ):
            consumed = float(fw["used_percent"]) - float(base_w["used_percent"])
            basis = "pre_run_baseline"
        else:
            in_w = first.get(key)
            if (
                isinstance(in_w, dict)
                and "used_percent" in in_w
                and in_w.get("resets_at") == resets
            ):
                consumed = float(fw["used_percent"]) - float(in_w["used_percent"])
                basis = "within_run_excludes_first_call"
        if consumed is not None:
            entry["consumed_percent"] = round(max(0.0, consumed), 3)
            entry["consumed_basis"] = basis
        windows[label] = entry
    if not windows:
        return None
    return {
        "plan_type": plan,
        "windows": windows,
        "note": (
            "Read from Codex's own rate-limit telemetry in the session rollouts "
            "(the rolling-window % cap your subscription actually enforces). "
            "'consumed_percent' is how much of that window this run used; "
            "'final_used_percent' is the standing total after the run. Because "
            "subscription caps are account-wide, concurrent Codex activity outside "
            "this harness can still move these percentages."
        ),
    }


def build_usage_summary(
    records: list[dict],
    *,
    bugs_artifacted: int,
    price_input: float | None,
    price_cached: float | None,
    price_output: float | None,
    price_basis: str = DEFAULT_PRICE_BASIS,
    rate_limit_baseline: dict | None = None,
) -> dict:
    """Aggregate per-call Codex token usage into the run-level token_usage block.

    Totals and a per-phase breakdown are always produced; per-bug averages are
    added only when there is at least one artifacted bug. A dollar cost estimate
    is computed whenever input and output prices are available (they default to
    the published API list rate, so cost is reported by default). output_tokens
    already includes hidden reasoning tokens, so cost never double-counts them.
    """
    countable = (*USAGE_FIELDS, "fresh_input_tokens")

    def blank() -> dict:
        return {field: 0 for field in countable}

    totals = blank()
    by_phase: dict[str, dict] = {}
    calls_with_usage = 0
    for rec in records:
        phase = str(rec.get("phase", "unknown"))
        bucket = by_phase.setdefault(
            phase, {**blank(), "calls": 0, "calls_with_usage": 0}
        )
        bucket["calls"] += 1
        has_usage = rec.get("source") in ("rollout", "log_text")
        if has_usage:
            calls_with_usage += 1
            bucket["calls_with_usage"] += 1
        for field in countable:
            value = int(rec.get(field, 0) or 0)
            totals[field] += value
            bucket[field] += value

    summary: dict[str, object] = {
        "calls": len(records),
        "calls_with_usage": calls_with_usage,
        "calls_without_usage": len(records) - calls_with_usage,
        "totals": totals,
        "by_phase": by_phase,
        "bugs_artifacted": bugs_artifacted,
        "prices_usd_per_million": {
            "input": price_input,
            "cached_input": price_cached,
            "output": price_output,
            "basis": price_basis,
        },
        "source_note": (
            "Per-call usage read from Codex session rollout files "
            "($CODEX_HOME/sessions); output_tokens includes reasoning tokens; "
            "fresh_input_tokens = input_tokens - cached_input_tokens. Cost is an "
            f"imputed pay-as-you-go figure at the {price_basis}; it is NOT what a "
            "ChatGPT/Codex subscription actually charges (a subscription is a flat "
            "fee that does not bill per token)."
        ),
    }

    subscription = build_subscription_usage(records, rate_limit_baseline)
    if subscription:
        summary["subscription"] = subscription

    if bugs_artifacted > 0:
        summary["per_bug"] = {
            field: round(totals[field] / bugs_artifacted, 1)
            for field in (
                "input_tokens",
                "cached_input_tokens",
                "fresh_input_tokens",
                "output_tokens",
                "total_tokens",
            )
        }

    if price_input is not None and price_output is not None:
        cached_price = price_cached if price_cached is not None else price_input
        cost_input = totals["fresh_input_tokens"] / 1_000_000 * price_input
        cost_cached = totals["cached_input_tokens"] / 1_000_000 * cached_price
        cost_output = totals["output_tokens"] / 1_000_000 * price_output
        cost_total = cost_input + cost_cached + cost_output
        cost: dict[str, object] = {
            "input_usd": round(cost_input, 4),
            "cached_input_usd": round(cost_cached, 4),
            "output_usd": round(cost_output, 4),
            "total_usd": round(cost_total, 4),
            "cached_priced_at_input_rate": price_cached is None,
            "basis": price_basis,
            "prices_usd_per_million": {
                "input": price_input,
                "cached_input": cached_price,
                "output": price_output,
            },
        }
        if bugs_artifacted > 0:
            cost["per_bug_usd"] = round(cost_total / bugs_artifacted, 4)
        summary["cost_usd"] = cost

    return summary


def render_token_usage_md(usage: dict) -> list[str]:
    """Markdown lines for the README Token Usage section (empty when absent)."""
    if not usage:
        return []
    totals = usage.get("totals", {})
    lines = [
        "## Token Usage & Cost",
        "",
        f"- model calls: {usage.get('calls', 0)} "
        f"(with usage captured: {usage.get('calls_with_usage', 0)}, "
        f"missing: {usage.get('calls_without_usage', 0)})",
        f"- input_tokens: {totals.get('input_tokens', 0):,} "
        f"(cached: {totals.get('cached_input_tokens', 0):,}, "
        f"fresh: {totals.get('fresh_input_tokens', 0):,})",
        f"- output_tokens (incl. reasoning): {totals.get('output_tokens', 0):,}",
        f"- total_tokens: {totals.get('total_tokens', 0):,}",
    ]
    per_bug = usage.get("per_bug")
    if per_bug:
        lines.extend(
            [
                "- per bug (artifacted):",
                f"  - input_tokens: {per_bug.get('input_tokens', 0):,.1f}",
                f"  - output_tokens: {per_bug.get('output_tokens', 0):,.1f}",
                f"  - total_tokens: {per_bug.get('total_tokens', 0):,.1f}",
            ]
        )
    cost = usage.get("cost_usd")
    if cost:
        lines.append(
            f"- imputed pay-as-you-go cost: ${cost.get('total_usd', 0):,.2f} "
            f"(input ${cost.get('input_usd', 0):,.2f} + cached "
            f"${cost.get('cached_input_usd', 0):,.2f} + output "
            f"${cost.get('output_usd', 0):,.2f})"
        )
        if "per_bug_usd" in cost:
            lines.append(f"- imputed cost per bug: ${cost['per_bug_usd']:,.4f}")
        prices = cost.get("prices_usd_per_million") or {}
        if prices:
            lines.append(
                "- conversion basis: {basis}, applied as "
                "${inp}/1M input, ${cached}/1M cached input, "
                "${out}/1M output tokens".format(
                    basis=cost.get("basis", "API list price"),
                    inp=prices.get("input"),
                    cached=prices.get("cached_input"),
                    out=prices.get("output"),
                )
            )
        if cost.get("cached_priced_at_input_rate"):
            lines.append(
                "  - note: cached input priced at the full input rate "
                "(--price-cached-input not set), so cost is an upper bound."
            )
        lines.append(
            "- caveat: this is an imputed pay-as-you-go (per-token) API cost. It "
            "is NOT the real amount you are charged on a ChatGPT/Codex "
            "subscription, which bills a flat recurring fee rather than per token. "
            "Treat the dollar figure as a relative API-equivalent estimate only."
        )
    by_phase = usage.get("by_phase", {})
    if by_phase:
        lines.extend(
            [
                "",
                "| Phase | Calls | Input | Cached | Output | Total |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for phase, bucket in by_phase.items():
            lines.append(
                "| {phase} | {calls} | {inp:,} | {cached:,} | {out:,} | {total:,} |".format(
                    phase=phase,
                    calls=bucket.get("calls", 0),
                    inp=bucket.get("input_tokens", 0),
                    cached=bucket.get("cached_input_tokens", 0),
                    out=bucket.get("output_tokens", 0),
                    total=bucket.get("total_tokens", 0),
                )
            )
    lines.append("")
    return lines


def render_subscription_md(sub: dict) -> list[str]:
    """Markdown for the Codex subscription-usage section (empty when absent).

    This is the metric your ChatGPT/Codex subscription actually enforces -- a
    rolling-window percentage cap -- so it is more meaningful than the imputed
    API dollar figure when you are not paying per token.
    """
    if not sub:
        return []
    windows = sub.get("windows", {})
    if not windows:
        return []
    lines = ["## Codex Plan Usage (subscription)", ""]
    plan = sub.get("plan_type")
    if plan:
        lines.append(f"- plan: {plan}")
    for label in ("weekly", "5-hour"):  # weekly first: the headline metric
        window = windows.get(label)
        if not window:
            continue
        resets_str = ""
        resets = window.get("resets_at")
        if isinstance(resets, (int, float)) and not isinstance(resets, bool):
            try:
                resets_str = " (window resets {})".format(
                    dt.datetime.fromtimestamp(int(resets), dt.timezone.utc).strftime(
                        "%Y-%m-%d %H:%MZ"
                    )
                )
            except (OverflowError, OSError, ValueError):
                resets_str = ""
        consumed = window.get("consumed_percent")
        if consumed is not None:
            approx = (
                " (approx; excludes the first model call)"
                if window.get("consumed_basis") == "within_run_excludes_first_call"
                else ""
            )
            lines.append(
                f"- this run consumed ~{consumed:.2f}% of your {label} Codex "
                f"limit{approx}{resets_str}"
            )
        final = window.get("final_used_percent")
        if final is not None:
            lines.append(
                f"  - standing at {final:.2f}% of the {label} limit used after "
                "the run"
            )
    note = sub.get("note")
    if note:
        lines.append(f"- note: {note}")
    lines.append("")
    return lines


def write_run_summary(run_root: Path, summary: dict) -> None:
    # run.json is the single machine-readable record for the run; README.md is its
    # human-readable counterpart. Both are regenerated whenever this is called.
    write_text(run_root / "run.json", json.dumps(summary, indent=2, sort_keys=True) + "\n")
    outcomes = derive_bug_outcomes(summary)
    discarded = outcomes.get("discarded_by_reason", {})
    novelty = outcomes.get("artifacted_by_novelty", {})
    config = summary.get("run_config", {})
    lines = [
        "# CAS Bug Codex Run Report",
        "",
        f"- run_started_utc: {summary['run_started_utc']}",
        f"- run_stopped_utc: {summary['run_stopped_utc']}",
        f"- result_dir: {summary['result_dir']}",
        f"- sympy_checkout_path: {summary['sympy_checkout_path']}",
        f"- sympy_version: {summary.get('sympy_version')}",
        f"- sympy_commit: {summary.get('sympy_commit')}",
        f"- python_executable: {summary.get('python_executable')}",
        "- run_config (stopping limits the run was launched with):",
        f"  - max_bugs: {config.get('max_bugs', '')}",
        f"  - max_hours: {config.get('max_hours', '')}",
        f"  - max_empty_passes: {config.get('max_empty_passes', '')}",
        f"- stop_reason: {summary['stop_reason']}",
        f"- empty_passes_observed: {summary.get('empty_passes_observed', '')}",
        "",
        "## Bug Outcomes",
        "",
        f"- candidates_resolved: {outcomes.get('candidates_resolved', '')}",
        f"- artifacted: {outcomes.get('artifacted', '')}",
        f"- discarded_total: {outcomes.get('discarded_total', '')}",
        f"  - rejected_as_duplicate: {discarded.get('rejected_as_duplicate', '')}",
        f"  - rejected_as_false_positive: {discarded.get('rejected_as_false_positive', '')}",
        "- artifacted_by_novelty:",
        f"  - completely_novel: {novelty.get('completely_novel', '')}",
        f"  - family_known_specific_new: {novelty.get('family_known_specific_new', '')}",
        f"  - unclear_duplicate_status: {novelty.get('unclear_duplicate_status', '')}",
        f"- root_causes_located: {summary.get('root_causes_located', 0)}",
        "",
    ]
    lines.extend(render_token_usage_md(summary.get("token_usage", {})))
    lines.extend(
        render_subscription_md(summary.get("token_usage", {}).get("subscription", {}))
    )
    lines.extend(
        [
            "## Bug Artifacts",
            "",
            "| Folder | Title | Subsystem | Dedup verdict | Hunter confidence |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    if summary["bug_artifacts"]:
        for bug in summary["bug_artifacts"]:
            lines.append(
                "| {folder} | {title} | {subsystem} | {dedup_verdict} | {confidence} |".format(
                    folder=bug.get("artifact_dir", ""),
                    title=bug.get("title", ""),
                    subsystem=bug.get("subsystem", ""),
                    dedup_verdict=dedup_verdict_label(bug.get("dedup_verdict", "")),
                    confidence=bug.get("hunter_confidence", ""),
                )
            )
    else:
        lines.append("| None | | | | |")
    lines.extend(
        [
            "",
            "## Discarded Candidates",
            "",
        ]
    )
    discarded_items = [
        item for item in summary["iterations"]
        if item.get("dedup_recommendation") == "reject_as_duplicate"
        or item.get("verify_recommendation") == "reject_as_false_positive"
    ]
    if discarded_items:
        for item in discarded_items:
            number = item.get("candidate_number")
            label = (
                f"Candidate {number:03d}"
                if isinstance(number, int)
                else f"Batch {item.get('batch_number', 0):03d}"
            )
            if item.get("verify_recommendation") == "reject_as_false_positive":
                reason = f"false positive (verify verdict: {item.get('verify_verdict', '')})"
            else:
                reason = f"duplicate ({dedup_verdict_label(item.get('dedup_verdict', ''))})"
            lines.append(f"- {label}: {item.get('title', '')} -- discarded as {reason}")
    else:
        lines.append("None.")

    writeup = summary.get("writeup", {})
    if writeup:
        lines.extend(
            [
                "",
                "## Final LaTeX Write-Up",
                "",
                f"- status: {writeup.get('writeup_status', '')}",
                f"- validation: {writeup.get('writeup_validation', '')}",
                f"- technical_report_tex_path: {writeup.get('tex_path', '')}",
                f"- technical_report_pdf_status: {writeup.get('pdf_status', '')}",
                f"- technical_report_finalize: {writeup.get('technical_report_finalize_status', '')}",
                f"- per_bug_reports: {writeup.get('bug_count', '')}",
                f"- bugs_dir: {writeup.get('bugs_dir', '')}",
                f"- latex_engine: {writeup.get('latex_engine', '')}",
                "",
            ]
        )
        if writeup.get("writeup_validation_errors"):
            lines.append("Validation errors:")
            for error in writeup["writeup_validation_errors"]:
                lines.append(f"- {error}")
            lines.append("")

    lines.extend(
        [
            "",
            "## Iterations",
            "",
        ]
    )
    for item in summary["iterations"]:
        number = item.get("candidate_number")
        header = (
            f"### Candidate {number:03d}"
            if isinstance(number, int)
            else f"### Batch {item.get('batch_number', 0):03d} (no candidates)"
        )
        lines.extend(
            [
                header,
                "",
                f"- status: {item.get('status')}",
                f"- title: {item.get('title', '')}",
                f"- dedup_verdict: {item.get('dedup_verdict', '')}",
                f"- dedup_recommendation: {item.get('dedup_recommendation', '')}",
                f"- artifact_status: {item.get('artifact_status', '')}",
                f"- artifact_dir: {item.get('artifact_dir', '')}",
                f"- directory: {item.get('candidate_dir', '')}",
                "",
            ]
        )
        if item.get("artifact_validation_errors"):
            lines.append("Artifact validation errors:")
            for error in item["artifact_validation_errors"]:
                lines.append(f"- {error}")
            lines.append("")

    lines.extend(
        [
            "## Commands Run",
            "",
        ]
    )
    commands = []
    for item in summary["iterations"]:
        commands.extend(item.get("commands_run", []))
    if commands:
        for command in commands:
            lines.append(f"- `{command}`")
    else:
        lines.append("See candidate log directories for Codex command transcripts.")

    lines.extend(
        [
            "",
            "## Remaining High-Value Areas",
            "",
            "Review candidate logs and continue exploring subsystems not covered by accepted artifacts.",
            "",
        ]
    )
    write_text(run_root / "README.md", "\n".join(lines))


def main() -> int:
    args = parse_args()
    report_name = Path(args.writeup_report_name)
    if report_name.is_absolute() or report_name.name != args.writeup_report_name:
        print(
            "--writeup-report-name must be a filename under final-report/, not a path.",
            file=sys.stderr,
        )
        return 2

    sympy_dir = args.sympy_dir.resolve()
    if not sympy_dir.exists():
        print(f"SymPy directory does not exist: {sympy_dir}", file=sys.stderr)
        return 2
    # Export the checkout as a real env var so agent-run scripts can pin the
    # version by reading SYMPY_CHECKOUT_PATH from the environment instead of
    # hardcoding a local absolute path into the artifacts they write.
    os.environ["SYMPY_CHECKOUT_PATH"] = str(sympy_dir)

    required_prompts = (
        SHARED_BUG_POLICY,
        HUNTER_PROMPT,
        VERIFY_PROMPT,
        DIAGNOSIS_PROMPT,
        DEDUP_PROMPT,
        ARTIFACT_PROMPT,
        WRITEUP_BUG_PROMPT,
        WRITEUP_FINALIZE_PROMPT,
    )
    for path in required_prompts:
        if not path.exists():
            print(f"Missing harness prompt: {path}", file=sys.stderr)
            return 2

    started = dt.datetime.now(dt.timezone.utc)
    metadata = collect_sympy_metadata(sympy_dir)
    if not metadata.get("sympy_imports_from_checkout"):
        print(
            "Warning: SymPy import probe did not resolve inside the supplied checkout.",
            file=sys.stderr,
        )
    stamp = started.strftime("%Y%m%d-%H%M%SZ")
    output_root = (args.output_root or Path.cwd()).resolve()
    version_token = filesystem_token(metadata.get("sympy_version"))
    run_root = output_root / f"cas-bug-results-{stamp}-sympy-{version_token}"
    candidates_root = run_root / "candidates"
    bug_report_root = run_root / "bug-report"
    # All non-reporting intermediates (handoff plans, codex logs, captured last
    # messages, per-agent scratchpads) live under _work/, kept out of the
    # reporting directories (candidates/, bug-report/, final-report/).
    work_root = run_root / "_work"
    run_root.mkdir(parents=True, exist_ok=True)
    candidates_root.mkdir(parents=True, exist_ok=True)
    bug_report_root.mkdir(parents=True, exist_ok=True)
    original_codex_home = default_codex_home()
    isolated_codex_home = Path(
        tempfile.mkdtemp(prefix=f"cas-bug-codex-{stamp}-codex-home-")
    )
    codex_home_info = prepare_isolated_codex_home(
        isolated_codex_home, original_codex_home
    )
    os.environ["CODEX_HOME"] = codex_home_info["path"]
    # Snapshot subscription rate-limit usage before any model call so the run's
    # own plan consumption can be measured as (final reading - this baseline).
    # With an isolated CODEX_HOME there is usually no prior rollout, so the
    # fallback is final-minus-first-call. Token rollouts themselves are isolated.
    capture_rate_limit_baseline()

    deadline = time.monotonic() + args.hours * 3600
    confirmed = existing_artifact_count(bug_report_root)
    start_confirmed = confirmed
    empty_passes = 0
    duplicate_candidates = 0
    false_positive_candidates = 0
    root_causes_located = 0
    bug_artifacts: list[dict] = []
    iterations: list[dict] = []
    stop_reason = "completed"

    print(f"[harness] sympy_dir={sympy_dir}")
    print(f"[harness] run_root={run_root}")
    print(f"[harness] CODEX_HOME={codex_home_info['path']} (isolated sessions)")
    print(f"[harness] pre_existing_artifacts={start_confirmed}")

    candidate_number = 1
    batch_number = 1
    while True:
        if confirmed - start_confirmed >= args.max_bugs:
            stop_reason = f"max bugs reached or exceeded ({args.max_bugs})"
            break
        if time.monotonic() >= deadline:
            stop_reason = f"time limit reached ({args.hours} hours)"
            break
        if empty_passes >= args.max_empty_passes:
            stop_reason = f"empty-pass limit reached ({args.max_empty_passes})"
            break

        batch_dir = work_root / f"batch-{batch_number:03d}"
        plans_dir = batch_dir / "plans"
        log_dir = batch_dir / "logs"
        output_dir = batch_dir / "messages"
        scratch_root = batch_dir / "scratch"
        plans_dir.mkdir(parents=True, exist_ok=True)
        candidate_batch_json = plans_dir / "candidate_batch.json"
        verify_batch_json = plans_dir / "verify_batch.json"
        diagnosis_batch_json = plans_dir / "diagnosis_batch.json"
        dedup_batch_json = plans_dir / "dedup_batch.json"
        artifact_batch_json = plans_dir / "artifact_batch.json"

        def agent_scratch(name: str) -> Path:
            path = scratch_root / name
            path.mkdir(parents=True, exist_ok=True)
            return path

        # Batch-level log entry for passes that yield no candidates. It carries no
        # candidate_number so that the per-candidate numbering stays contiguous
        # (empty/failed passes must not create gaps in candidate-NNN).
        batch_item: dict[str, object] = {
            "candidate_number": None,
            "candidate_dir": str(batch_dir.relative_to(run_root)),
            "batch_number": batch_number,
            "commands_run": [],
        }

        hunter_prompt = build_candidate_prompt(
            candidate_batch_json,
            sympy_dir,
            run_root,
            agent_scratch("hunter"),
            bug_report_root,
            candidates_root,
            metadata,
        )
        hunter_rc = run_codex(
            args,
            prompt=hunter_prompt,
            workdir=run_root,
            output_path=output_dir / "hunter_candidate.txt",
            log_path=log_dir / "hunter_candidate.log",
            phase="hunter",
        )
        batch_item["hunter_exit"] = hunter_rc

        if hunter_rc != 0:
            batch_item["status"] = "hunter_command_failed"
            iterations.append(batch_item)
            stop_reason = f"hunter command failed (exit {hunter_rc})"
            break

        if not candidate_batch_json.exists():
            batch_item["status"] = "candidate_batch_json_missing"
            iterations.append(batch_item)
            empty_passes += 1
            batch_number += 1
            continue

        try:
            hunter_batch = load_json(candidate_batch_json)
        except json.JSONDecodeError as exc:
            batch_item["status"] = "candidate_batch_json_invalid"
            batch_item["error"] = str(exc)
            iterations.append(batch_item)
            empty_passes += 1
            batch_number += 1
            continue

        batch_status, candidates, batch_commands = normalize_hunter_batch(hunter_batch)
        batch_item["status"] = batch_status
        batch_item["commands_run"] = batch_commands
        batch_item["candidates_in_batch"] = len(candidates)

        if not candidates:
            empty_passes += 1
            iterations.append(batch_item)
            batch_number += 1
            continue

        empty_passes = 0

        candidate_items: list[dict] = []
        dedup_entries: list[dict] = []
        verify_entries: list[dict] = []
        for index, candidate in enumerate(candidates, start=1):
            current_number = candidate_number
            candidate_dir = candidates_root / f"candidate-{current_number:03d}"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            candidate_json = candidate_dir / "candidate_minimized.json"
            verify_report = candidate_dir / "verify_report.md"
            root_cause_report = candidate_dir / "root_cause.md"
            dedup_report = candidate_dir / "dedup_report.md"
            artifact_status = candidate_dir / "artifact_status.json"
            candidate_payload = {**candidate, "status": "candidate"}
            write_text(
                candidate_json,
                json.dumps(candidate_payload, indent=2, sort_keys=True) + "\n",
            )

            item = candidate_iteration_item(
                candidate_number=current_number,
                candidate_dir=candidate_dir,
                run_root=run_root,
                batch_number=batch_number,
                hunter_rc=hunter_rc,
                candidate=candidate_payload,
            )
            item["batch_candidate_index"] = index
            candidate_items.append(item)
            dedup_entries.append(
                {
                    "candidate_number": current_number,
                    "candidate_json_path": str(candidate_json),
                    "dedup_report_path": str(dedup_report),
                    "diagnosis_report_path": str(root_cause_report),
                    "artifact_status_path": str(artifact_status),
                    "title": candidate_payload.get("title", ""),
                    "subsystem": candidate_payload.get("subsystem", ""),
                    "error_signature": candidate_payload.get("error_signature", ""),
                }
            )
            verify_entries.append(
                {
                    "candidate_number": current_number,
                    "candidate_json_path": str(candidate_json),
                    "verify_report_path": str(verify_report),
                    "title": candidate_payload.get("title", ""),
                    "subsystem": candidate_payload.get("subsystem", ""),
                    "error_signature": candidate_payload.get("error_signature", ""),
                }
            )
            candidate_number += 1

        # Independent verification phase (between hunting and dedup): re-run each
        # candidate's reproducer against the pinned checkout and drop false
        # positives before they can reach dedup and artifact generation. This is
        # the only correctness gate in the pipeline; dedup checks novelty only,
        # so this phase always runs.
        if verify_entries:
            item_by_number = {
                int(item["candidate_number"]): item for item in candidate_items
            }
            dedup_entry_by_number = {
                int(entry["candidate_number"]): entry for entry in dedup_entries
            }
            write_verify_batch(verify_batch_json, run_root, verify_entries)
            verify_prompt = build_verify_prompt(
                verify_batch_json,
                sympy_dir,
                run_root,
                agent_scratch("verify"),
                metadata,
            )
            verify_rc = run_codex(
                args,
                prompt=verify_prompt,
                workdir=run_root,
                output_path=output_dir / "verify_agent.txt",
                log_path=log_dir / "verify_agent.log",
                phase="verify",
            )
            for item in candidate_items:
                item["verify_exit"] = verify_rc

            if verify_rc != 0:
                for item in candidate_items:
                    item["verify_verdict"] = "command_failed"
                iterations.extend(candidate_items)
                stop_reason = f"verify command failed (exit {verify_rc})"
                break

            kept_candidate_items: list[dict] = []
            kept_dedup_entries: list[dict] = []
            for entry in verify_entries:
                number = int(entry["candidate_number"])
                item = item_by_number[number]
                report_path = Path(str(entry["verify_report_path"]))
                if not report_path.exists():
                    item["verify_verdict"] = "unclear"
                    item["verify_recommendation"] = "continue_but_mark_unclear"
                else:
                    verdict, confidence, recommendation = parse_verify_front_matter(
                        report_path
                    )
                    item["verify_verdict"] = verdict
                    item["verify_confidence"] = confidence
                    item["verify_recommendation"] = recommendation

                if item["verify_recommendation"] == "reject_as_false_positive":
                    false_positive_candidates += 1
                    item["artifact_status"] = "skipped_as_false_positive"
                    iterations.append(item)
                    continue

                kept_candidate_items.append(item)
                kept_dedup_entries.append(dedup_entry_by_number[number])

            candidate_items = kept_candidate_items
            dedup_entries = kept_dedup_entries

            if not dedup_entries:
                # Every candidate in this batch was refuted as a false positive.
                batch_number += 1
                continue

        # Source-level diagnosis phase (after verification, before dedup): read
        # the SymPy checkout to locate the code responsible for each verified bug
        # and write a root_cause.md per candidate. This is non-blocking and never
        # drops a candidate; a bug with an unlocated cause is still a real bug. It
        # always runs for any surviving candidates.
        if dedup_entries:
            diagnosis_entries = [
                {
                    "candidate_number": entry["candidate_number"],
                    "candidate_json_path": entry["candidate_json_path"],
                    "root_cause_path": entry["diagnosis_report_path"],
                    "title": entry.get("title", ""),
                    "subsystem": entry.get("subsystem", ""),
                }
                for entry in dedup_entries
            ]
            write_diagnosis_batch(diagnosis_batch_json, run_root, diagnosis_entries)
            diagnosis_prompt = build_diagnosis_prompt(
                diagnosis_batch_json,
                sympy_dir,
                run_root,
                agent_scratch("diagnosis"),
                metadata,
            )
            diagnosis_rc = run_codex(
                args,
                prompt=diagnosis_prompt,
                workdir=run_root,
                output_path=output_dir / "diagnosis_agent.txt",
                log_path=log_dir / "diagnosis_agent.log",
                phase="diagnosis",
            )
            diag_item_by_number = {
                int(item["candidate_number"]): item for item in candidate_items
            }
            for entry in diagnosis_entries:
                item = diag_item_by_number[int(entry["candidate_number"])]
                item["diagnosis_exit"] = diagnosis_rc
                report_path = Path(str(entry["root_cause_path"]))
                if diagnosis_rc == 0 and report_path.exists():
                    status, confidence, location = parse_diagnosis_front_matter(
                        report_path
                    )
                    item["diagnosis_status"] = status
                    item["diagnosis_confidence"] = confidence
                    item["diagnosis_location"] = location
                    if status == "located":
                        root_causes_located += 1
                elif diagnosis_rc != 0:
                    item["diagnosis_status"] = "command_failed"
                else:
                    item["diagnosis_status"] = "missing"

        write_candidate_batch_for_dedup(dedup_batch_json, run_root, dedup_entries)
        dedup_prompt = build_dedup_prompt(dedup_batch_json, agent_scratch("dedup"))
        dedup_rc = run_codex(
            args,
            prompt=dedup_prompt,
            workdir=run_root,
            output_path=output_dir / "dedup_agent.txt",
            log_path=log_dir / "dedup_agent.log",
            phase="dedup",
            enable_search=not args.no_dedup_search,
        )
        for item in candidate_items:
            item["dedup_exit"] = dedup_rc

        if dedup_rc != 0:
            for item in candidate_items:
                item["dedup_verdict"] = "command_failed"
            iterations.extend(candidate_items)
            stop_reason = f"dedup command failed (exit {dedup_rc})"
            break

        item_by_number = {
            int(item["candidate_number"]): item for item in candidate_items
        }
        artifact_plan_items: list[dict] = []
        for entry in dedup_entries:
            item = item_by_number[int(entry["candidate_number"])]
            dedup_report = Path(str(entry["dedup_report_path"]))
            if not dedup_report.exists():
                item["dedup_verdict"] = "unclear"
                item["dedup_recommendation"] = "continue_but_mark_unclear"
            else:
                verdict, confidence, recommendation = parse_dedup_front_matter(dedup_report)
                item["dedup_verdict"] = verdict
                item["dedup_confidence"] = confidence
                item["dedup_recommendation"] = recommendation

            if item["dedup_recommendation"] == "reject_as_duplicate":
                duplicate_candidates += 1
                item["artifact_status"] = "skipped_as_duplicate"
                continue

            planned_offset = len(artifact_plan_items) + 1
            bug_number = confirmed + planned_offset
            slug = slugify(str(item.get("title", f"candidate-{int(entry['candidate_number']):03d}")))
            artifact_dir_rel = f"bug-report/bug-{bug_number:03d}-{slug}"
            artifact_dir = run_root / artifact_dir_rel
            item["planned_artifact_dir"] = artifact_dir_rel
            artifact_plan_items.append(
                {
                    **entry,
                    "bug_number": bug_number,
                    "bug_number_padded": f"{bug_number:03d}",
                    "slug": slug,
                    "artifact_dir": str(artifact_dir),
                    "artifact_dir_relative": artifact_dir_rel,
                    "dedup_verdict": item.get("dedup_verdict", ""),
                    "dedup_recommendation": item.get("dedup_recommendation", ""),
                }
            )

        if not artifact_plan_items:
            iterations.extend(candidate_items)
            batch_number += 1
            continue

        write_artifact_batch_plan(
            artifact_batch_json,
            run_root,
            bug_report_root,
            artifact_plan_items,
        )
        artifact_prompt = build_artifact_prompt(
            artifact_batch_json,
            sympy_dir,
            run_root,
            agent_scratch("artifact"),
            metadata,
        )
        artifact_rc = run_codex(
            args,
            prompt=artifact_prompt,
            workdir=run_root,
            output_path=output_dir / "artifact_agent.txt",
            log_path=log_dir / "artifact_agent.log",
            phase="artifact",
        )
        accepted_numbers = {
            int(plan_item["candidate_number"]) for plan_item in artifact_plan_items
        }
        for item in candidate_items:
            if int(item["candidate_number"]) in accepted_numbers:
                item["artifact_exit"] = artifact_rc

        if artifact_rc != 0:
            for item in candidate_items:
                if int(item["candidate_number"]) in accepted_numbers:
                    item["artifact_status"] = "command_failed"
            iterations.extend(candidate_items)
            stop_reason = f"artifact command failed (exit {artifact_rc})"
            break

        validation_failed = False
        for plan_item in artifact_plan_items:
            item = item_by_number[int(plan_item["candidate_number"])]
            artifact_status = Path(str(plan_item["artifact_status_path"]))
            try:
                status = load_json(artifact_status) if artifact_status.exists() else {}
            except json.JSONDecodeError as exc:
                status = {"status": "artifact_status_invalid", "error": str(exc)}
            item["artifact_status"] = status.get("status")
            item["artifact_dir"] = status.get("artifact_dir", "")
            if status.get("status") == "artifact_created":
                finalize_artifact_bundle_metadata(
                    run_root,
                    status,
                    Path(str(plan_item["candidate_json_path"])),
                )
                ok, errors, artifact_dir = validate_artifact_bundle(
                    run_root,
                    bug_report_root,
                    status,
                )
                item["artifact_dir"] = artifact_dir or item["artifact_dir"]
                if ok:
                    confirmed += 1
                    artifact_path = run_root / artifact_dir
                    item["artifact_validation"] = "passed"
                    bug_artifacts.append(
                        {
                            "artifact_dir": artifact_dir,
                            "title": item.get("title", ""),
                            "subsystem": item.get("subsystem", ""),
                            "dedup_verdict": (
                                item.get("dedup_verdict", "")
                                or extract_dedup_verdict_from_artifact(artifact_path)
                                or "unclear"
                            ),
                            "hunter_confidence": item.get("confidence", ""),
                            **bug_artifact_deliverable_paths(run_root, artifact_dir),
                        }
                    )
                else:
                    item["artifact_status"] = "artifact_validation_failed"
                    item["artifact_validation_errors"] = errors
                    stop_reason = "artifact validation failed"
                    validation_failed = True
                    break

            elif not artifact_status.exists():
                item["artifact_status"] = "missing"

        iterations.extend(candidate_items)
        if validation_failed:
            break
        batch_number += 1

    stopped = dt.datetime.now(dt.timezone.utc)
    bugs_total_artifacted = confirmed - start_confirmed
    bugs_completely_novel = sum(
        1 for bug in bug_artifacts if bug.get("dedup_verdict") == "novel"
    )
    bugs_family_known_specific_new = sum(
        1
        for bug in bug_artifacts
        if bug.get("dedup_verdict") == "family_known_specific_new"
    )
    bugs_unclear_duplicate_status = sum(
        1 for bug in bug_artifacts if bug.get("dedup_verdict") == "unclear"
    )
    # Meta-summary of where every considered candidate ended up: artifacted as a
    # confirmed bug, or discarded for a specific reason. `completely_novel` means
    # dedup found no public relative at all; `family_known_specific_new` bugs are
    # still genuinely new instances, just within a publicly-known family.
    bug_outcomes = {
        # Candidates that reached a terminal verdict (artifacted or discarded for a
        # reason). Excludes any lost to command/validation errors, so it is not
        # necessarily every candidate the hunter ever produced.
        "candidates_resolved": (
            bugs_total_artifacted + duplicate_candidates + false_positive_candidates
        ),
        "artifacted": bugs_total_artifacted,
        "discarded_total": duplicate_candidates + false_positive_candidates,
        "discarded_by_reason": {
            "rejected_as_duplicate": duplicate_candidates,
            "rejected_as_false_positive": false_positive_candidates,
        },
        "artifacted_by_novelty": {
            "completely_novel": bugs_completely_novel,
            "family_known_specific_new": bugs_family_known_specific_new,
            "unclear_duplicate_status": bugs_unclear_duplicate_status,
        },
    }
    # Stopping limits the run was launched with (inputs, not results). Grouped so
    # they are not mistaken for counts of what the run actually found.
    run_config = {
        "max_bugs": args.max_bugs,
        "max_hours": args.hours,
        "max_empty_passes": args.max_empty_passes,
        "codex_home": codex_home_info,
    }
    run_metadata = {
        "run_started_utc": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "run_stopped_utc": stopped.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "result_dir": str(run_root),
        "sympy_checkout_path": str(sympy_dir),
        "sympy_version": metadata.get("sympy_version"),
        "sympy_file": metadata.get("sympy_file"),
        "sympy_imports_from_checkout": metadata.get("sympy_imports_from_checkout"),
        "sympy_commit": metadata.get("sympy_commit"),
        "python_executable": metadata.get("python_executable"),
        "python_version": metadata.get("python_version"),
        "run_config": run_config,
        "stop_reason": stop_reason,
        "bug_outcomes": bug_outcomes,
        "root_causes_located": root_causes_located,
    }
    summary = {
        **run_metadata,
        "pre_existing_artifacts": start_confirmed,
        "empty_passes_observed": empty_passes,
        "bug_artifacts": bug_artifacts,
        "rejected_duplicate_candidates": collect_rejected_duplicate_candidates(
            run_root, iterations
        ),
        "iterations": iterations,
    }

    def attach_token_usage() -> None:
        summary["token_usage"] = build_usage_summary(
            CODEX_USAGE_RECORDS,
            bugs_artifacted=bugs_total_artifacted,
            price_input=args.price_input,
            price_cached=args.price_cached_input,
            price_output=args.price_output,
            price_basis=args.price_basis,
            rate_limit_baseline=RATE_LIMIT_BASELINE,
        )

    attach_token_usage()
    write_run_summary(run_root, summary)

    print("[harness] starting final LaTeX write-up agent")
    summary["writeup"] = run_writeup_agent(args, run_root, summary)
    # Recompute so the write-up phase's token usage is included in the final
    # record.
    attach_token_usage()
    write_run_summary(run_root, summary)

    print(f"[harness] stop_reason={stop_reason}")
    print(f"[harness] run_report={run_root / 'README.md'}")
    print(f"[harness] run_json={run_root / 'run.json'}")
    writeup_info = summary.get("writeup", {})
    if writeup_info.get("tex_path"):
        print(f"[harness] technical_report={run_root / str(writeup_info['tex_path'])}")
    if writeup_info.get("pdf_path"):
        print(f"[harness] technical_report_pdf={run_root / str(writeup_info['pdf_path'])}")
    elif writeup_info.get("pdf_status") not in (None, "skipped"):
        print(
            f"[harness] technical report pdf not produced (status={writeup_info.get('pdf_status')}, "
            f"engine={writeup_info.get('pdf_engine') or 'none'}); "
            f"see {writeup_info.get('pdf_compile_log')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
