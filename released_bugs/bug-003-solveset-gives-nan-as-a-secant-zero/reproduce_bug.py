import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import S, cos, sec, solveset, symbols

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

x = symbols("x")

solution = solveset(sec(x), x, domain=S.Complexes)
print("solveset(sec(x), x, domain=S.Complexes) =", solution)
print("sec(nan) =", sec(S.NaN))
print("solveset(1/cos(x), x, domain=S.Complexes) =",
      solveset(1 / cos(x), x, domain=S.Complexes))
