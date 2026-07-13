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

a, b = symbols("a b")
M = Matrix([[a, 1], [0, b]])
print("is_diagonalizable:", M.is_diagonalizable())
P, D = M.diagonalize()
print("P:", P)
print("D:", D)
M_equal = M.subs(b, a)
print("specialized matrix:", M_equal)
print("specialized is_diagonalizable:", M_equal.is_diagonalizable())
