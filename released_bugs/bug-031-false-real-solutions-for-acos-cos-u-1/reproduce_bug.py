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

u = symbols("u")
eq = Eq(acos(cos(u)), -1)
sol = solveset(eq, u, S.Reals)
print("solveset =", sol)
for value in [1, -1]:
    print(f"residual at {value} =", simplify(acos(cos(value)) + 1))
    print(f"numeric residual at {value} =", N(acos(cos(value)) + 1, 50))
print("sample value acos(cos(0)) =", acos(cos(0)))
