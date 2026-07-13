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
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

x = symbols("x")
eq = Eq(asin(x), pi)
sol = solveset(eq, x, domain=S.Complexes)

print("solveset result:", sol)
print("residual at returned value 0:", simplify(eq.lhs.subs(x, 0) - eq.rhs.subs(x, 0)))
print("numeric residual:", N(eq.lhs.subs(x, 0) - eq.rhs.subs(x, 0), 50))
