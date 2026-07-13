# Fix singularities returns EmptySet for gamma(x) although x = 0 is a pole

        ## Summary

        SymPy currently reports an incorrect result for `singularities(gamma(x), x, S.Complexes)`. The returned output contradicts direct substitution and independent numerical checks.

        ## Reproducer

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

        ## Actual behavior

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

        ## Expected behavior

        A set containing all nonpositive integers, in particular 0; gamma has a simple pole at x = 0.

        ## Evidence

        The Laurent expansion gamma(x)=1/x-EulerGamma+O(x) proves a simple pole at 0. Direct evaluation gives zoo and residue returns 1, so EmptySet is mathematically false.

        The artifact `related_bugs.py` covers the representative case plus five additional instantiations and exits with `Incorrect` on the current checkout.

        ## Suggested regression test

        See `pr/tests/test_bug_054_singularities_returns_emptyset_for_gamma_x_although_x_0_is_a.py` for a single parametrized pytest test that can be adapted into SymPy's test suite.
