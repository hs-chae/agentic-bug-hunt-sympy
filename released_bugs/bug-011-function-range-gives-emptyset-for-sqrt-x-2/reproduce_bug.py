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

from sympy.calculus.util import function_range

x = symbols("x")
r = function_range(sqrt(x**2), x, S.Reals)
print("range:", r)
print("values:", sqrt((-2)**2), sqrt(0**2), sqrt(3**2))
print("contains 0:", r.contains(0))
print("contains 2:", r.contains(2))
