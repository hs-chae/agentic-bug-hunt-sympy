# Candidate Bug 7: dsolve returns a solution that fails f' = sqrt(f**2)

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
f = Function("f")
C1 = symbols("C1")
ode = Eq(diff(f(x), x), sqrt(f(x)**2))
sol = dsolve(ode)
rhs = sol[0].rhs.subs(C1, 1)
residual = diff(rhs, x) - sqrt(rhs**2)
print("dsolve result:", sol)
print("chosen returned branch with C1=1:", rhs)
print("residual:", simplify(residual))
print("residual at x=0:", N(residual.subs(x, 0), 50))
```

**Actual output**

```text
dsolve result: [Eq(f(x), C1*exp(-x)), Eq(f(x), C1*exp(x))]
chosen returned branch with C1=1: exp(-x)
residual: -sqrt(exp(-2*x)) - exp(-x)
residual at x=0: -2.0000000000000000000000000000000000000000000000000
```

**Expected output**

The returned solution set should not include an unrestricted `C1*exp(-x)` branch. If a decreasing branch is returned, it needs a sign or branch condition on the constant/function.

**Why this is wrong**

For `f(x) = exp(-x)`, the left side is `-exp(-x)` and the right side is `sqrt(exp(-2*x)) = exp(-x)` on the real line. At `x = 0`, the ODE residual is `-2`, so the returned branch is not a solution.

**Root cause**

The diagnosis narrows the cause to `sympy/solvers/ode/ode.py:1666`, in `odesimp`. The separable solution contains the branch-sensitive term `sqrt(f(x)**2)`, but `odesimp` calls `solve(..., force=True)` and returns explicit exponential branches without retaining the sign condition on `f(x)` or the integration constant. Full details are in `root_cause.md`.

**Independent verification**

`related_bugs.py` substitutes positive constants `1` through `6` into each returned explicit branch and checks the ODE residual at `x = 0`; it also records the elementary oracle residual for the decreasing branch.

**Additional instantiations**

The additional instantiations are positive constants `2, 3, 4, 5, 6` substituted into the returned `C1*exp(-x)` branch; all produce nonzero residuals.

**Affected function or subsystem**

`sympy/solvers/ode/ode.py:1666`, `odesimp`; subsystem `ODE solving / branch-sensitive nonlinear equations`.

**Severity**

High.

**Suggested regression test**

See `pr/tests/test_bug_007_dsolve_returns_a_solution_that_fails_f_sqrt_f_2.py`.

**Confidence**

97%. Direct residual substitution shows one returned explicit branch is false for every tested positive constant.
