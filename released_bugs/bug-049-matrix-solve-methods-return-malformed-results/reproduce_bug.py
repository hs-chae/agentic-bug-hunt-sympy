import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import Matrix

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)
if not sympy.__file__.startswith(SYMPY_CHECKOUT_PATH):
    raise RuntimeError("SymPy was not imported from SYMPY_CHECKOUT_PATH")

A = Matrix([[1, 1], [2, 2]])
b = Matrix([1, 2])

print("rank(A):", A.rank())
print("rank([A|b]):", A.row_join(b).rank())
print("gauss_jordan_solve:", A.gauss_jordan_solve(b))

for method in ["QR", "LDL", "CRAMER"]:
    try:
        sol = A.solve(b, method=method)
        print(method, sol, sol.shape)
    except Exception as exc:
        print(method, type(exc).__name__, exc)
