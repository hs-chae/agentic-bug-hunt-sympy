# Candidate Bug 23: solveset returns 0 for atan(x) = pi outside the principal atan range

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
eq = Eq(atan(x), pi)
sol = solveset(eq, x, domain=S.Complexes)
print("solution =", sol)
for s in sol:
    print("residual at", s, "=", N(atan(s) - pi, 80))

```

**Actual output**

```text
solution = {0}
residual at 0 = -3.1415926535897932384626433832795028841971693993751058209749445923078164062862090
```

**Expected output**

EmptySet; the principal value atan(0) is 0, not pi.

**Why this is wrong**

Principal atan is not a globally invertible periodic tangent equation. Applying tan to both sides accepts values outside the principal branch range. The principal arctangent does not attain pi. SymPy's returned value x=0 fails direct substitution because atan(0)=0, and the 80-digit residual is exactly -pi.

**Root cause**

sympy/solvers/solveset.py:_invert_complex, lines 550-557, maps the target through atan(x).inverse() = tan without checking the target is in the principal atan range. The full diagnosis, including call path and mechanism, is in `root_cause.md`.

**Independent verification**

`related_bugs.py` runs the representative case plus 5 additional instantiations. It substitutes SymPy's returned candidate into the original equation and compares the principal value against Python `cmath`; on this checkout it reports nonzero residuals and exits with `Incorrect`.

**Additional instantiations**

The parametrized cases are in `related_bugs.py` and mirrored in `pr/tests/test_bug_023_solveset_returns_0_for_atan_x_pi_outside_the_principal_atan_.py`.

**Affected function or subsystem**

solvers.solveset / inverse trigonometric functions; affected locations: sympy/solvers/solveset.py:550-557, sympy/solvers/solveset.py:1313, sympy/functions/elementary/trigonometric.py:2775.

**Severity**

High

**Suggested regression test**

Use `pr/tests/test_bug_023_solveset_returns_0_for_atan_x_pi_outside_the_principal_atan_.py`. It asserts that `solveset` must not return the false candidate and that any returned candidate satisfies the original equation.

**Confidence**

97%, because direct substitution, high-precision residuals, independent principal-value evaluation, and source-level diagnosis all agree.
