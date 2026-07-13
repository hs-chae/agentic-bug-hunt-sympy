import os
import sys


SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *  # noqa: F401,F403
from sympy.stats import P, Rayleigh, cdf


print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)

checkout_real = os.path.realpath(SYMPY_CHECKOUT_PATH)
sympy_file_real = os.path.realpath(sympy.__file__)
if not sympy_file_real.startswith(checkout_real + os.sep):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

R = Rayleigh("R", 1)

print("cdf(R)(-1):", cdf(R)(-1))
print("P(R <= -1):", P(R <= -1))
print("expected cdf below support:", 0)
print("incorrect:", cdf(R)(-1) != 0)
