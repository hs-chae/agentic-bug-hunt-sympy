### Candidate Bug 54: singularities returns EmptySet for gamma(x) although x = 0 is a pole

        **Status**

        Confirmed

        **SymPy version**

        SymPy version: `1.14.0`

        SYMPY_CHECKOUT_PATH: `$SYMPY_CHECKOUT_PATH`

        SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`

        Python executable: `python3`

        **Minimal reproducer**

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

from sympy.calculus.singularities import singularities

x = symbols("x")
s = singularities(gamma(x), x, S.Complexes)
print("singularities =", s)
print("contains 0 =", s.contains(0))
print("gamma(0) =", gamma(0))
print("residue at 0 =", residue(gamma(x), x, 0))
print("series at 0 =", series(gamma(x), x, 0, 1))
        ```

        **Actual output**

        ```text
        SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
singularities = EmptySet
contains 0 = False
gamma(0) = zoo
residue at 0 = 1
series at 0 = 1/x - EulerGamma + O(x)
        ```

        **Expected output**

        A set containing all nonpositive integers, in particular 0; gamma has a simple pole at x = 0.

        **Why this is wrong**

        The Laurent expansion gamma(x)=1/x-EulerGamma+O(x) proves a simple pole at 0. Direct evaluation gives zoo and residue returns 1, so EmptySet is mathematically false.

        **Root cause**

        The diagnosis localizes the miss to the syntactic scanner in `sympy/calculus/singularities.py:94-108`. The scanner handles negative powers and a small list of log/inverse-hyperbolic atoms, but it has no rule for `gamma` finite poles and does not use `gamma.eval`'s knowledge of nonpositive integer poles. See `root_cause.md` for the full trace.

        **Independent verification**

        `related_bugs.py` checks the representative pole and five shifted gamma poles. It also evaluates mpmath's gamma function near the pole, where the magnitude grows like `1/eps`, independently confirming a pole. On the buggy version it prints `Incorrect` and exits nonzero.

        **Additional instantiations**

        The same error pattern is verified for `gamma(x + 1)` at `x = -1`, `gamma(x + 2)` at `x = -2`, `gamma(x - 1)` at `x = 1`, `gamma(x + 3)` at `x = -3`, and `gamma(x - 2)` at `x = 2`.

        **Affected function or subsystem**

        calculus / singularities / special functions: `sympy/calculus/singularities.py:94-108`, `sympy/functions/special/gamma_functions.py:112`, `sympy/functions/special/gamma_functions.py:127-131`.

        **Severity**

        Medium. SymPy returns a mathematically incorrect result for an exact symbolic query.

        **Suggested regression test**

        See `pr/tests/test_bug_054_singularities_returns_emptyset_for_gamma_x_although_x_0_is_a.py`. It is a single parametrized pytest test covering the representative case plus five additional instantiations.

        **Confidence**

        99%. The Laurent expansion and mpmath near-pole behavior are definitive, and the diagnosis identifies the scanner omission.
