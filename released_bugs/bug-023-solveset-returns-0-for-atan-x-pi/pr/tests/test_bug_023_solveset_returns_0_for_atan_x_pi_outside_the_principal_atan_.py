import cmath
import pytest
from sympy import Eq, S, acos, acosh, asinh, atan, pi, I, solveset, symbols, simplify

x = symbols("x")
CASES = [("pi", pi, 0, complex(cmath.pi, 0)), ("-pi", -pi, 0, complex(-cmath.pi, 0)), ("2*pi", 2*pi, 0, complex(2*cmath.pi, 0)), ("-2*pi", -2*pi, 0, complex(-2*cmath.pi, 0)), ("3*pi", 3*pi, 0, complex(3*cmath.pi, 0)), ("-3*pi", -3*pi, 0, complex(-3*cmath.pi, 0))]

@pytest.mark.parametrize("label,target,bad,_target_complex", CASES)
def test_bug_023_solveset_returns_0_for_atan_x_pi_outside_the_principal_atan_(label, target, bad, _target_complex):
    func = atan
    sol = solveset(Eq(func(x), target), x, domain=S.Complexes)
    assert sol.contains(bad) is not S.true
    assert simplify(func(bad) - target) != 0
