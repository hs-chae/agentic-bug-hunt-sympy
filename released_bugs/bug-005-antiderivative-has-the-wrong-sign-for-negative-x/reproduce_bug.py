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

x = symbols("x")
integrand = sqrt(x**2 + 1)/x
F = integrate(integrand, x)
residual = diff(F, x) - integrand
print("antiderivative:", F)
print("integrand at -2:", integrand.subs(x, -2))
print("derivative at -2:", diff(F, x).subs(x, -2))
print("residual at -2:", simplify(residual.subs(x, -2)))
print("numeric residual:", N(residual.subs(x, -2), 50))
