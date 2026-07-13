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

t = symbols("t", real=True)
s = symbols("s", positive=True)
a = symbols("a")

with_conditions = laplace_transform(Heaviside(a - t), t, s, noconds=False)
symbolic_transform = laplace_transform(Heaviside(a - t), t, s, noconds=True)
actual_at_two = symbolic_transform.subs(a, 2)
expected_at_two = integrate(exp(-s*t), (t, 0, 2))

print("laplace_transform(Heaviside(a - t), t, s, noconds=False) =", with_conditions)
print("laplace_transform(Heaviside(a - t), t, s, noconds=True) =", symbolic_transform)
print("after substituting a = 2 =", actual_at_two)
print("direct integral from 0 to 2 =", expected_at_two)
print("difference =", simplify(actual_at_two - expected_at_two))
print("matches expected =", simplify(actual_at_two - expected_at_two) == 0)
