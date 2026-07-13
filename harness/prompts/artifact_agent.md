You are the artifact-generation agent in a multi-agent SymPy correctness-bug harness.

The deduplication agent has reviewed a batch of minimized candidates. Your job in this phase is to create final artifact bundles only for candidates whose dedup reports recommend continuing.

Read the artifact batch plan:

```text
{artifact_batch_path}
```

The plan lists each candidate JSON path, dedup report path, artifact status
path, assigned bug number, slug, artifact directory, and artifact directory
relative to `RESULT_DIR`. Process every item in the plan. Read each candidate
JSON and dedup report before creating that item's artifact.

For any item whose dedup report recommendation is `reject_as_duplicate`, do not
create a final artifact bundle. Instead, write a short rejection status to that
item's `artifact_status_path`.

If the recommendation is `continue_to_artifact_generation` or `continue_but_mark_unclear`, create a complete artifact bundle under:

```text
the item's artifact_dir
```

This path is under `RESULT_DIR/bug-report/`, not inside the SymPy checkout.

Follow the final artifact requirements in `prompts/shared_bug_policy.md`. The bundle must contain:

```text
README.md
reproduce_bug.py
related_bugs.py
dedup_report.md
pr/
  README.md
  tests/
    test_bug_<bug_number_padded>_<slug>.py
```

Copy the dedup report into the bundle as `dedup_report.md` (verbatim from the
item's dedup report path).

Do NOT write `bug.json` into the bundle. Do NOT write
`candidate_minimized.json` or `artifact_status.json` into the
bundle either. You still write the item's `artifact_status_path` (it lives outside the
bundle, in the candidate's working directory) as the harness control signal; the
harness copies `root_cause.md` into the bundle for you.

Source-level diagnosis: each item in the artifact batch plan may include a
`diagnosis_report_path` pointing at a `root_cause.md` produced by the diagnosis
agent (the diagnosis phase always runs, so it is absent only if that agent
errored or could not locate a cause). When it exists,
read it and use its findings — the responsible file/function/line, the faulty
step, the call path, and the mechanism — to write the required **Root cause**
section of `README.md` (a few-sentence summary that refers the reader to
`root_cause.md`) and the "Affected function or subsystem" line, instead of a bare
guess. Every bug `README.md` must contain a Root cause section. The harness
copies `root_cause.md` into the bundle automatically; do not overwrite it, and do
not fabricate a source-level cause if no diagnosis is available — in that case
say so explicitly in the Root cause section and fall back to a clearly-labelled
hypothesis.

The artifact must include:

- one minimal representative instantiation,
- a source-level root cause when a `root_cause.md` diagnosis is available, otherwise a clearly-labelled hypothesis of what is causing the problem,
- concrete mathematical evidence that SymPy is wrong,
- runnable test code in `related_bugs.py` that would print or return `Correct` if SymPy were correct, exercising the representative case plus `k = 5` additional instantiations (unless a smaller number is justified) as parametrized cases inside that one file, AND folding in the concrete runnable numerical cross-check (high precision and, when useful, a comparison with NumPy/SciPy/`cmath` or another independent computation) as part of the same file. Do not emit a separate `numerical_evidence.py` or `additional_instantiations.py`.
- a human-ready `pr/README.md` draft and a single parametrized regression-test file under `pr/tests/` that follows SymPy's test conventions: plain `from sympy import ...`, no `sys.path` manipulation, no environment prints, and a `@pytest.mark.parametrize` test covering the representative case plus the additional instantiations. Do not submit a PR remotely.

Every runnable script must force-import SymPy from `SYMPY_CHECKOUT_PATH` before
`import sympy`, reading that path from the environment with
`os.environ.get("SYMPY_CHECKOUT_PATH")` (the harness exports it) -- do NOT
hardcode the absolute checkout path into the file, so the published artifact
stays portable. Each script must print `sympy.__version__`, `sympy.__file__`,
and `sys.executable`.

Canonical structure for `related_bugs.py` (the merged evidence+test
file). Adapt the case grid and the two per-case checks to the specific bug, but
keep this shape so the one file is both an importable pytest and a standalone
`python related_bugs.py` runner, and carries the independent numerical
cross-check inline:

```python
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import cmath  # or mpmath; the independent oracle, not SymPy
import pytest
import sympy
from sympy import *  # noqa: F401,F403

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

# Representative case first, then k=5 additional instantiations of the same pattern.
CASES = [0, 1, 2, 3, 4, 5]


def check_case(a):
    """Return (ok, detail). `ok` is True iff SymPy agrees with the independent
    numerical oracle for this instantiation."""
    x = symbols("x")
    lhs = sqrt((x + a) ** 2)
    rhs = x + a
    bad = -a - 2
    sol = solveset(Eq(lhs, rhs), x, domain=S.Complexes)
    sympy_residual = simplify((lhs - rhs).subs(x, bad))
    oracle_residual = cmath.sqrt(complex((bad + a) ** 2)) - complex(bad + a)  # independent
    ok = not (sol.contains(bad) is S.true and sympy_residual != 0)
    detail = (f"a={a} sol={sol} bad={bad} sympy_residual={sympy_residual} "
              f"oracle_residual={oracle_residual}")
    return ok, detail


@pytest.mark.parametrize("a", CASES)
def test_sympy_correct(a):
    ok, detail = check_case(a)
    assert ok, detail


if __name__ == "__main__":
    failures = []
    for a in CASES:
        ok, detail = check_case(a)
        print(detail)
        if not ok:
            failures.append(detail)
    if failures:
        print("Incorrect")
        raise SystemExit(1)
    print("Correct")
```

Before writing `artifact_status_path`, list or inspect the bundle and make sure
the required files are inside the bug-specific directory. Do not place per-bug
artifact files directly under `RESULT_DIR` or directly under `RESULT_DIR/bug-report/`.

For each item, when finished, write its `artifact_status_path` as valid JSON
with this shape:

```json
{
  "status": "artifact_created",
  "artifact_dir": "bug-report/bug-001-short-title",
  "notes": "brief notes"
}
```

Use an `artifact_dir` relative to `RESULT_DIR`, as in the example above.

If you decide not to create the artifact, use:

```json
{
  "status": "artifact_rejected",
  "reason": "brief reason"
}
```

Stop after writing all artifact status files for the batch.
