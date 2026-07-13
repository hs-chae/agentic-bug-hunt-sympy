# Candidate Bug 61: series(expint(2, x), x=0) adds a spurious imaginary term on the positive real branch

**Status**

Confirmed

**SymPy version**

SymPy version: `1.14.0`

`SYMPY_CHECKOUT_PATH`: `$SYMPY_CHECKOUT_PATH`

SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`

Python executable: `python3`

**Minimal reproducer**

```python
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *  # noqa: F401,F403

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)

x = symbols("x", positive=True)
s = series(expint(2, x), x, 0, 2)
print("series:", s)
t = Rational(1, 1000)
print("truncated at 1/1000:", N(s.removeO().subs(x, t), 50))
print("actual at 1/1000:", N(expint(2, t), 50))
```

**Actual output**

```text
series: 1 + x*(log(x) - 1 + EulerGamma - I*pi) + O(x**2)
truncated at 1/1000: 0.99266946038591939580855253772602930980823885487005 - 0.0031415926535897932384626433832795028841971693993751*I
actual at 1/1000: 0.99266896046923884233605257079126963912695444183171
```

**Expected output**

For positive real `x`, the first-order series should be `1 + x*(log(x) - 1 + EulerGamma) + O(x**2)`, with no `-I*pi*x` term.

**Why this is wrong**

For `x > 0`, `E_2(x) = exp(-x) - x*E_1(x)` and `E_1(x) = -EulerGamma - log(x) + x + O(x**2)`. This gives a real expansion through first order. The imaginary term contradicts both the recurrence and high-precision numerical evaluation.

**Root cause**

The diagnosis locates the failure in `sympy/functions/special/error_functions.py:1226-1227` and `:1443-1445`. `expint._eval_nseries` rewrites through `Ei(x*exp_polar(I*pi))`, then `Ei._eval_rewrite_as_Si` treats that polar argument as an ordinary negative value and subtracts `I*pi`; see `root_cause.md` for details.

**Independent verification**

The verification script checks six positive argument scalings. It compares SymPy's series with the recurrence-derived real series and with `mpmath.expint` samples on the positive real axis.

**Additional instantiations**

The representative case plus five scaled positive arguments are covered in `related_bugs.py` and mirrored in the PR regression test.

**Affected function or subsystem**

series / special functions / exponential integrals; affected code: `sympy/functions/special/error_functions.py:1226-1227` and `sympy/functions/special/error_functions.py:1443-1445`.

**Severity**

Medium

**Suggested regression test**

```python
import pytest

from sympy import EulerGamma, I, O, S, expint, log, pi, series, simplify, symbols


@pytest.mark.parametrize("scale", [S(1), S(2), S(3), S.Half, S(5), 3*S.Half])
def test_expint_two_positive_origin_series_has_no_imaginary_branch_term(scale):
    x = symbols("x", positive=True)
    actual = series(expint(2, scale*x), x, 0, 2)
    expected = 1 + scale*x*(log(scale*x) - 1 + EulerGamma) + O(x**2)
    assert simplify(actual.removeO() - expected.removeO()) == 0
```

**Confidence**

95%, because the wrong series reproduces, the source diagnosis identifies the branch correction, and independent recurrence/numerical checks agree against SymPy.
