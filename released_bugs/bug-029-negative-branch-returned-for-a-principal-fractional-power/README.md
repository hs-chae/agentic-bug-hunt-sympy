# Candidate Bug 29: solveset over the reals returns a negative solution for principal x**(2/3) = 4

## Status

Confirmed

## SymPy version

- SymPy version: 1.14.0
- SYMPY_CHECKOUT_PATH: `$SYMPY_CHECKOUT_PATH`
- SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`
- Python executable: `python3`
- Commit hash: None

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
sol = solveset(Eq(x**Rational(2, 3), 4), x, S.Reals)
print("solution =", sol)
for s in sol:
    residual = (x**Rational(2, 3) - 4).subs(x, s)
    print("residual at", s, "=", simplify(residual))
    print("numeric residual at", s, "=", N(residual, 50))
```

## Actual output

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
solution = {-8, 8}
residual at -8 = -4 + 4*(-1)**(2/3)
numeric residual at -8 = -6.0 + 3.4641016151377545870548926830117447338856105076208*I
residual at 8 = 0
numeric residual at 8 = 0
```

## Expected output

The real-domain solution set should be {8}; -8 is not a solution for SymPy principal powers.

## Why this is wrong

SymPy Pow uses the principal complex branch for negative bases with non-integer rational exponents. Therefore (-8)**(2/3) = 4*(-1)**(2/3) = -2 + 2*sqrt(3)*I, not 4. A real-domain solve result must satisfy the original equation when substituted back.

## Root cause

The diagnosis locates the fault in sympy/solvers/solveset.py:284-289, in _invert_real. For exponent 2/3, the rational-power inverse branch returns both y**(3/2) and -y**(3/2), which is the inverse of real-root semantics rather than principal Pow semantics. No residual check removes the invalid negative branch. See `root_cause.md` for the full source-level diagnosis.

## Independent verification

`related_bugs.py` runs the representative case plus five additional instantiations. It also evaluates each case against an independent numerical or direct-definition oracle (`mpmath`, `cmath`, or Python `math.comb`, depending on the subsystem). On the current buggy version it prints `Incorrect` and exits nonzero.

## Additional instantiations

The runnable verification file and regression test cover 6 total cases: the representative case plus 5 additional instantiations of the same error pattern.

## Affected function or subsystem

Subsystem: solvers.solveset / real-domain fractional powers

Affected locations from diagnosis:
- `sympy/solvers/solveset.py:284-289 (_invert_real rational-power branch)`
- `sympy/solvers/solveset.py:1057-1062 (_solveset calls invert_real on x**(2/3))`

## Severity

High

## Suggested regression test

See `pr/tests/test_bug_029_solveset-over-the-reals-returns-a-negative-solution-for-prin.py`. It is a single parametrized pytest file using SymPy maintenance-test conventions.

## Confidence

96%. The reproducer is minimal, substitution/direct numerical checks are decisive, and the diagnosis identifies a concrete source-level mechanism.
