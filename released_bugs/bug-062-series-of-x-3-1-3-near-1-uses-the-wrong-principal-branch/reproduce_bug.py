import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *  # noqa: F401,F403

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

x = symbols("x")

expr = (x**3)**Rational(1, 3)
ser = series(expr, x, -1, 2)
print("series((x**3)**(1/3), x, -1, 2) =", ser)
print("value at x=-9/10 =", N(expr.subs(x, Rational(-9, 10)), 80))
print("series polynomial at x=-9/10 =", N(ser.removeO().subs(x, Rational(-9, 10)), 80))
print("limit at x=-1 =", limit(expr, x, -1))
