import pytest

from sympy import Eq, Rational, S, simplify, sqrt, solveset, symbols


@pytest.mark.parametrize(
    "bad_value",
    [
        S.NegativeOne,
        S(-2),
        S(-3),
        Rational(-1, 2),
        S(-5),
        Rational(-7, 3),
    ],
)
def test_solveset_sqrt_x_sqrt_reciprocal_excludes_negative_real_axis(bad_value):
    x = symbols("x")
    lhs = sqrt(x) * sqrt(1/x)

    sol = solveset(Eq(lhs, 1), x, domain=S.Complexes)

    assert sol.contains(bad_value) is S.false
    assert simplify((lhs - 1).subs(x, bad_value)) != 0
