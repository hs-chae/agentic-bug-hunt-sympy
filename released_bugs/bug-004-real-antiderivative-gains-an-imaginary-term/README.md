### Candidate Bug 4: Integral of log(x)/(x**2 - 1) differentiates back with an extra imaginary term

**Status**

Confirmed

**SymPy version**

SymPy 1.14.0, `SYMPY_CHECKOUT_PATH=$SYMPY_CHECKOUT_PATH`, `sympy.__file__=$SYMPY_CHECKOUT_PATH/sympy/__init__.py`, Python `python3`, commit `None`.

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
f = log(x)/(x**2 - 1)
F = integrate(f, x)
residual = simplify(diff(F, x) - f)
print(N(residual.subs(x, 2), 50))
```

**Actual output**

```text
residual at x=2 = 0.e-56 - 1.5707963267948966192313216916397514420985846996876*I
```

**Expected output**

The derivative of an indefinite integral should equal `log(x)/(x**2 - 1)` at a regular point such as `x = 2`, so the residual should be `0`.

**Why this is wrong**

The integrand is finite and analytic at `x = 2`, with real value `log(2)/3`. A correct antiderivative on that interval differentiates back to the integrand; the nonzero residual `-I*pi/2` is a branch artifact.

**Root cause**

The diagnosis locates the faulty branch in `sympy/integrals/meijerint.py:196` and `sympy/integrals/meijerint.py:1653-1740`. The integration-by-parts result delegates `Integral(log(x - 1)/x, x)` to Meijer integration; the shifted-log rewrite uses a principal-branch representation that differentiates to `log(x - 1)/x + I*pi/x` on the positive side of the branch point. See `root_cause.md` for details.

**Independent verification**

`related_bugs.py` evaluates the derivative residual at regular real points and also computes the finite real integrand value with Python `cmath`. The residual should be zero, but the representative case gives `-I*pi/2`.

**Additional instantiations**

Five additional cases are included for `log(x)/(x**2 - a**2)` with `a = 2, 3, 4, 5, 6`, evaluated at `x = 2*a`.

**Affected function or subsystem**

Integrals / Meijer indefinite integration: `sympy/integrals/meijerint.py:196`, `sympy/integrals/meijerint.py:1653-1740`.

**Severity**

High

**Suggested regression test**

See `pr/tests/test_bug_004_integral_of_log_x_x_2_1_differentiates_back_with_an_extra_im.py`.

**Confidence**

92%. The derivative check fails at ordinary real points, and the diagnosis isolates the subintegral branch error.
