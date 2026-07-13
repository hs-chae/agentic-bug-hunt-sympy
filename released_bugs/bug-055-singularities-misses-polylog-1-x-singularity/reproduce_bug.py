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
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

x = symbols("x")
expr = polylog(1, x)
sing = singularities(expr, x, S.Complexes)

print("expr =", expr)
print("singularities =", sing)
print("contains 1 =", sing.contains(1) if hasattr(sing, "contains") else "n/a")
print("value at 1 =", expr.subs(x, 1))
print("rewritten value at 1 =", (-log(1 - x)).subs(x, 1))
