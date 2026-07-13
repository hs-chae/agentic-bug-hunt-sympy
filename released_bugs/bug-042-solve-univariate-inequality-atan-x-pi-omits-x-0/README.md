### Candidate Bug 42: solve_univariate_inequality(atan(x) < pi) omits x = 0

**Status**

Confirmed

**SymPy version**

SymPy 1.14.0, checkout from `SYMPY_CHECKOUT_PATH`, `sympy.__file__` observed as `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`, Python executable `python3`.

**Minimal reproducer**

See `reproduce_bug.py`.

**Actual output**

`solution = Union(Interval.open(-oo, 0), Interval.open(0, oo)); 0 in solution = False`

**Expected output**

`S.Reals`, because real principal `atan(x)` is always less than `pi`.

**Why this is wrong**

For every real `x`, `atan(x)` lies in `(-pi/2, pi/2)`, so `atan(x) < pi`. In particular `atan(0)=0<pi`.

**Root cause**

The diagnosis locates a downstream interaction: `sympy/solvers/inequalities.py:520` asks `solvify` for equality roots, and `sympy/solvers/solveset.py:230-238` incorrectly supplies `0` for `atan(x)=pi`. The strict-inequality partition code then excludes that spurious critical point instead of validating the original inequality there. See `root_cause.md`.

**Independent verification**

`related_bugs.py` checks the representative inequality plus five related bounds. It independently evaluates `math.atan(point) < bound` at the omitted point.

**Additional instantiations**

The additional cases are `(3*pi/4, -1)`, `(2*pi, 0)`, `(5*pi/4, 1)`, `(10, tan(10))`, and `(3*pi, 0)`.

**Affected function or subsystem**

`solvers.inequalities / inverse trigonometric inequalities`; affected locations `sympy/solvers/inequalities.py:520`, `sympy/solvers/inequalities.py:572-658`, and `sympy/solvers/solveset.py:230-238`.

**Severity**

High

**Suggested regression test**

See `pr/tests/test_bug_042_solve_univariate_inequality_atan_x_pi_omits_x_0.py`.

**Confidence**

99%. The omitted point exactly satisfies the strict inequality and the internal root used to omit it is spurious.
