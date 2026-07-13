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
