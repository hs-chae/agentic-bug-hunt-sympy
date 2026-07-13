import pytest

from sympy import Piecewise, limit, symbols


@pytest.mark.parametrize(
    "left_value, default_value",
    [(0, 1), (2, 5), (-3, 7), (4, -2), (11, 13), (-8, -1)],
)
def test_piecewise_left_hand_limit_uses_left_branch(left_value, default_value):
    x = symbols("x", real=True)
    p = Piecewise((left_value, x < 0), (default_value, True))
    assert limit(p, x, 0, dir="-") == left_value
