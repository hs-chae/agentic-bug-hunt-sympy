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

expr = lerchphi(x, 1, 1)
closed = -log(1 - x)/x
print("limit =", limit(expr, x, 1, dir="-"))
for v in [Rational(9, 10), Rational(999, 1000)]:
    print("sample", v, "lerchphi =", N(expr.subs(x, v), 50), "closed_form =", N(closed.subs(x, v), 50))
