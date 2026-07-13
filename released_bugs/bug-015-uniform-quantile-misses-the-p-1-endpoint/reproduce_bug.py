import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import FiniteSet, S
from sympy.stats import P, Uniform, cdf, quantile

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

U = Uniform("U", 0, 1)
actual = quantile(U)(S.One)
expected = FiniteSet(S.One)

print('quantile(Uniform("U", 0, 1))(1) =', actual)
print('cdf(Uniform("U", 0, 1))(1) =', cdf(U)(S.One))
print("P(U <= 1) =", P(U <= 1))
print("expected p=1 quantile =", expected)
print("matches expected =", actual == expected)
