import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import N, Rational, besselj, diff, limit, series, symbols

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

print()
x = symbols("x")
expr = diff(besselj(1, x) / x, x)
print("expression:", expr)
print("actual limit:", limit(expr, x, 0))
print("expected limit:", 0)
print("series of besselj(1, x)/x:", series(besselj(1, x) / x, x, 0, 5))
print("series of derivative:", series(expr, x, 0, 5))
print("numeric derivative at x=1/1000:", N(expr.subs(x, Rational(1, 1000)), 50))
