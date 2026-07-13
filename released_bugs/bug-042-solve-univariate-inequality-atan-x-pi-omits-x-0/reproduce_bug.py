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

from sympy.solvers.inequalities import solve_univariate_inequality

x = symbols("x")
sol = solve_univariate_inequality(atan(x) < pi, x, relational=False)
print("solution =", sol)
print("0 in solution =", S.Zero in sol)
print("atan(0) < pi evaluates to", atan(S.Zero) < pi)
print("numeric atan(0) - pi =", N(atan(S.Zero) - pi, 50))
