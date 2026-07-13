import pytest

from sympy import Eq, S, acot, pi, simplify, solveset
from sympy.abc import x


@pytest.mark.parametrize("shift", [0, 1, -1, 2, -3, pi])
def test_acot_endpoint_is_not_inverted_to_false_solution(shift):
    sol = solveset(Eq(acot(x - shift), -pi/2), x, S.Reals)
    assert sol.contains(shift) is not S.true
    assert simplify(acot(shift - shift) + pi/2) != 0

