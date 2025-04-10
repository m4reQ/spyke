import pytest

from spyke.math import Vector2


def test_vector2_dot():
    a = Vector2(1, 2)
    b = Vector2(3, 4)
    assert a.dot(b) == pytest.approx(11.0)

def test_vector2_cross():
    a = Vector2(1, 2)
    b = Vector2(3, 4)
    assert a.cross(b) == pytest.approx(-2.0)

def test_vector2_length():
    v = Vector2(3, 4)
    assert v.length() == pytest.approx(5.0)

def test_vector2_distance():
    a = Vector2(1, 2)
    b = Vector2(4, 6)
    assert a.distance(b) == pytest.approx(5.0)

def test_vector2_normalize():
    v = Vector2(3, 4)
    norm = v.normalized()
    assert norm.length() == pytest.approx(1.0)

def test_vector2_interpolate():
    a = Vector2(0, 0)
    b = Vector2(10, 10)
    c = a.interpolate(b, 0.5)
    assert c.x == pytest.approx(5.0)
    assert c.y == pytest.approx(5.0)

def test_vector2_add():
    assert Vector2(1, 2) + Vector2(3, 4) == Vector2(4, 6)

def test_vector2_sub():
    assert Vector2(1, 2) - Vector2(3, 4) == Vector2(-2, -2)

def test_vector2_mul():
    assert Vector2(1, 2) * 2 == Vector2(2, 4)

def test_vector2_div():
    assert Vector2(3, 4) / 2 == Vector2(1.5, 2.0)

def test_vector2_neg():
    assert -Vector2(1, 2) == Vector2(-1, -2)

def test_vector2_iadd():
    v = Vector2(1, 2)
    v += Vector2(3, 4)
    assert v == Vector2(4, 6)

def test_vector2_isub():
    v = Vector2(5, 5)
    v -= Vector2(2, 3)
    assert v == Vector2(3, 2)

def test_vector2_imul():
    v = Vector2(1, 2)
    v *= 3
    assert v == Vector2(3, 6)

def test_vector2_idiv():
    v = Vector2(4, 6)
    v /= 2
    assert v == Vector2(2, 3)

def test_vector2_mod_scalar():
    assert Vector2(5, 7) % 2 == Vector2(1, 1)

def test_vector2_mod_vector():
    assert Vector2(5, 7) % Vector2(2, 3) == Vector2(1, 1)

def test_vector2_imod_scalar():
    v = Vector2(5, 7)
    v %= 2
    assert v == Vector2(1, 1)

def test_vector2_imod_vector():
    v = Vector2(5, 7)
    v %= Vector2(2, 3)
    assert v == Vector2(1, 1)

def test_vector2_add_scalar():
    assert Vector2(1, 2) + 3 == Vector2(4, 5)

def test_vector2_sub_scalar():
    assert Vector2(5, 6) - 2 == Vector2(3, 4)

def test_vector2_mul_scalar():
    assert Vector2(2, 3) * 2 == Vector2(4, 6)

def test_vector2_div_scalar():
    assert Vector2(6, 8) / 2 == Vector2(3, 4)

def test_vector2_iadd_scalar():
    v = Vector2(1, 2)
    v += 3
    assert v == Vector2(4, 5)

def test_vector2_isub_scalar():
    v = Vector2(5, 6)
    v -= 2
    assert v == Vector2(3, 4)

def test_vector2_imul_scalar():
    v = Vector2(2, 3)
    v *= 2
    assert v == Vector2(4, 6)

def test_vector2_idiv_scalar():
    v = Vector2(6, 8)
    v /= 2
    assert v == Vector2(3, 4)

def test_vector2_div_by_zero():
    with pytest.raises(ZeroDivisionError):
        _ = Vector2(1, 2) / 0

def test_vector2_mod_by_zero():
    with pytest.raises(ZeroDivisionError):
        _ = Vector2(1, 2) % 0

def test_vector2_idiv_by_zero():
    v = Vector2(1, 2)
    with pytest.raises(ZeroDivisionError):
        v /= 0

def test_vector2_imod_by_zero():
    v = Vector2(1, 2)
    with pytest.raises(ZeroDivisionError):
        v %= 0

def test_vector2_single_value_constructor():
    v = Vector2(5.0)
    assert v == Vector2(5.0, 5.0)

def test_vector2_two_value_constructor():
    v = Vector2(1.0, 2.0)
    assert v.x == 1.0 and v.y == 2.0

def test_vector2_zero():
    assert Vector2.zero() == Vector2(0.0, 0.0)

def test_vector2_one():
    assert Vector2.one() == Vector2(1.0, 1.0)

def test_vector2_unit_x():
    assert Vector2.unit_x() == Vector2(1.0, 0.0)

def test_vector2_unit_y():
    assert Vector2.unit_y() == Vector2(0.0, 1.0)
