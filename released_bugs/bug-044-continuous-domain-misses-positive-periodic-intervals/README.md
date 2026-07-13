# Candidate Bug 44: continuous_domain misses positive periodic intervals for sqrt(sin(x)) over the reals

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
from sympy.calculus.util import continuous_domain

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)

x = symbols("x")
dom = continuous_domain(sqrt(sin(x)), x, S.Reals)
print("domain =", dom)
print("contains 5*pi/2 =", dom.contains(5*pi/2))
print("value at 5*pi/2 =", sqrt(sin(x)).subs(x, 5*pi/2))
        ```

        **Actual output**

        ```text
        SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
domain = Interval(0, pi)
contains 5*pi/2 = False
value at 5*pi/2 = 1
        ```

        **Expected output**

        The domain should include every real interval where sin(x) >= 0, including 5*pi/2.

        **Why this is wrong**

        For real x, sqrt(sin(x)) is real-valued and continuous wherever sin(x) >= 0. Since sin(5*pi/2) = 1, a neighborhood of 5*pi/2 is in the real continuous domain.

        **Root cause**

        continuous_domain imposes the square-root constraint sin(x) >= 0 by calling solve_univariate_inequality. The inequality solver narrows an unbounded real periodic problem to one period and returns that fundamental-domain slice as the full answer, without lifting it over all periods. See `root_cause.md` for the full call path and source-level analysis.

        **Independent verification**

        `related_bugs.py` runs the representative case plus five additional instantiations and includes an independent numerical or direct-definition check for each case. On SymPy 1.14.0 it prints the failing details and exits with `Incorrect`.

        **Additional instantiations**

        The verification and regression-test files cover six total cases: the representative case plus `k = 5` additional instantiations of the same error pattern.

        **Affected function or subsystem**

        calculus / continuous_domain / periodic real domains. Affected source locations from diagnosis: sympy/calculus/util.py:116, sympy/solvers/inequalities.py:508.

        **Severity**

        Medium

        **Suggested regression test**

        See `pr/tests/test_bug_044_continuous-domain-misses-positive-periodic-intervals-for-sqr.py` for a single parametrized pytest covering the representative case and five additional instantiations.

        **Confidence**

        96%. The reproducer is minimal, direct substitution or definition-level checking shows the result is false, and the source-level diagnosis explains the mechanism.
