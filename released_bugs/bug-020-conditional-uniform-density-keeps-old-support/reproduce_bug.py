import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import S, integrate, oo, symbols
from sympy.stats import P, Uniform, density, given

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

x = symbols("x")
U = Uniform("U", 0, 1)
Y = given(U, U > S.Half)
d = density(Y)(x)

print()
print("density:", d)
print("total mass:", integrate(d, (x, -oo, oo)))
print("mass below 1/2 from density:", integrate(d, (x, 0, S.Half)))
print("P(Y < 1/2):", P(Y < S.Half))
