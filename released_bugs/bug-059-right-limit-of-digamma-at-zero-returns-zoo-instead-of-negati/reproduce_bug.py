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

import mpmath as mp
mp.mp.dps = 80

expr = polygamma(0, x)
print("limit(polygamma(0, x), x, 0, dir='+') =", limit(expr, x, 0, dir="+"))
print("value at x=1/10**20 =", N(expr.subs(x, Rational(1, 10)**20), 80))
print("mpmath digamma(1e-20) =", mp.digamma(mp.mpf("1e-20")))
