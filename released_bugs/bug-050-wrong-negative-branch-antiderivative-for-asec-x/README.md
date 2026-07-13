# Candidate Bug 50: integrate(asec(x), x) differentiates to the wrong value on negative real inputs

**Status**

Confirmed

**SymPy version**

SymPy version: 1.14.0

SYMPY_CHECKOUT_PATH: `$SYMPY_CHECKOUT_PATH`

SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`

Python executable: `python3`

Commit hash: None; the supplied checkout is not a Git repository.

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

x = symbols("x", real=True)
residual = diff(integrate(asec(x), x), x) - asec(x)
print("residual at x=-2:", simplify(residual.subs(x, -2)))
print("numeric residual:", N(residual.subs(x, -2), 50))
```

**Actual output**

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
residual at x=-2: -2*sqrt(3)/3
numeric residual: -1.1547005383792515290182975610039149112952035025403
```

**Expected output**

The residual `diff(integrate(asec(x), x), x) - asec(x)` should be `0` at `x = -2`.

**Why this is wrong**

An antiderivative `F` of `asec(x)` must satisfy `F'(x) = asec(x)` on any open interval where the branch is smooth. The point `x = -2` lies inside the nonsingular real interval `(-oo, -1)`, away from the branch endpoint. SymPy's exact residual is `-2*sqrt(3)/3`, so the returned expression is not an antiderivative there.

The integration-by-parts identity reduces the integral to `x*asec(x) - Integral(1/(x*sqrt(1 - 1/x**2)), x)`. On `x < -1`, the subintegrand is negative and a real primitive is `acosh(Abs(x))`, whose derivative is `-1/sqrt(x**2 - 1)`. SymPy instead uses a branch proportional to `x*acosh(Abs(x))/Abs(x)`, which differentiates with the opposite sign on `x < -1`.

**Root cause**

The source-level diagnosis locates the branch error in `sympy/functions/special/hyper.py:841`, through `HyperRep._eval_rewrite_as_nonrep`, with the responsible continuation formula in `HyperRep_asin1._expr_big` at `sympy/functions/special/hyper.py:971-973`. The public `integrate(asec(x), x)` call enters manual integration by parts, leaves a radical subintegral, and then the Meijer-G integration path calls `hyperexpand`; the hypergeometric representative splits only on `abs(x) > 1` and produces an `x/Abs(x)` multiplier that flips the derivative on the negative real branch. See `root_cause.md` for the full call path and mechanism.

**Independent verification**

`related_bugs.py` checks six inputs exactly and also uses `mpmath` to numerically differentiate the returned primitive, then compares that derivative with the independent real formula `asec(t) = acos(1/t)`. For `t = -2`, the independent numerical residual is approximately `-1.15470053837925`, matching the exact residual `-2*sqrt(3)/3` and confirming the failure is not a simplification artifact.

**Additional instantiations**

The same error is included as parametrized runnable cases for `x = -3`, `x = -3/2`, `x = -4`, `x = -5/2`, and `x = -10` in `related_bugs.py` and in the proposed regression test under `pr/tests/`.

**Related issues**

This is a specific-new instance of a known family, not a fully novel failure. The `integrate(asec(x), x)` capability under test was added by PR #19993 ("upgrades to manualintegrate", merged 2020-09-02, https://github.com/sympy/sympy/pull/19993), which closed issue #14329 ("Integration of asec and acsc", https://github.com/sympy/sympy/issues/14329) and issue #19983 ("Sympy doesn't Integrate when expr contains asec / acsc", https://github.com/sympy/sympy/issues/19983); #14329 already shows the `Piecewise`/`acosh` shape whose `real=True` variant is the buggy primitive here. The same wrong-real-branch Meijer/`acosh` mechanism is reported in the still-open issue #10453 ("integrate return wrong answer (inverse trigonometric functions).", https://github.com/sympy/sympy/issues/10453). What remains unreported is this exact instance: a nonzero derivative residual (e.g. `-2*sqrt(3)/3` at `x = -2`) on the smooth negative real branch `x < -1`.

**Affected function or subsystem**

Integration / inverse trigonometric antiderivatives. Diagnosed source locations: `sympy/functions/special/hyper.py:841` and `sympy/functions/special/hyper.py:971-973`, reached from the Meijer-G indefinite integration path after `manualintegrate(asec(x), x)` leaves the radical subintegral.

**Severity**

High. SymPy returns a mathematically false antiderivative on an entire real interval, not just at an endpoint or removable singularity.

**Suggested regression test**

```python
import pytest

from sympy import S, asec, diff, integrate, simplify, symbols


@pytest.mark.parametrize(
    "value",
    [
        S(-2),
        S(-3),
        -S(3) / 2,
        S(-4),
        -S(5) / 2,
        S(-10),
    ],
)
def test_integrate_asec_antiderivative_on_negative_real_branch(value):
    x = symbols("x", real=True)
    residual = diff(integrate(asec(x), x), x) - asec(x)
    assert simplify(residual.subs(x, value)) == 0
```

**Confidence**

93%. The residual is exact, reproduces on multiple points in the same interval, is confirmed by independent high-precision numerical differentiation, and the source-level diagnosis identifies the branch-sign mechanism.
