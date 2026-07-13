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

x = symbols("x", real=True)
p = Piecewise((0, x < 0), (1, True))
print("limit(Piecewise((0, x < 0), (1, True)), x, 0, dir='-') =", limit(p, x, 0, dir="-"))
print("left sample p.subs(x, -1/10) =", p.subs(x, Rational(-1, 10)))
print("right sample p.subs(x, 1/10) =", p.subs(x, Rational(1, 10)))
