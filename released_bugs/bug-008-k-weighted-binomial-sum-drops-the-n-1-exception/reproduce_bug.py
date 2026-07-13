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

n = symbols("n", integer=True, nonnegative=True)
k = symbols("k", integer=True)
closed = summation((-1)**k*k*binomial(n, k), (k, 0, n))
direct_n1 = sum(((-1)**j)*j*binomial(1, j) for j in range(0, 2))
print("closed form =", closed)
print("closed at n=1 =", closed.subs(n, 1))
print("direct finite sum at n=1 =", direct_n1)
print("difference =", closed.subs(n, 1) - direct_n1)
