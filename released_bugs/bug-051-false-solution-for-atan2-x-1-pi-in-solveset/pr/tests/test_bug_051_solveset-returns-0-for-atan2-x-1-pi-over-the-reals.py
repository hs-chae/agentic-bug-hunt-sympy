import pytest
from sympy import Eq, Rational, S, atan2, pi, solveset, symbols


x = symbols("x")


@pytest.mark.parametrize(
    "scale,denom,sign",
    [
        (S.One, S.One, S.One),
        (S.One, S(2), S.One),
        (S(2), S.One, S.One),
        (Rational(1, 3), S.One, S.One),
        (-S.One, S.One, S.One),
        (S.One, S.One, -S.One),
    ],
)
def test_solveset_atan2_rejects_values_outside_principal_range(scale, denom, sign):
    assert solveset(Eq(atan2(scale*x, denom), sign*pi), x, S.Reals) == S.EmptySet
