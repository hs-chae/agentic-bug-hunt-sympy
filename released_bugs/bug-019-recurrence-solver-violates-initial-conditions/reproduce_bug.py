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

n = symbols("n", integer=True)
y = Function("y")
rec = y(n + 2) - (n + 2)*y(n + 1) + y(n)
sol = rsolve(rec, y(n), {y(0): 1, y(1): 1})
print("rsolve output:", sol)
print("returned y(0):", sol.subs(n, 0))
print("returned y(1):", sol.subs(n, 1))
manual = [S(1), S(1)]
for i in range(4):
    manual.append((i + 2)*manual[-1] - manual[-2])
print("manual first terms:", manual)
