# Candidate Bug 1: solveset returns 0 for asin(x) = pi outside the principal asin range

**Status**

Confirmed.

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
eq = Eq(asin(x), pi)
sol = solveset(eq, x, domain=S.Complexes)
print("solveset result:", sol)
print("residual at returned value 0:", simplify(eq.lhs.subs(x, 0) - eq.rhs.subs(x, 0)))
print("numeric residual:", N(eq.lhs.subs(x, 0) - eq.rhs.subs(x, 0), 50))
```

**Actual output**

```text
solveset result: {0}
residual at returned value 0: -pi
numeric residual: -3.1415926535897932384626433832795028841971693993751
```

**Expected output**

`EmptySet`, because principal `asin` does not take the value `pi`.

**Why this is wrong**

SymPy's `asin` is the principal inverse sine. Direct substitution into the returned solution gives `asin(0) - pi = -pi`, so the reported solution does not satisfy the equation.

**Root cause**

The diagnosis locates the cause in `sympy/solvers/solveset.py:550`, inside `_invert_complex`. The generic inverse path uses `sin` as a global inverse of principal `asin`, producing `sin(pi) = 0` without carrying the required principal-range condition. Full details are in `root_cause.md`.

**Independent verification**

`related_bugs.py` checks six nonzero integer multiples of `pi` and compares the candidate residual at `x = 0` with Python `cmath.asin`.

**Additional instantiations**

The same false solution appears for `asin(x) = n*pi` with `n` in `[1, 2, -1, 3, 4, 5]`; these cases are parametrized in `related_bugs.py` and the PR regression test.

**Affected function or subsystem**

`sympy/solvers/solveset.py:550`, `_invert_complex`; subsystem `solvers.solveset / inverse trigonometric functions`.

**Severity**

High.

**Suggested regression test**

See `pr/tests/test_bug_001_solveset_returns_0_for_asin_x_pi_outside_the_principal_asin_.py`.

**Confidence**

98%. The returned value has a direct residual of `-pi` in the representative case and analogous nonzero residuals in the additional cases.
