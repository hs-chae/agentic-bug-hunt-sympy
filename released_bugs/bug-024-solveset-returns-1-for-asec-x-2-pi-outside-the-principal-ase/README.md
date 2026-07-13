# Candidate Bug 24: solveset returns 1 for asec(x) = 2*pi outside the principal asec range

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
eq = Eq(asec(x), 2*pi)
sol = solveset(eq, x, domain=S.Complexes)
print("solution:", sol)
print("residual at returned value:", simplify((eq.lhs - eq.rhs).subs(x, 1)))
print("numeric residual:", N((eq.lhs - eq.rhs).subs(x, 1), 50))
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
solution: {1}
residual at returned value: -2*pi
numeric residual: -6.2831853071795864769252867665590057683943387987502
```

**Expected output**

EmptySet. The principal value asec(1) is 0, and 2*pi is outside the principal inverse-secant value at x = 1.

**Why this is wrong**

SymPy applies `sec` to both sides and accepts `x = sec(2*pi) = 1`. Principal `asec` is not a global two-sided inverse of `sec`, so the returned value must still be checked against the original equation.

**Root cause**

The diagnosis locates the cause in `sympy/solvers/solveset.py:550-557`, where `_invert_complex` uses the generic `.inverse()` path for `asec(_C)`. Since `asec.inverse()` returns `sec`, the solver transforms `asec(_C) = 2*pi` into `_C = sec(2*pi)` without checking the principal range of `asec`. Full details are in `root_cause.md`.

**Independent verification**

`related_bugs.py` checks these targets against direct residuals and the independent principal formula `asec(z) = acos(1/z)` using Python `cmath`.

**Additional instantiations**

The same false solution appears for `asec(x) = 2*pi*n` with `n` in `[1, 2, -1, 3, 4, 5]`. These cases are parametrized in `related_bugs.py` and the PR regression test.

**Affected function or subsystem**

`sympy/solvers/solveset.py:550-557`, `_invert_complex`; `asec.inverse()` from `sympy/functions/elementary/trigonometric.py:3130-3134`.

**Severity**

High.

**Suggested regression test**

See `pr/tests/test_bug_024_solveset_returns_1_for_asec_x_2_pi_outside_the_principal_ase.py`.

**Confidence**

96%. The reproducer directly returns a value whose substitution or real-integral interpretation contradicts the original mathematical problem.
