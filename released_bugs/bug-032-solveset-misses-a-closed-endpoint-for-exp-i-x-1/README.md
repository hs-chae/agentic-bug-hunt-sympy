### Candidate Bug 32: solveset misses the endpoint 2*pi for exp(I*x) = 1 on a closed interval

**Status**

Confirmed

**SymPy version**

SymPy version: 1.14.0

SYMPY_CHECKOUT_PATH: `$SYMPY_CHECKOUT_PATH`

SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`

Python executable: `python3`

Commit hash: None

**Minimal reproducer**

```python
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *  # noqa: F401,F403

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not os.path.abspath(sympy.__file__).startswith(os.path.abspath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

x = symbols("x")
interval = Interval(0, 2*pi)
sol = solveset(Eq(exp(I*x), 1), x, interval)
print("solution:", sol)
print("2*pi in solution:", sol.contains(2*pi))
print("residual at 2*pi:", simplify(exp(I*2*pi) - 1))

```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
solution: {0}
2*pi in solution: False
residual at 2*pi: 0
```

**Expected output**

On the closed interval [0, 2*pi], exp(I*x)=1 at both endpoints, so the expected solution set is {0, 2*pi}.

**Why this is wrong**

Euler periodicity gives exp(I*2*pi)=1, so x=2*pi exactly satisfies the equation and lies in the closed domain. The returned FiniteSet omits it.

**Root cause**

The diagnosis locates the problem in sympy/solvers/solveset.py:178. For a real interval domain, _invert chooses _invert_real for exp(I*x), applies a single-valued logarithm, and loses the periodic ImageSet that _invert_complex would produce. See `root_cause.md` for the full call path and source-level analysis.

**Independent verification**

`related_bugs.py` checks the representative case plus five additional instantiations. It also evaluates the critical point with an independent numerical oracle (`math`, `cmath`, or direct complex arithmetic as appropriate). On SymPy 1.14.0 it prints `Incorrect` and exits nonzero.

**Additional instantiations**

The bundle uses `k = 5` additional instantiations, included as parametrized cases in `related_bugs.py` and mirrored in `pr/tests/test_bug_032_solveset-misses-the-endpoint-2-pi-for-exp-i-x-1-on-a-closed-.py`.

**Affected function or subsystem**

solvers.solveset / periodic exponential equations over intervals; affected locations from diagnosis: sympy/solvers/solveset.py:178, sympy/solvers/solveset.py:1313.

**Severity**

Medium

**Suggested regression test**

See `pr/tests/test_bug_032_solveset-misses-the-endpoint-2-pi-for-exp-i-x-1-on-a-closed-.py`.

**Confidence**

95%: the reproducer has an exact symbolic counterexample, a numerical cross-check, and a source-level diagnosis matching the observed failure.
