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

x = symbols("x")
sol = solveset(Eq(acsc(x), 3*pi/2), x, S.Complexes)

print("solveset(Eq(acsc(x), 3*pi/2), x, S.Complexes) =", sol)
for candidate in sol:
    print("candidate =", candidate)
    print("acsc(candidate) =", acsc(candidate))
    print("residual =", simplify(acsc(candidate) - 3*pi/2))
    print("numeric residual =", N(acsc(candidate) - 3*pi/2, 50))
