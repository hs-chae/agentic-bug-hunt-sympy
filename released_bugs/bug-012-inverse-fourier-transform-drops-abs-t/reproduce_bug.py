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


t, w = symbols("t w", real=True)
F = 2/(1 + 4*pi**2*w**2)
inv = inverse_fourier_transform(F, w, t)
print("inverse =", inv)
print("at t=-1:", inv.subs(t, -1))
print("expected at t=-1:", exp(-1))
print("difference:", simplify(inv.subs(t, -1) - exp(-1)))
