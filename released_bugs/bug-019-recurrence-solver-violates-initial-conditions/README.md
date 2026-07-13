# Candidate Bug 19: rsolve returns a solution that violates supplied initial conditions

**Status**

Confirmed

**SymPy version**

SymPy 1.14.0, commit `None`, imported from `$SYMPY_CHECKOUT_PATH/sympy/__init__.py` with `python3`.

**Minimal reproducer**

See `reproduce_bug.py`.

**Actual output**

```text
rsolve output: 0
returned y(0): 0
returned y(1): 0
manual first terms: [1, 1, 1, 2, 7, 33]
```

**Expected output**

The solver should return a sequence satisfying `y(0)=1` and `y(1)=1`, or report that it cannot solve the recurrence with these initial conditions.

**Why this is wrong**

The returned expression is the zero sequence, so direct substitution gives `y(0)=0` and `y(1)=0`, contradicting the user-supplied initial conditions. Independent forward recurrence from those initial terms gives `1, 1, 1, 2, 7, 33`.

**Root cause**

The source-level diagnosis locates the bug in `sympy/solvers/recurr.py:rsolve`, around lines `816-841`. `rsolve_hyper` returns the constant-free candidate `0` with `symbols=[]`; because the IC application block is guarded by `if symbols and init is not None`, the supplied initial conditions are skipped and no final validation rejects the result. See `root_cause.md`.

This is the IC-validation-skip lens on the known `rsolve`-returns-`0` failure family (see "Related issues" below); it is not a previously-unknown failure mode.

**Independent verification**

`related_bugs.py` exercises the representative recurrence and five variants `y(n+2) - (n+a)y(n+1) + y(n) = 0` for `a = 3, 4, 5, 6, 7`. It compares the returned solution with the defining initial conditions and independently generates forward recurrence terms.

**Additional instantiations**

Five additional values of `a` are included in `related_bugs.py` and the PR regression test.

**Related issues**

This is the same `rsolve_hyper`-returns-`0` failure family already reported in open public issues, not a novel defect:

- https://github.com/sympy/sympy/issues/27902 — "rsolve: Gives 0 for higher order recurrences" (most direct match; same second-order variable-coefficient `rsolve` -> `0` symptom).
- https://github.com/sympy/sympy/issues/17982 — "Wrong result from rsolve".
- https://github.com/sympy/sympy/issues/11063 — "Some wrong answers from rsolve".

Bug-019's specific contribution is the IC-validation-skip lens: the constant-free `0` candidate causes the `if symbols and init is not None` block to be bypassed, so supplied initial conditions are never checked.

**Affected function or subsystem**

`sympy/solvers/recurr.py:rsolve`, especially lines `816-841`.

**Severity**

High

**Suggested regression test**

`pr/tests/test_bug_019_rsolve_returns_a_solution_that_violates_supplied_initial_con.py`

**Confidence**

95%. The returned expression directly violates explicit initial conditions, and the source path skipping validation is identified.
