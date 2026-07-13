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

import cmath
import math

expr = sinh(I*pi + I*(pi - 1))
combined = sinh(I*(2*pi - 1))
print("sinh(I*pi + I*(pi - 1)) =", expr)
print("sinh(I*(2*pi - 1)) =", combined)
print("difference =", simplify(expr - combined))
print("cmath expected =", cmath.sinh(1j*(2*math.pi - 1)))
