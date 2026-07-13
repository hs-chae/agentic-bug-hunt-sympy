# Fix solve_univariate_inequality(atan(x) < pi) omitting satisfying points

## Summary

The inequality solver excludes a point that directly satisfies the strict inequality because it trusts a spurious boundary root from branch-invalid `atan` inversion.

## Reproducer

Run `reproduce_bug.py`; current output excludes `0` from the solution of `atan(x) < pi`.

## Expected behavior

The representative solution should be all real numbers.

## Evidence

`related_bugs.py` covers six omitted-point cases and checks each with an independent `math.atan` evaluation.

## Suggested regression test

Use `pr/tests/test_bug_042_solve_univariate_inequality_atan_x_pi_omits_x_0.py`.
