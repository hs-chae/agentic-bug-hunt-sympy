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
eq = Eq((x**2)**Rational(1, 3), x**Rational(2, 3))
sol = solveset(eq, x, S.Reals)
print("solveset(Eq((x**2)**Rational(1, 3), x**Rational(2, 3)), x, S.Reals) =", sol)
print("lhs at x = -1:", eq.lhs.subs(x, -1))
print("rhs at x = -1:", eq.rhs.subs(x, -1))
print("numeric residual at x = -1:", N(eq.lhs.subs(x, -1) - eq.rhs.subs(x, -1), 30))
