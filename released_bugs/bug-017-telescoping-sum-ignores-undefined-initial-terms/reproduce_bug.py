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

k = symbols("k", integer=True)
s = Sum(1/(k*(k - 1)), (k, 0, oo))
print("actual_sum =", s.doit())
print("first_terms =", [s.function.subs(k, i) for i in range(5)])
print("tail_sum_from_2 =", Sum(1/(k*(k - 1)), (k, 2, oo)).doit())
