import pytest

from sympy import S, sec, solveset, symbols


@pytest.mark.parametrize(
    "scale, slope, offset",
    [
        (1, 1, 0),
        (1, 1, 1),
        (1, 1, -2),
        (1, 2, 0),
        (1, 3, 1),
        (2, 1, 0),
    ],
)
def test_solveset_sec_has_no_complex_zero(scale, slope, offset):
    x = symbols("x")
    assert solveset(scale * sec(slope * x + offset), x, domain=S.Complexes) == S.EmptySet
