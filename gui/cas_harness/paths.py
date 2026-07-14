"""Path policy for run-generated files."""

from __future__ import annotations

from pathlib import Path, PurePosixPath, PureWindowsPath


class PathPolicyError(ValueError):
    """Raised when a path violates the run containment policy."""


RESERVED_OUTPUT_DIRS = ("_work", "candidates", "bug-report", "final-report")


def validate_report_filename(raw: str) -> str:
    posix = PurePosixPath(raw)
    windows = PureWindowsPath(raw)
    if (
        posix.is_absolute()
        or windows.is_absolute()
        or posix.name != raw
        or windows.name != raw
        or raw in {"", ".", ".."}
    ):
        raise PathPolicyError("report name must be a filename, not a path")
    if not raw.endswith(".tex"):
        raise PathPolicyError("report name must end with .tex")
    return raw


def resolve_run_root(raw: Path) -> Path:
    """Return canonical RUN_ROOT while accepting harmless path aliases."""
    if raw.is_symlink() and not raw.exists():
        raise PathPolicyError(f"RUN_ROOT symlink target is missing: {raw}")
    if raw.exists() and not raw.is_dir():
        raise PathPolicyError(f"RUN_ROOT must be a directory: {raw}")
    return raw.resolve(strict=False)


def reject_symlink_components(run_root: Path, path: Path) -> None:
    """Reject existing symlink components between RUN_ROOT and path."""
    root = run_root.resolve(strict=False)
    raw = path if path.is_absolute() else root / path
    resolved = raw.resolve(strict=False)
    try:
        rel = raw.relative_to(root)
    except ValueError:
        try:
            rel = resolved.relative_to(root)
        except ValueError as exc:
            raise PathPolicyError(f"path escapes RUN_ROOT: {path}") from exc
    cursor = root
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            target = cursor.resolve(strict=False)
            try:
                target.relative_to(root)
            except ValueError as exc:
                raise PathPolicyError(
                    f"symlinked output path component escapes RUN_ROOT: {cursor}"
                ) from exc
        if not cursor.exists():
            break


def ensure_reserved_output_dirs(run_root: Path) -> None:
    """Fail closed if a reserved output directory symlink escapes RUN_ROOT."""
    root = resolve_run_root(run_root)
    for name in RESERVED_OUTPUT_DIRS:
        path = root / name
        if path.is_symlink():
            target = path.resolve(strict=False)
            try:
                target.relative_to(root)
            except ValueError as exc:
                raise PathPolicyError(
                    f"reserved output directory symlink escapes RUN_ROOT: {path}"
                ) from exc


def safe_output_path(run_root: Path, path: Path) -> Path:
    """Return an absolute path under RUN_ROOT with no symlinked components."""
    root = resolve_run_root(run_root)
    raw = path if path.is_absolute() else root / path
    resolved = raw.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise PathPolicyError(f"path escapes RUN_ROOT after resolving symlinks: {path}") from exc
    reject_symlink_components(root, raw)
    return resolved


def safe_run_path(run_root: Path, raw: str | Path, *, allowed_subtree: str | None = None) -> Path:
    if raw is None:
        raise PathPolicyError("missing path")
    raw_text = str(raw)
    if not raw_text.strip():
        raise PathPolicyError("missing path")
    raw_path = Path(raw_text)
    root = resolve_run_root(run_root)
    base = (root / allowed_subtree).resolve() if allowed_subtree else root
    candidate = raw_path if raw_path.is_absolute() else root / raw_path
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(base)
    except ValueError as exc:
        raise PathPolicyError(f"path escapes allowed root: {raw_text}") from exc
    reject_symlink_components(root, candidate)
    return resolved


def display_path(path: Path, run_root: Path) -> str:
    try:
        return str(path.resolve(strict=False).relative_to(run_root.resolve()))
    except ValueError:
        return str(path)
