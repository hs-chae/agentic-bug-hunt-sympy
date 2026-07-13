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
if SYMPY_CHECKOUT_PATH and not os.path.abspath(sympy.__file__).startswith(os.path.abspath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

x, k = symbols("x k", real=True)
expr = cos(x) / (x**2 + 1)
F = fourier_transform(expr, x, k)
value = Rational(-1, 3)
expected = pi * (exp(-Abs(2*pi*value - 1)) + exp(-Abs(2*pi*value + 1))) / 2

print("transform:", F)
print("SymPy at k=-1/3:", N(F.subs(k, value), 50))
print("shift-theorem expected:", N(expected, 50))
print("difference:", N(F.subs(k, value) - expected, 50))
