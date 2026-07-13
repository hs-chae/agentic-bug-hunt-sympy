import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import Eq, Piecewise, symbols

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

x = symbols("x", real=True)
p = Piecewise((1, x > 0))

print("p.subs(x, -1) =", p.subs(x, -1))
print("(p*0).subs(x, -1) =", (p * 0).subs(x, -1))
print("(p-p).subs(x, -1) =", (p - p).subs(x, -1))
print("Eq(p, p).subs(x, -1) =", Eq(p, p).subs(x, -1))
