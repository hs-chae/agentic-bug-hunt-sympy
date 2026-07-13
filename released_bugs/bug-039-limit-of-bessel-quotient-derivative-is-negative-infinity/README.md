# Candidate Bug 39: Limit of derivative of besselj(1, x)/x is -oo instead of 0

**Status**

Confirmed

**SymPy version**

SymPy version: `1.14.0`

`SYMPY_CHECKOUT_PATH`: `$SYMPY_CHECKOUT_PATH`

SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`

Python executable: `python3`

Commit hash: `None`

**Minimal reproducer**

```python
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)

x = symbols("x")
expr = diff(besselj(1, x) / x, x)
print("actual limit:", limit(expr, x, 0))
print("expected limit:", 0)
print("series of derivative:", series(expr, x, 0, 5))
```

**Actual output**

```text
actual limit: -oo
expected limit: 0
series of derivative: -x/8 + x**3/96 + O(x**5)
```

**Expected output**

The limit should be `0`.

**Why this is wrong**

The Taylor expansion is `J_1(x) = x/2 - x**3/16 + x**5/384 + O(x**7)`.
Therefore `J_1(x)/x = 1/2 - x**2/16 + x**4/384 + O(x**6)`, and differentiating
gives `d/dx(J_1(x)/x) = -x/8 + x**3/96 + O(x**5)`. This tends to `0` as
`x -> 0`, not to negative infinity.

**Root cause**

The source-level diagnosis locates the bad step in
`sympy/core/add.py:1067-1078`, inside `Add._eval_as_leading_term`. The public
call differentiates through `BesselBase.fdiff` in
`sympy/functions/special/bessel.py:66-70`, which produces a correct derivative,
then `Limit.doit` in `sympy/series/limits.py:304-312` asks for a leading term.
After the `1/(2*x)` and `-1/(2*x)` terms cancel, the cancellation fallback asks
`_eval_nseries` for order `n = 0`, which is too low to expose the next nonzero
term `-x/8`. The truncated result leaves a spurious `-1/(2*x)` leading term,
so the limit machinery returns `-oo`. See `root_cause.md` for the full call
path and line-level analysis.

**Independent verification**

`related_bugs.py` uses mpmath's Bessel implementation and the
identity `J_1'(z) = (J_0(z) - J_2(z))/2` to evaluate
`d/dx J_1(c*x)/x` near zero without using SymPy's limit algorithm. For each
case, the numerical value at `x = 1e-6` agrees with the hand-derived leading
term `-c**3*x/8`, which tends to zero, while SymPy reports `-oo`.

**Additional instantiations**

The same error pattern is included in `related_bugs.py` and the
regression test for `c = 1/2, 3/2, 3, 4, 5` in
`limit(diff(besselj(1, c*x)/x, x), x, 0)`.

**Affected function or subsystem**

Limits and leading-term computation for special functions:
`sympy/core/add.py:1067-1078` (`Add._eval_as_leading_term`), reached from
`sympy/series/limits.py:304-312` after differentiating through
`sympy/functions/special/bessel.py:66-70`.

**Severity**

Medium

SymPy returns a mathematically false infinite limit for an analytic expression
with a finite zero limit. The failure is localized to a cancellation-sensitive
special-function limit but can affect users relying on symbolic asymptotics.

**Suggested regression test**

```python
import pytest

from sympy import Rational, besselj, diff, limit, symbols


@pytest.mark.parametrize("c", [1, Rational(1, 2), Rational(3, 2), 3, 4, 5])
def test_limit_derivative_scaled_besselj1_quotient(c):
    x = symbols("x")
    expr = diff(besselj(1, c * x) / x, x)

    assert limit(expr, x, 0) == 0
```

**Confidence**

96%. The Taylor expansion, SymPy's own series output, mpmath numerical checks,
and source-level diagnosis all agree that the limit should be zero and that the
reported infinity is introduced by an insufficient leading-term expansion after
cancellation.
