import pytest

from sympy import Eq, S, acsc, pi, simplify, solveset, symbols


@pytest.mark.parametrize(
    "target",
    [3*pi/2, 5*pi/2, -3*pi/2, 7*pi/2, 11*pi/2, -5*pi/2],
)
def test_solveset_acsc_filters_targets_outside_principal_range(target):
    x = symbols("x")
    sol = solveset(Eq(acsc(x), target), x, S.Complexes)

    assert all(simplify(acsc(candidate) - target) == 0 for candidate in sol)
