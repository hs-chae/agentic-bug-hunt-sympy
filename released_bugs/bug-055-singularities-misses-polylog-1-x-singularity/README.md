# Candidate Bug 55: singularities misses the logarithmic singularity of polylog(1, x) at x = 1

## Status

Confirmed.

## SymPy version

- SymPy version: `1.14.0`
- `SYMPY_CHECKOUT_PATH`: `$SYMPY_CHECKOUT_PATH`
- SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`
- Python executable: `python3`

## Minimal reproducer

```python
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if SYMPY_CHECKOUT_PATH:
    sys.path.insert(0, SYMPY_CHECKOUT_PATH)
import sympy
from sympy import *  # noqa: F401,F403
from sympy.calculus.singularities import singularities

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)

x = symbols("x")
expr = polylog(1, x)
sing = singularities(expr, x, S.Complexes)

print("expr =", expr)
print("singularities =", sing)
print("contains 1 =", sing.contains(1))
print("value at 1 =", expr.subs(x, 1))
print("rewritten value at 1 =", (-log(1 - x)).subs(x, 1))
```

## Actual output

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
expr = polylog(1, x)
singularities = EmptySet
contains 1 = False
value at 1 = zoo
rewritten value at 1 = zoo
```

## Expected output

The singularity set should include `x = 1`.

## Why this is wrong

The standard identity `polylog(1, z) = -log(1 - z)` shows that `polylog(1, x)` has a logarithmic singularity where `1 - x = 0`, i.e. at `x = 1`. SymPy also evaluates `polylog(1, 1)` and `-log(1 - 1)` to `zoo`, so returning `EmptySet` misses a concrete singular point.

## Root cause

The diagnosis located the miss in `sympy/calculus/singularities.py`, lines 95-108. The call path is the public `singularities(expr, x, S.Complexes)` function, which rewrites only a small set of trig/hyperbolic functions and scans for `Pow`, `log`, `asech`, `acsch`, `atanh`, and `acoth` atoms. It never expands `polylog(1, z)` through the existing `polylog._eval_expand_func` rewrite in `sympy/functions/special/zeta_functions.py`, lines 342-345, so no log atom is seen. See `root_cause.md` for the full source trace.

## Independent verification

`related_bugs.py` uses Python `cmath` to check the independent form `-log(1 - z)`: at `z = 1`, `-cmath.log(0)` is singular, and values near `z = 1` grow large. The same file also shows that `expand_func(polylog(1, arg))` exposes a log singularity that the current direct `singularities` call misses.

## Additional instantiations

The verifier and regression test cover `polylog(1, arg)` for `arg = x, x + 1, x - 2, 2*x, -x, x/3`. These have singular points `1, 0, 3, 1/2, -1, 3` respectively.

## Affected function or subsystem

`sympy/calculus/singularities.py:95-108`, `singularities`; calculus / singularities / special functions. Related available rewrite: `sympy/functions/special/zeta_functions.py:342-345`, `polylog._eval_expand_func`.

## Severity

Medium. The result misses a real singular point for a standard special-function identity.

## Suggested regression test

```python
import pytest
from sympy import S, polylog, symbols
from sympy.calculus.singularities import singularities

x = symbols("x")


@pytest.mark.parametrize(
    ("arg", "point"),
    [(x, S.One), (x + 1, S.Zero), (x - 2, S(3)), (2*x, S.Half), (-x, -S.One), (x/3, S(3))],
)
def test_singularities_polylog_one_includes_log_singularity(arg, point):
    found = singularities(polylog(1, arg), x, S.Complexes)
    assert found.contains(point) == S.true
```

## Confidence

94%. The wrong output reproduces, the logarithmic identity independently proves the missing singularity, and the source-level diagnosis identifies the missing expansion/handler.
