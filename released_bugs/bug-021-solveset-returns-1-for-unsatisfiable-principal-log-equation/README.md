# Candidate Bug 21: solveset returns 1 for unsatisfiable principal-log equation

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
eq = Eq(log(x), 2*pi*I)
sol = solveset(eq, x, domain=S.Complexes)
print("solveset result:", sol)
print("residual at returned value 1:", simplify(eq.lhs.subs(x, 1) - eq.rhs.subs(x, 1)))
print("numeric residual:", N(eq.lhs.subs(x, 1) - eq.rhs.subs(x, 1), 50))
```

**Actual output**

```text
solveset result: {1}
residual at returned value 1: -2*I*pi
numeric residual: -6.2831853071795864769252867665590057683943387987502*I
```

**Expected output**

`EmptySet`, because SymPy `log` is the principal logarithm and no complex `x` satisfies `log(x) = 2*pi*I`.

**Why this is wrong**

The principal complex logarithm has imaginary part in `(-pi, pi]`. The value `2*pi*I` is outside that image. The returned value `x = 1` gives `log(1) - 2*pi*I = -2*pi*I`, so it is not a solution.

**Root cause**

The diagnosis locates the cause in `sympy/solvers/solveset.py:550`, inside `_invert_complex`. The generic inverse-function path applies `exp` as the inverse of `log` without checking that the target lies in the principal branch range of `log`; `_solveset` then accepts `{1}` after only a domain-finiteness check. Full details are in `root_cause.md`.

**Independent verification**

`related_bugs.py` checks the representative case plus five additional nonzero multiples of `2*pi*I`. It also compares the returned value against Python `cmath.log`, which gives a nonzero residual for the same principal branch convention.

**Additional instantiations**

The same false solution appears for `log(x) = 2*pi*I*n` with `n` in `[1, 2, -1, 3, 4, 5]`; these are parametrized in `related_bugs.py` and the PR regression test.

**Affected function or subsystem**

`sympy/solvers/solveset.py:550`, `_invert_complex`; subsystem `solvers.solveset / elementary inverse functions`.

**Severity**

High.

**Suggested regression test**

See `pr/tests/test_bug_021_solveset_returns_1_for_unsatisfiable_principal_log_equation.py`.

**Confidence**

98%. The returned finite set contains a value whose direct symbolic and numerical residual is nonzero.
