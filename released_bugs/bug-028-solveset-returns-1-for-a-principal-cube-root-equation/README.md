# Candidate Bug 28: solveset over the reals returns -1 for the principal cube-root equation

**Status**

Confirmed

**SymPy version**

SymPy 1.14.0, `SYMPY_CHECKOUT_PATH=$SYMPY_CHECKOUT_PATH`, SymPy file `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`, Python executable `python3`.

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
eq = Eq(x**Rational(1, 3), -1)
sol = solveset(eq, x, S.Reals)
print("equation:", eq)
print("solveset:", sol)
for s in sol:
    print("candidate:", s)
    print("lhs at candidate:", eq.lhs.subs(x, s))
    print("residual:", simplify(eq.lhs.subs(x, s) - eq.rhs))
    print("numeric residual:", N(eq.lhs.subs(x, s) - eq.rhs, 30))
print("complex-domain solveset:", solveset(eq, x, S.Complexes))
```

**Actual output**

```text
equation: Eq(x**(1/3), -1)
solveset: {-1}
candidate: -1
lhs at candidate: (-1)**(1/3)
residual: 1 + (-1)**(1/3)
numeric residual: 1.5 + 0.866025403784438646763723170753*I
complex-domain solveset: EmptySet
```

**Expected output**

`EmptySet` for `S.Reals`, because SymPy's `x**Rational(1, 3)` is the principal complex power and `(-1)**(1/3)` is not `-1`.

**Why this is wrong**

SymPy `Pow` with a rational exponent uses the principal complex branch. The principal cube root of `-1` is `1/2 + sqrt(3)*I/2`, not the real cube root `-1`. The returned value therefore does not satisfy the original equation; substituting it gives a nonzero residual.

**Root cause**

The diagnosis locates the faulty path in `sympy/solvers/solveset.py`, especially `_invert_real` at `solveset.py:284-291`. When the exponent denominator is odd, `_invert_real` inverts the principal `Pow` using `real_root` semantics, producing `-1` as if the original expression were a real radical. The later `_check=True` filtering only calls `domain_check`, which checks definedness rather than equation truth, so the extraneous solution remains. See `root_cause.md` for the call path and source-level details.

**Independent verification**

`related_bugs.py` checks denominators `3, 5, 7, 9, 11, 13`. It compares the SymPy result with Python's independent principal complex power evaluation, which gives a nonzero residual for `x = -1` in every case.

**Additional instantiations**

The verification file and regression test include five additional odd-denominator principal-root equations: denominators `5, 7, 9, 11, 13`.

**Affected function or subsystem**

`sympy/solvers/solveset.py:_invert_real`, lines `284-291`; public API `solveset`.

**Severity**

High

**Suggested regression test**

See `pr/tests/test_bug_028_solveset_over_the_reals_returns_1_for_the_principal_cube_roo.py`.

**Confidence**

95%. The returned finite solution has a direct nonzero residual and the source-level branch that substitutes real-root semantics for principal `Pow` is located.
