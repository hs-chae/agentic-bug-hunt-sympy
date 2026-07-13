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
if not os.path.abspath(sympy.__file__).startswith(os.path.abspath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

from sympy.assumptions import Q, ask

xr = symbols("xr", real=True)
expr = 1/(xr - 1)
print("ask(Q.extended_real(expr)) =", ask(Q.extended_real(expr)))
print("expr.subs(xr, 1) =", expr.subs(xr, 1))
print("substituted value is_extended_real =", expr.subs(xr, 1).is_extended_real)
