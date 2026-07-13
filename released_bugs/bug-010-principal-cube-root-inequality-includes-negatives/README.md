# Candidate Bug 10: solve_univariate_inequality includes negative reals for a principal cube-root inequality

## Status

Confirmed

## SymPy version

SymPy version: 1.14.0  
SYMPY_CHECKOUT_PATH: `$SYMPY_CHECKOUT_PATH`  
SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`  
Python executable: `python3`  
Commit hash: None

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
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

from sympy.solvers.inequalities import solve_univariate_inequality

x = symbols("x")
sol = solve_univariate_inequality(x**(S(1)/3) <= 1, x, relational=False)
print("solution:", sol)
print("contains_minus_one:", sol.contains(-1))
print("lhs_at_minus_one:", N((-1)**(S(1)/3), 30))
```

## Actual output

```text
solution: Interval(-oo, 1); contains_minus_one: True; lhs_at_minus_one: 0.5 + 0.866025403784438646763723170753*I
```

## Expected output

Interval(0, m**3).

## Why this is wrong

A real inequality can only include points where both sides define ordered real values. Negative real inputs make the principal fractional power complex.

## Root cause

continuous_domain assumes odd-denominator fractional powers are real-valued on all real bases, so the inequality solver samples and accepts an interval containing negative inputs. The missing domain restriction comes from principal Pow semantics; see root_cause.md.

## Independent verification

Run `related_bugs.py`. It covers the representative case plus five additional instantiations and includes an independent numerical/definition-based oracle for the same mathematical claim. On SymPy 1.14.0 it prints `Incorrect` and exits with failure.

## Additional instantiations

The bundled `related_bugs.py` and `pr/tests/test_bug_010_solve_univariate_inequality_includes_negative_reals_for_a_pr.py` use six parametrized cases total: the representative case plus five additional instantiations of the same error pattern.

## Affected function or subsystem

Subsystem: solvers.inequalities / fractional powers / real-domain filtering  
Affected locations from diagnosis: sympy/calculus/util.py:111, sympy/solvers/inequalities.py:563

## Severity

High

## Suggested regression test

See `pr/tests/test_bug_010_solve_univariate_inequality_includes_negative_reals_for_a_pr.py` for a single parametrized pytest test following SymPy test-suite conventions.

## Confidence

96%. The reproducer is minimized, the wrong output is deterministic, and the diagnosis identifies the responsible source-level path.
