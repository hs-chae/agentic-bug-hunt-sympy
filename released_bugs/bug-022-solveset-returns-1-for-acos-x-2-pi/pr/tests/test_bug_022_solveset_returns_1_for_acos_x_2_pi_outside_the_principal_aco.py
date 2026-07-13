import cmath
import pytest
from sympy import Eq, S, acos, acosh, asinh, atan, pi, I, solveset, symbols, simplify

x = symbols("x")
CASES = [("2*pi", 2*pi, 1, complex(2*cmath.pi, 0)), ("-pi", -pi, -1, complex(-cmath.pi, 0)), ("3*pi", 3*pi, -1, complex(3*cmath.pi, 0)), ("4*pi", 4*pi, 1, complex(4*cmath.pi, 0)), ("-2*pi", -2*pi, 1, complex(-2*cmath.pi, 0)), ("5*pi", 5*pi, -1, complex(5*cmath.pi, 0))]

@pytest.mark.parametrize("label,target,bad,_target_complex", CASES)
def test_bug_022_solveset_returns_1_for_acos_x_2_pi_outside_the_principal_aco(label, target, bad, _target_complex):
    func = acos
    sol = solveset(Eq(func(x), target), x, domain=S.Complexes)
    assert sol.contains(bad) is not S.true
    assert simplify(func(bad) - target) != 0
