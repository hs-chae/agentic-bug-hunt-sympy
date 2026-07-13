import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if SYMPY_CHECKOUT_PATH:
    sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *  # noqa: F401,F403

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if SYMPY_CHECKOUT_PATH and not os.path.abspath(sympy.__file__).startswith(os.path.abspath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

x = symbols("x")
eq = Eq(x**Rational(1, 3), -1)
sol = solveset(eq, x, S.Reals)
print("equation:", eq)
print("solveset:", sol)
for s in sol:
    print("candidate:", s)
    print("lhs at candidate:", eq.lhs.subs(x, s))
    print("residual:", simplify(eq.lhs.subs(x, s) - eq.rhs))
    print("numeric residual:", N(eq.lhs.subs(x, s) - eq.rhs, 30))
print("complex-domain solveset:", solveset(eq, x, S.Complexes))
