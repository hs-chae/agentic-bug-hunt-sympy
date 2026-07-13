# Candidate Bug 45: singularities misses real poles of 1/((x**2)**(1/3) - 1)

## Status

Confirmed

## SymPy version

SymPy version: 1.14.0

SYMPY_CHECKOUT_PATH: `$SYMPY_CHECKOUT_PATH`

SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`

Python executable: `python3`

Commit hash: `None`

## Minimal reproducer

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

from sympy.calculus.singularities import singularities

x = symbols("x")
expr = 1/((x**2)**Rational(1, 3) - 1)
s = singularities(expr, x, S.Reals)
print("singularities(1/((x**2)**Rational(1, 3) - 1), x, S.Reals) =", s)
print("value at x = 1:", expr.subs(x, 1))
print("value at x = -1:", expr.subs(x, -1))
```

## Actual output

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
singularities(1/((x**2)**Rational(1, 3) - 1), x, S.Reals) = EmptySet
value at x = 1: zoo
value at x = -1: zoo
```

## Expected output

The real singularities include {-1, 1}.

## Why this is wrong

The denominator is zero whenever x**2 = 1. At x = -1 and x = 1 the reciprocal is infinite, so both points are real singularities.

## Root cause

`singularities` asks `solveset` for denominator zeros. In the real-domain path, the equation is rewritten to an absolute-value equation, and `_invert_abs` in `sympy/solvers/solveset.py:612-617` rejects an entire finite target set if any target is negative. It discards the valid `Abs(x) = 1` branch along with the invalid one. See `root_cause.md`.

## Independent verification

`related_bugs.py` exercises the representative case plus five additional instantiations and includes an independent numerical or definition-based oracle. On SymPy 1.14.0 it prints `Incorrect` and exits nonzero. The representative contradiction is: the reported singularity set omits points where the denominator is exactly zero

## Additional instantiations

The single parametrized evidence file covers the representative case plus five additional instantiations of the same error pattern. The same case grid is mirrored in `pr/tests/test_bug_045_singularities_misses_real_poles_of_1_x_2_1_3_1.py`.

## Affected function or subsystem

calculus singularities / principal rational powers. Source-level diagnosis points to: sympy/solvers/solveset.py:612-617, sympy/calculus/singularities.py:100-102.

## Severity

Medium

## Suggested regression test

See `pr/tests/test_bug_045_singularities_misses_real_poles_of_1_x_2_1_3_1.py`. It is a single pytest parametrization covering the representative case and five additional instantiations, written with SymPy test-suite imports.

## Confidence

94%. The reproducer gives a direct false output and the independent verification checks the same contradiction with a separate mathematical oracle.
