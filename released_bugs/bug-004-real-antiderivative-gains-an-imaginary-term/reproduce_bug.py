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

x = symbols("x")
f = log(x)/(x**2 - 1)
F = integrate(f, x)
residual = simplify(diff(F, x) - f)
print("integrate(log(x)/(x**2 - 1), x) =", F)
print("diff(integral, x) - log(x)/(x**2 - 1) =", residual)
print("residual at x=2 =", N(residual.subs(x, 2), 50))
