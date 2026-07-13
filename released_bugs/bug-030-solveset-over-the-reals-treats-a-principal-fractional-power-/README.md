# Candidate Bug 30: solveset over the reals treats principal fractional-power identity as true for negative inputs

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

x = symbols("x")
eq = Eq((x**2)**Rational(1, 3), x**Rational(2, 3))
sol = solveset(eq, x, S.Reals)
print("solveset(Eq((x**2)**Rational(1, 3), x**Rational(2, 3)), x, S.Reals) =", sol)
print("lhs at x = -1:", eq.lhs.subs(x, -1))
print("rhs at x = -1:", eq.rhs.subs(x, -1))
print("numeric residual at x = -1:", N(eq.lhs.subs(x, -1) - eq.rhs.subs(x, -1), 30))
```

## Actual output

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
solveset(Eq((x**2)**Rational(1, 3), x**Rational(2, 3)), x, S.Reals) = Reals
lhs at x = -1: 1
rhs at x = -1: (-1)**(2/3)
numeric residual at x = -1: 1.5 - 0.866025403784438646763723170753*I
```

## Expected output

The real solution set must exclude negative real numbers; in the representative case it is Interval(0, oo).

## Why this is wrong

Principal powers use the complex principal branch. For negative real x, ((x**2)**(1/3)) is positive real, while x**(2/3) is exp(2*pi*I/3)*abs(x)**(2/3), so the two sides differ.

## Root cause

`unrad` in `sympy/solvers/solvers.py:3535-3538` cubes both radical terms and turns `(x**2)**(1/3) = x**(2/3)` into the identity `x**2 = x**2`. `_solve_radical` accepts the resulting whole-domain solve without checking the lost branch condition. See `root_cause.md` for details.

## Independent verification

`related_bugs.py` exercises the representative case plus five additional instantiations and includes an independent numerical or definition-based oracle. On SymPy 1.14.0 it prints `Incorrect` and exits nonzero. The representative contradiction is: the returned `Reals` contains negative real values where principal complex powers disagree

## Additional instantiations

The single parametrized evidence file covers the representative case plus five additional instantiations of the same error pattern. The same case grid is mirrored in `pr/tests/test_bug_030_solveset_over_the_reals_treats_principal_fractional_power_id.py`.

## Affected function or subsystem

solvers.solveset / rational powers over real domains. Source-level diagnosis points to: sympy/solvers/solvers.py:3535-3538, sympy/solvers/solveset.py:_solve_radical.

## Severity

High

## Suggested regression test

See `pr/tests/test_bug_030_solveset_over_the_reals_treats_principal_fractional_power_id.py`. It is a single pytest parametrization covering the representative case and five additional instantiations, written with SymPy test-suite imports.

## Confidence

95%. The reproducer gives a direct false output and the independent verification checks the same contradiction with a separate mathematical oracle.
