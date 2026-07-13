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


x = symbols("x")
eq = Eq(atan2(x, 1), pi)
sol = solveset(eq, x, S.Reals)
print("solveset(Eq(atan2(x, 1), pi), x, S.Reals) =", sol)
print("residual at returned value 0 =", (eq.lhs - eq.rhs).subs(x, 0))
print("atan2(0, 1) =", atan2(0, 1))
