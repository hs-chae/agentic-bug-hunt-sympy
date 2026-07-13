import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *  # noqa: F401,F403
from sympy.calculus.singularities import singularities

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

x = symbols("x")
result = singularities(zeta(x), x, S.Complexes)
print("singularities(zeta(x), x, S.Complexes) =", result)
print("1 in result =", result.contains(S.One))
print("zeta(1) =", zeta(1))
print("limit(zeta(x), x, 1) =", limit(zeta(x), x, 1))
