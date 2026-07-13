# Candidate Bug 52: function_range says sqrt(tan(x)**2) is constant on [-1, 1]

**Status**

Confirmed

**SymPy version**

SymPy 1.14.0.

`SYMPY_CHECKOUT_PATH`: `$SYMPY_CHECKOUT_PATH`

SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`

Python executable: `python3`

**Minimal reproducer**

```python
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

x = symbols("x")
expr = sqrt(tan(x)**2)
actual = function_range(expr, x, Interval(-1, 1))

print("function_range =", actual)
print("value_at_0 =", expr.subs(x, 0))
print("value_at_1_over_2 =", N(expr.subs(x, Rational(1, 2)), 50))
print("range_contains_0 =", actual.contains(0))
print("python_abs_tan_half =", abs(math.tan(0.5)))
print("expected_range =", Interval(0, tan(1)))
```

**Actual output**

```text
function_range = {tan(1)}
value_at_0 = 0
value_at_1_over_2 = 0.54630248984379051325517946578028538329755172017979
range_contains_0 = False
python_abs_tan_half = 0.5463024898437905
expected_range = Interval(0, tan(1))
```

**Expected output**

`Interval(0, tan(1))`.

**Why this is wrong**

On `[-1, 1]`, `sqrt(tan(x)**2) = Abs(tan(x))`. The tangent function is continuous and strictly increasing on this interval, so the absolute value has minimum `0` at `x = 0` and maximum `tan(1)` at the endpoints.

**Root cause**

The diagnosis located the source issue in `sympy/calculus/util.py:260`. `function_range` samples interval endpoints and derivative zeros, but it does not include points where the derivative is undefined while the original function is continuous. For this expression the derivative is undefined at `x = 0`, so the only sampled value is the endpoint value `tan(1)`. See `root_cause.md`.

**Independent verification**

`related_bugs.py` checks the original interval and five smaller intervals. It also compares sample values against Python's `math.tan`, showing that interior values such as `Abs(tan(bound/2))` are real range values excluded by SymPy's singleton result.

**Additional instantiations**

Five additional interval bounds are included in `related_bugs.py` and mirrored in `pr/tests/test_bug_052_function_range_says_sqrt_tan_x_2_is_constant_on_1_1.py`.

**Affected function or subsystem**

`sympy/calculus/util.py:function_range`, especially the critical-point collection near lines 253-281.

**Severity**

Medium

**Suggested regression test**

See `pr/tests/test_bug_052_function_range_says_sqrt_tan_x_2_is_constant_on_1_1.py`.

**Confidence**

93%. The expected range follows from monotonicity of `tan` on the tested intervals and is confirmed by direct numerical samples.
