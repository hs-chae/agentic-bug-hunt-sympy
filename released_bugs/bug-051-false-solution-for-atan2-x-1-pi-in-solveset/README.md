### Candidate Bug 51: solveset returns 0 for atan2(x, 1) = pi over the reals

**Status**

Confirmed

**SymPy version**

- SymPy version: 1.14.0
- SYMPY_CHECKOUT_PATH: `$SYMPY_CHECKOUT_PATH`
- SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`
- Python executable: `python3`

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
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")


x = symbols("x")
eq = Eq(atan2(x, 1), pi)
sol = solveset(eq, x, S.Reals)
print("solveset(Eq(atan2(x, 1), pi), x, S.Reals) =", sol)
print("residual at returned value 0 =", (eq.lhs - eq.rhs).subs(x, 0))
print("atan2(0, 1) =", atan2(0, 1))
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
solveset(Eq(atan2(x, 1), pi), x, S.Reals) = {0}
residual at returned value 0 = -pi
atan2(0, 1) = 0
```

**Expected output**

EmptySet. For real x, atan2(x, 1) lies strictly between -pi/2 and pi/2.

**Why this is wrong**

The returned value x=0 does not satisfy the equation: atan2(0, 1)=0, so the residual is -pi. More generally, the point (1, x) is in the right half-plane and cannot have principal argument pi.

**Root cause**

The diagnosis locates the bug in _invert_real in sympy/solvers/solveset.py. After atan2(x, 1) simplifies to atan(x), the solver applies tan to the right-hand side pi without checking that pi is in atan's real range. See root_cause.md for details.

**Independent verification**

`related_bugs.py` runs the representative case plus five additional instantiations and includes an independent numerical or elementary-function check for each case. On this checkout it prints `Incorrect` and exits nonzero.

**Additional instantiations**

The verification and regression tests cover six scale/denominator/sign variants of atan2(scale*x, denom) = +/-pi with positive denominator.

**Affected function or subsystem**

solvers / solveset / inverse-trig range checks. Affected location from the diagnosis: sympy/solvers/solveset.py:230-238.

**Severity**

High

**Suggested regression test**

The proposed pytest file is `pr/tests/test_bug_051_solveset-returns-0-for-atan2-x-1-pi-over-the-reals.py`. It contains one parametrized test covering the representative case plus five additional instantiations.

**Confidence**

98%. The reproducer is deterministic, independently checked, and has a source-level diagnosis.
