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

x = symbols("x")
f = Function("f")
C1 = symbols("C1")
ode = Eq(diff(f(x), x), sqrt(f(x)**2))
sol = dsolve(ode)
rhs = sol[0].rhs.subs(C1, 1)
residual = diff(rhs, x) - sqrt(rhs**2)

print("dsolve result:", sol)
print("chosen returned branch with C1=1:", rhs)
print("residual:", simplify(residual))
print("residual at x=0:", N(residual.subs(x, 0), 50))
