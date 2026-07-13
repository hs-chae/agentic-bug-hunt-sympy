#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/setup_sympy_target.sh [options]

Creates a reproducible SymPy target checkout/worktree for CAS bug-hunting.

Options:
  --base-dir DIR          Parent directory for clone, worktrees, and metadata.
                          Default: $HOME/sympy-bug-hunt
  --repo-url URL          SymPy git repository URL.
                          Default: https://github.com/sympy/sympy.git
  --ref REF               Git ref to lock the run to.
                          Default: origin/master
  --run-name NAME         Worktree directory name.
                          Default: sympy-run-YYYYmmdd-HHMMSS
  --env-name NAME         Conda environment name.
                          Default: sympy-bug-hunt
  --no-fetch              Do not git fetch before resolving --ref.
  --no-worktree           Use the main clone directly instead of creating a worktree.
  --create-env            Create the conda environment, but do not install packages.
  --install               Install SymPy editable + bug-hunt dependencies into conda env.
  --no-conda              Skip conda environment creation/checks.
  -h, --help              Show this help.

Output:
  Prints TARGET_DIR=... as the final line. Pass that path to:
    python3 scripts/run_harness.py --sympy-dir "$TARGET_DIR"

Notes:
  This script intentionally does not use Codex dangerous sandbox bypasses.
  Use a fresh worktree per autonomous run so generated artifacts and edits are isolated.
EOF
}

BASE_DIR="${HOME}/sympy-bug-hunt"
REPO_URL="https://github.com/sympy/sympy.git"
REF="origin/master"
RUN_NAME="sympy-run-$(date +%Y%m%d-%H%M%S)"
ENV_NAME="sympy-bug-hunt"
DO_FETCH=1
DO_WORKTREE=1
DO_INSTALL=0
DO_CONDA=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-dir)
      BASE_DIR="$2"
      shift 2
      ;;
    --repo-url)
      REPO_URL="$2"
      shift 2
      ;;
    --ref)
      REF="$2"
      shift 2
      ;;
    --run-name)
      RUN_NAME="$2"
      shift 2
      ;;
    --env-name)
      ENV_NAME="$2"
      shift 2
      ;;
    --no-fetch)
      DO_FETCH=0
      shift
      ;;
    --no-worktree)
      DO_WORKTREE=0
      shift
      ;;
    --create-env)
      DO_CONDA=1
      shift
      ;;
    --install)
      DO_CONDA=1
      DO_INSTALL=1
      shift
      ;;
    --no-conda)
      DO_CONDA=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

CLONE_DIR="$BASE_DIR/sympy-main"
RUNS_DIR="$BASE_DIR/runs"
METADATA_DIR="$BASE_DIR/metadata"

mkdir -p "$BASE_DIR" "$RUNS_DIR" "$METADATA_DIR"

if [[ ! -d "$CLONE_DIR/.git" ]]; then
  echo "[setup] cloning SymPy into $CLONE_DIR"
  git clone "$REPO_URL" "$CLONE_DIR"
else
  echo "[setup] using existing clone $CLONE_DIR"
fi

if [[ "$DO_FETCH" -eq 1 ]]; then
  echo "[setup] fetching latest refs"
  git -C "$CLONE_DIR" fetch --tags origin
fi

COMMIT="$(git -C "$CLONE_DIR" rev-parse "$REF")"
echo "[setup] locked ref $REF to commit $COMMIT"

if [[ "$DO_WORKTREE" -eq 1 ]]; then
  TARGET_DIR="$RUNS_DIR/$RUN_NAME"
  if [[ -e "$TARGET_DIR" ]]; then
    echo "Target worktree already exists: $TARGET_DIR" >&2
    exit 1
  fi
  echo "[setup] creating worktree $TARGET_DIR"
  git -C "$CLONE_DIR" worktree add --detach "$TARGET_DIR" "$COMMIT"
else
  TARGET_DIR="$CLONE_DIR"
  echo "[setup] using main clone as target"
  git -C "$TARGET_DIR" checkout --detach "$COMMIT"
fi

if [[ "$DO_CONDA" -eq 1 ]]; then
  if ! command -v conda >/dev/null 2>&1; then
    echo "[setup] conda not found on PATH; skipping env setup" >&2
  else
    if ! conda env list | awk '{print $1}' | grep -qx "$ENV_NAME"; then
      echo "[setup] creating conda env $ENV_NAME"
      conda create -n "$ENV_NAME" python=3.12 -y
    else
      echo "[setup] using existing conda env $ENV_NAME"
    fi

    if [[ "$DO_INSTALL" -eq 1 ]]; then
      echo "[setup] installing target checkout into conda env $ENV_NAME"
      conda run -n "$ENV_NAME" python -m pip install -U pip
      conda run -n "$ENV_NAME" python -m pip install -e "$TARGET_DIR[dev]"
      conda run -n "$ENV_NAME" python -m pip install numpy scipy mpmath pytest hypothesis
    else
      echo "[setup] install skipped; rerun with --install to install editable SymPy and dependencies"
    fi
  fi
fi

METADATA_FILE="$METADATA_DIR/$RUN_NAME.json"
cat > "$METADATA_FILE" <<EOF
{
  "target_dir": "$TARGET_DIR",
  "clone_dir": "$CLONE_DIR",
  "repo_url": "$REPO_URL",
  "ref": "$REF",
  "commit": "$COMMIT",
  "run_name": "$RUN_NAME",
  "env_name": "$ENV_NAME",
  "created_at_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo "[setup] metadata: $METADATA_FILE"
echo "TARGET_DIR=$TARGET_DIR"
