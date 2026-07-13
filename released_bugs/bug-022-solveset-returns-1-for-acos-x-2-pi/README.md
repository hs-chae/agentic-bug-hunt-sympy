# Candidate Bug 22: solveset returns 1 for acos(x) = 2*pi outside the principal acos range

**Status**

Confirmed

**SymPy version**

SymPy 1.14.0; `SYMPY_CHECKOUT_PATH` supplied by the harness; observed `sympy.__file__` is `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`; Python executable `python3`.

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
eq = Eq(acos(x), 2*pi)
sol = solveset(eq, x, domain=S.Complexes)
print("solution =", sol)
for s in sol:
    print("residual at", s, "=", N(acos(s) - 2*pi, 80))

```

**Actual output**

```text
solution = {1}
residual at 1 = -6.2831853071795864769252867665590057683943387987502116419498891846156328125724180
```

**Expected output**

EmptySet; the principal value acos(1) is 0, not 2*pi.

**Why this is wrong**

The principal branch of acos does not attain real values outside its principal range. Applying cos to both sides solves a periodic equation and introduces extraneous points. The principal branch of acos has range 0 <= Re(acos(z)) <= pi (with branch conventions), so 2*pi is not attained. Direct substitution gives acos(1) - 2*pi = -2*pi, and numerically the residual is nonzero to 80 digits.

**Root cause**

sympy/solvers/solveset.py:_invert_complex, lines 550-557, applies acos(x).inverse() = cos to the target set without a principal-range condition; _solveset later checks only definedness, not the residual. The full diagnosis, including call path and mechanism, is in `root_cause.md`.

**Independent verification**

`related_bugs.py` runs the representative case plus 5 additional instantiations. It substitutes SymPy's returned candidate into the original equation and compares the principal value against Python `cmath`; on this checkout it reports nonzero residuals and exits with `Incorrect`.

**Additional instantiations**

The parametrized cases are in `related_bugs.py` and mirrored in `pr/tests/test_bug_022_solveset_returns_1_for_acos_x_2_pi_outside_the_principal_aco.py`.

**Affected function or subsystem**

solvers.solveset / inverse trigonometric functions; affected locations: sympy/solvers/solveset.py:550-557, sympy/solvers/solveset.py:1313, sympy/functions/elementary/trigonometric.py:2560.

**Severity**

High

**Suggested regression test**

Use `pr/tests/test_bug_022_solveset_returns_1_for_acos_x_2_pi_outside_the_principal_aco.py`. It asserts that `solveset` must not return the false candidate and that any returned candidate satisfies the original equation.

**Confidence**

97%, because direct substitution, high-precision residuals, independent principal-value evaluation, and source-level diagnosis all agree.
