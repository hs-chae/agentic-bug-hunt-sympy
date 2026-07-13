import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if SYMPY_CHECKOUT_PATH:
    sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *  # noqa: F401,F403

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if SYMPY_CHECKOUT_PATH and not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

x, y = symbols("x y")
eqs = [(x*y - x)/(x - 1) - y, y - 1]
sol = nonlinsolve(eqs, [x, y])

print("nonlinsolve result =", sol)
for candidate in sol:
    print("candidate =", candidate)
    print("residuals =", [eq.subs({x: candidate[0], y: candidate[1]}) for eq in eqs])
print("direct left side at (1, 1) =", ((x*y - x)/(x - 1)).subs({x: 1, y: 1}))
print("direct equation at (1, 1) =", Eq(((x*y - x)/(x - 1)).subs({x: 1, y: 1}), 1))
print("cleared numerator equation =", expand((x*y - x) - y*(x - 1)))
print("denominator at (1, 1) =", (x - 1).subs(x, 1))
