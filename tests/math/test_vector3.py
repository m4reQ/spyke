import pytest

from spyke.math import Vector3


def test_vector3_dot():
    a = Vector3(1, 2, 3)
    b = Vector3(4, -5, 6)
    assert a.dot(b) == pytest.approx(12.0)

def test_vector3_cross():
    a = Vector3(1, 0, 0)
    b = Vector3(0, 1, 0)
    c = a.cross(b)
    assert (c.x, c.y, c.z) == pytest.approx((0, 0, 1))

def test_vector3_length():
    v = Vector3(1, 2, 2)
    assert v.length() == pytest.approx(3.0)

def test_vector3_distance():
    a = Vector3(1, 2, 3)
    b = Vector3(4, 6, 3)
    assert a.distance(b) == pytest.approx(5.0)

def test_vector3_normalize():
    v = Vector3(2, 0, 0)
    assert v.normalized().length() == pytest.approx(1.0)

def test_vector3_interpolate():
    a = Vector3(0, 0, 0)
    b = Vector3(2, 4, 6)
    c = a.interpolate(b, 0.5)
    assert (c.x, c.y, c.z) == pytest.approx((1, 2, 3))

def test_vector3_add():
    assert Vector3(1, 2, 3) + Vector3(4, 5, 6) == Vector3(5, 7, 9)

def test_vector3_sub():
    assert Vector3(1, 2, 3) - Vector3(4, 5, 6) == Vector3(-3, -3, -3)

def test_vector3_mul():
    assert Vector3(1, 2, 3) * 2 == Vector3(2, 4, 6)

def test_vector3_div():
    assert Vector3(4, 5, 6) / 2 == Vector3(2, 2.5, 3)

def test_vector3_neg():
    assert -Vector3(1, 2, 3) == Vector3(-1, -2, -3)

def test_vector3_iadd():
    v = Vector3(1, 2, 3)
    v += Vector3(4, 5, 6)
    assert v == Vector3(5, 7, 9)

def test_vector3_isub():
    v = Vector3(4, 5, 6)
    v -= Vector3(1, 2, 3)
    assert v == Vector3(3, 3, 3)

def test_vector3_imul():
    v = Vector3(1, 2, 3)
    v *= 2
    assert v == Vector3(2, 4, 6)

def test_vector3_idiv():
    v = Vector3(4, 6, 8)
    v /= 2
    assert v == Vector3(2, 3, 4)

def test_vector3_mod_scalar():
    assert Vector3(5, 7, 9) % 2 == Vector3(1, 1, 1)

def test_vector3_mod_vector():
    assert Vector3(5, 7, 9) % Vector3(2, 3, 4) == Vector3(1, 1, 1)

def test_vector3_imod_scalar():
    v = Vector3(5, 7, 9)
    v %= 2
    assert v == Vector3(1, 1, 1)

def test_vector3_imod_vector():
    v = Vector3(5, 7, 9)
    v %= Vector3(2, 3, 4)
    assert v == Vector3(1, 1, 1)

def test_vector3_add_scalar():
    assert Vector3(1, 2, 3) + 1 == Vector3(2, 3, 4)

def test_vector3_sub_scalar():
    assert Vector3(4, 5, 6) - 1 == Vector3(3, 4, 5)

def test_vector3_mul_scalar():
    assert Vector3(1, 2, 3) * 3 == Vector3(3, 6, 9)

def test_vector3_div_scalar():
    assert Vector3(6, 9, 12) / 3 == Vector3(2, 3, 4)

def test_vector3_iadd_scalar():
    v = Vector3(1, 2, 3)
    v += 1
    assert v == Vector3(2, 3, 4)

def test_vector3_isub_scalar():
    v = Vector3(4, 5, 6)
    v -= 1
    assert v == Vector3(3, 4, 5)

def test_vector3_imul_scalar():
    v = Vector3(1, 2, 3)
    v *= 3
    assert v == Vector3(3, 6, 9)

def test_vector3_idiv_scalar():
    v = Vector3(6, 9, 12)
    v /= 3
    assert v == Vector3(2, 3, 4)

def test_vector3_div_by_zero():
    with pytest.raises(ZeroDivisionError):
        _ = Vector3(1, 2, 3) / 0

def test_vector3_mod_by_zero():
    with pytest.raises(ZeroDivisionError):
        _ = Vector3(1, 2, 3) % 0

def test_vector3_idiv_by_zero():
    v = Vector3(1, 2, 3)
    with pytest.raises(ZeroDivisionError):
        v /= 0

def test_vector3_imod_by_zero():
    v = Vector3(1, 2, 3)
    with pytest.raises(ZeroDivisionError):
        v %= 0

def test_vector3_float_constructor():
    v = Vector3(5.0)
    assert v == Vector3(5.0, 5.0, 5.0)

def test_vector3_tuple_constructor():
    v = Vector3((1.0, 2.0, 3.0))
    assert v == Vector3(1.0, 2.0, 3.0)

def test_vector3_list_constructor():
    v = Vector3([1.0, 2.0, 3.0])
    assert v == Vector3(1.0, 2.0, 3.0)

def test_vector3_buffer_constructor():
    v = Vector3(b'\x00\x00\x80?\x00\x00\x00@\x00\x00@@')
    assert v == Vector3(1.0, 2.0, 3.0)

def test_vector3_multi_value_constructor():
    v = Vector3(1.0, 2.0, 3.0)
    assert v.x == 1.0 and v.y == 2.0 and v.z == 3.0

def test_vector3_zero():
    assert Vector3.zero() == Vector3(0.0, 0.0, 0.0)

def test_vector3_one():
    assert Vector3.one() == Vector3(1.0, 1.0, 1.0)

def test_vector3_unit_x():
    assert Vector3.unit_x() == Vector3(1.0, 0.0, 0.0)

def test_vector3_unit_y():
    assert Vector3.unit_y() == Vector3(0.0, 1.0, 0.0)

def test_vector3_unit_z():
    assert Vector3.unit_z() == Vector3(0.0, 0.0, 1.0)
