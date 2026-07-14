#!/usr/bin/env python3
"""Create a pinned SymPy checkout on Windows, macOS, or Linux."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence


def default_run_name() -> str:
    return dt.datetime.now().strftime("sympy-run-%Y%m%d-%H%M%S")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a reproducible SymPy target checkout for the GUI pipeline."
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path.home() / "sympy-bug-hunt",
        help="Parent directory for the clone, worktrees, and metadata.",
    )
    parser.add_argument("--repo-url", default="https://github.com/sympy/sympy.git")
    parser.add_argument("--ref", default="origin/master", help="Git ref to pin.")
    parser.add_argument("--run-name", default=default_run_name())
    parser.add_argument("--env-name", default="sympy-bug-hunt")
    parser.add_argument("--no-fetch", action="store_true")
    parser.add_argument("--no-worktree", action="store_true")
    parser.add_argument("--create-env", action="store_true")
    parser.add_argument("--install", action="store_true")
    parser.add_argument(
        "--no-conda",
        action="store_true",
        help="Skip Conda setup (this is already the default).",
    )
    parser.add_argument(
        "--output",
        choices=("env", "path", "json"),
        default="env",
        help="Final stdout format. Progress messages are written to stderr.",
    )
    return parser.parse_args()


def log(message: str) -> None:
    print(f"[setup] {message}", file=sys.stderr)


def git_command(*args: str) -> list[str]:
    return ["git", "-c", "core.longpaths=true", *args]


def run(command: Sequence[str], *, capture: bool = False) -> str:
    try:
        completed = subprocess.run(
            list(command),
            check=True,
            text=True,
            stdout=subprocess.PIPE if capture else sys.stderr,
            stderr=subprocess.PIPE if capture else sys.stderr,
        )
    except FileNotFoundError as exc:
        raise SystemExit(f"required executable not found: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        if detail:
            print(detail, file=sys.stderr)
        raise SystemExit(exc.returncode) from exc
    return completed.stdout.strip() if capture and completed.stdout else ""


def conda_env_exists(conda: str, env_name: str) -> bool:
    payload = json.loads(run([conda, "env", "list", "--json"], capture=True))
    wanted = env_name.casefold()
    return any(Path(path).name.casefold() == wanted for path in payload.get("envs", []))


def configure_conda(args: argparse.Namespace, target_dir: Path) -> None:
    requested = args.create_env or args.install
    if not requested or args.no_conda:
        return
    conda = shutil.which("conda")
    if conda is None:
        raise SystemExit("Conda setup was requested, but conda is not on PATH")
    if conda_env_exists(conda, args.env_name):
        log(f"using existing conda env {args.env_name}")
    else:
        log(f"creating conda env {args.env_name}")
        run([conda, "create", "-n", args.env_name, "python=3.12", "-y"])
    if not args.install:
        log("install skipped; pass --install to install SymPy and test dependencies")
        return
    log(f"installing target checkout into conda env {args.env_name}")
    prefix = [conda, "run", "-n", args.env_name, "python", "-m", "pip"]
    run([*prefix, "install", "-U", "pip"])
    run([*prefix, "install", "-e", f"{target_dir}[dev]"])
    run([*prefix, "install", "numpy", "scipy", "mpmath", "pytest", "hypothesis"])


def create_target(args: argparse.Namespace) -> dict[str, str]:
    if shutil.which("git") is None:
        raise SystemExit("Git is required but was not found on PATH")

    base_dir = args.base_dir.expanduser().resolve()
    clone_dir = base_dir / "sympy-main"
    runs_dir = base_dir / "runs"
    metadata_dir = base_dir / "metadata"
    runs_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    if not (clone_dir / ".git").is_dir():
        log(f"cloning SymPy into {clone_dir}")
        run(git_command("clone", args.repo_url, str(clone_dir)))
    else:
        log(f"using existing clone {clone_dir}")

    if not args.no_fetch:
        log("fetching latest refs")
        run(git_command("-C", str(clone_dir), "fetch", "--tags", "origin"))

    commit = run(
        git_command("-C", str(clone_dir), "rev-parse", args.ref),
        capture=True,
    )
    log(f"locked ref {args.ref} to commit {commit}")

    if args.no_worktree:
        target_dir = clone_dir
        log("using main clone as target")
        run(git_command("-C", str(target_dir), "checkout", "--detach", commit))
    else:
        target_dir = runs_dir / args.run_name
        if target_dir.exists():
            raise SystemExit(f"target worktree already exists: {target_dir}")
        log(f"creating worktree {target_dir}")
        run(
            git_command(
                "-C",
                str(clone_dir),
                "worktree",
                "add",
                "--detach",
                str(target_dir),
                commit,
            )
        )

    configure_conda(args, target_dir)

    metadata = {
        "target_dir": str(target_dir),
        "clone_dir": str(clone_dir),
        "repo_url": args.repo_url,
        "ref": args.ref,
        "commit": commit,
        "run_name": args.run_name,
        "env_name": args.env_name,
        "created_at_utc": dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
    }
    metadata_file = metadata_dir / f"{args.run_name}.json"
    metadata_file.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    metadata["metadata_file"] = str(metadata_file)
    log(f"metadata: {metadata_file}")
    return metadata


def main() -> int:
    args = parse_args()
    metadata = create_target(args)
    if args.output == "path":
        print(metadata["target_dir"])
    elif args.output == "json":
        print(json.dumps(metadata, indent=2, sort_keys=True))
    else:
        print(f"TARGET_DIR={metadata['target_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
