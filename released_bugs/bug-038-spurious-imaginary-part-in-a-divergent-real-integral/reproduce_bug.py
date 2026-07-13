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


x = symbols("x", real=True)
val = integrate(1/Abs(x), (x, -1, 0))
print("integral =", val)
print("truncated eps=1/10:", integrate(1/Abs(x), (x, -1, -Rational(1, 10))))
print("truncated eps=1/100:", integrate(1/Abs(x), (x, -1, -Rational(1, 100))))
