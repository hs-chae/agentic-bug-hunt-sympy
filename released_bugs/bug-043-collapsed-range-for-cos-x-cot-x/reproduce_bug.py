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

from sympy.calculus.util import continuous_domain, function_range

x = symbols("x")
expr = cos(x)/cot(x)
dom = continuous_domain(expr, x, S.Reals)
rng = function_range(expr, x, S.Reals)
print("continuous_domain(cos(x)/cot(x), x, S.Reals) =", dom)
print("function_range(cos(x)/cot(x), x, S.Reals) =", rng)
print("value at pi/3 =", expr.subs(x, pi/3))
print("range contains sqrt(3)/2 =", rng.contains(sqrt(3)/2))
print("value at pi/2 =", expr.subs(x, pi/2))
