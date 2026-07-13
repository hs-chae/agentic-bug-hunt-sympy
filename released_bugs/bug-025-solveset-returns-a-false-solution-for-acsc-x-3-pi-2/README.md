### Candidate Bug 25: solveset returns -1 for acsc(x) = 3*pi/2 outside the principal range

**Status**

Confirmed

**SymPy version**

SymPy 1.14.0, `SYMPY_CHECKOUT_PATH=$SYMPY_CHECKOUT_PATH`, `sympy.__file__=$SYMPY_CHECKOUT_PATH/sympy/__init__.py`, Python executable `python3`.

**Minimal reproducer**

```python
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if SYMPY_CHECKOUT_PATH:
    sys.path.insert(0, SYMPY_CHECKOUT_PATH)
import sympy
from sympy import *

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)

x = symbols("x")
sol = solveset(Eq(acsc(x), 3*pi/2), x, S.Complexes)
print("solveset(Eq(acsc(x), 3*pi/2), x, S.Complexes) =", sol)
for candidate in sol:
    print("residual =", simplify(acsc(candidate) - 3*pi/2))
```

**Actual output**

```text
solveset(Eq(acsc(x), 3*pi/2), x, S.Complexes) = {-1}
residual = -2*pi
```

**Expected output**

`EmptySet`, or at minimum no returned value whose substitution residual is nonzero. `acsc(-1)` is `-pi/2`, not `3*pi/2`.

**Why this is wrong**

Applying `csc` to both sides is not reversible unless the target is in the principal range of `acsc`. The value `3*pi/2` is coterminal with `-pi/2` modulo `2*pi`, but it is not the principal value returned by `acsc(-1)`. The returned candidate fails direct substitution.

**Root cause**

The diagnosis in `root_cause.md` locates the faulty step at `sympy/solvers/solveset.py:550-557` in `_invert_complex`. The generic inverse-function branch applies `acsc.inverse()`, which is `csc`, and maps `3*pi/2` to `-1` without attaching or checking a principal-range condition. The final `solveset` result accepts that false candidate.

**Independent verification**

`related_bugs.py` checks the representative target plus five related out-of-range targets. It compares the substitution residual with an independent principal `acsc` calculation using Python `cmath.asin(1/z)`.

**Additional instantiations**

Five additional target values are included in `related_bugs.py` and mirrored in `pr/tests/test_bug_025_solveset_returns_1_for_acsc_x_3_pi_2_outside_the_principal_a.py`.

**Affected function or subsystem**

`sympy.solvers.solveset._invert_complex`, `sympy/solvers/solveset.py:550-557`; `acsc.inverse` in `sympy/functions/elementary/trigonometric.py:3340-3344`.

**Severity**

High

**Suggested regression test**

See `pr/tests/test_bug_025_solveset_returns_1_for_acsc_x_3_pi_2_outside_the_principal_a.py`.

**Confidence**

88%. The solver returns an explicit value with exact residual `-2*pi`, and the diagnosis identifies the branch-condition omission.
