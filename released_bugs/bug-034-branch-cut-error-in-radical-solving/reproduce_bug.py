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

checkout_real = os.path.realpath(SYMPY_CHECKOUT_PATH)
sympy_file_real = os.path.realpath(sympy.__file__)
if not sympy_file_real.startswith(checkout_real + os.sep):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

x = symbols("x")
sol = solveset(Eq(sqrt(1/x), 1/sqrt(x)), x, domain=S.Complexes)

print("solution:", sol)
print("contains -1:", sol.contains(S.NegativeOne))
print("lhs at -1:", sqrt(1/x).subs(x, -1))
print("rhs at -1:", (1/sqrt(x)).subs(x, -1))
print("residual at -1:", (sqrt(1/x) - 1/sqrt(x)).subs(x, -1))
