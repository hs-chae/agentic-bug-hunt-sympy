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


x = symbols("x")
integrand = 1/(x*sqrt(x**2 - 1))
F = integrate(integrand, x)
dF = diff(F, x)
print("antiderivative =", F)
print("derivative =", dF)
print("integrand at x=-3:", N(integrand.subs(x, -3), 50))
print("derivative at x=-3:", N(dF.subs(x, -3), 50))
print("difference:", N((dF - integrand).subs(x, -3), 50))
