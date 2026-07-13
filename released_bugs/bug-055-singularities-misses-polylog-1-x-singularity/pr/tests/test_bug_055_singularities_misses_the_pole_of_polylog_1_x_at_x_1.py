import pytest
from sympy import S, polylog, symbols
from sympy.calculus.singularities import singularities

x = symbols("x")


@pytest.mark.parametrize(
    ("arg", "point"),
    [
        (x, S.One),
        (x + 1, S.Zero),
        (x - 2, S(3)),
        (2*x, S.Half),
        (-x, -S.One),
        (x/3, S(3)),
    ],
)
def test_singularities_polylog_one_includes_log_singularity(arg, point):
    found = singularities(polylog(1, arg), x, S.Complexes)
    assert found.contains(point) == S.true
