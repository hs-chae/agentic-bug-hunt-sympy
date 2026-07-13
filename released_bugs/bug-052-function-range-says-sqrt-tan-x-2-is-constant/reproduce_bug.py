import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import math
import sympy
from sympy import *  # noqa: F401,F403
from sympy.calculus.util import function_range

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not os.path.realpath(sympy.__file__).startswith(os.path.realpath(SYMPY_CHECKOUT_PATH)):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

x = symbols("x")
expr = sqrt(tan(x)**2)
actual = function_range(expr, x, Interval(-1, 1))
sample = Rational(1, 2)

print("function_range =", actual)
print("value_at_0 =", expr.subs(x, 0))
print("value_at_1_over_2 =", N(expr.subs(x, sample), 50))
print("range_contains_0 =", actual.contains(0))
print("python_abs_tan_half =", abs(math.tan(0.5)))
print("expected_range =", Interval(0, tan(1)))
