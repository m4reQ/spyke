import struct

import pytest

from spyke.math import Matrix3, Matrix4, Vector3, Vector4


def test_matrix4_identity():
    m = Matrix4.identity()
    assert all(m[i, i] == 1 for i in range(4))
    assert all(m[i, j] == 0 for i in range(4) for j in range(4) if i != j)

def test_matrix4_zero():
    m = Matrix4.zero()
    assert all(m[i, j] == 0 for i in range(4) for j in range(4))

def test_matrix4_transpose():
    m = Matrix4.zero()
    m[0, 1] = 1
    m[1, 0] = 2
    m.transpose()
    assert m[0, 1] == 2 and m[1, 0] == 1

def test_matrix4_transposed():
    m = Matrix4.zero()
    m[0, 1] = 1
    m[1, 0] = 2
    t = m.transposed()
    assert t[0, 1] == 2 and t[1, 0] == 1

def test_matrix4_inverse():
    m = Matrix4.identity()
    m.inverse()
    assert all(m[i, i] == 1 for i in range(4))

def test_matrix4_inversed():
    m = Matrix4.identity()
    inv = m.inversed()
    assert all(inv[i, i] == 1 for i in range(4))

def test_matrix4_inverse_fast():
    m = Matrix4.identity()
    m.inverse_fast()

    assert all(m[i, i] == pytest.approx(1.0, abs=0.001) for i in range(4))

def test_matrix4_inversed_fast():
    m = Matrix4.identity()
    inv = m.inversed_fast()
    assert all(inv[i, i] == pytest.approx(1.0, abs=0.001) for i in range(4))

def test_matrix4_determinant():
    m = Matrix4.identity()
    assert m.determinant() == pytest.approx(1.0)

def test_matrix4_translate():
    m = Matrix4.identity()
    m.translate(Vector3(1.0, 2.0, 3.0))

def test_matrix4_scale():
    m = Matrix4.identity()
    m.scale(Vector3(2.0, 2.0, 2.0))

def test_matrix4_perspective_resize():
    m = Matrix4.identity()
    m.perspective_resize(16 / 9)

def test_matrix4_transform_static():
    m = Matrix4.transform(Vector3(1, 2, 3), Vector3(1, 1, 1), Vector3(0, 0, 0))
    assert isinstance(m, Matrix4)

def test_matrix4_ortho_static():
    m = Matrix4.ortho(-1, 1, -1, 1, 0.1, 100)
    assert isinstance(m, Matrix4)

def test_matrix4_perspective_static():
    m = Matrix4.perspective(60, 16 / 9, 0.1, 100)
    assert isinstance(m, Matrix4)

def test_matrix4_look_at_static():
    m = Matrix4.look_at(Vector3(0, 0, 5), Vector3(0, 0, 0), Vector3(0, 1, 0))
    assert isinstance(m, Matrix4)

def test_matrix4_rotate_vector():
    m = Matrix4.identity()
    m.rotate(Vector3(0, 1, 0))

def test_matrix4_rotate_axis_angle():
    m = Matrix4.identity()
    m.rotate(90, Vector3(0, 1, 0))

def test_matrix4_constructor_buffer():
    data = struct.pack('16f', *(float(i) for i in range(16)))
    m = Matrix4(data)

    assert all(m[i] == pytest.approx(float(i)) for i in range(16))

def test_matrix4_constructor_list():
    data = [float(i) for i in range(16)]
    m = Matrix4(data)

    assert all(m[i] == pytest.approx(float(i)) for i in range(16))

def test_matrix4_constructor_tuple():
    data = tuple(float(i) for i in range(16))
    m = Matrix4(data)

    assert all(m[i] == pytest.approx(float(i)) for i in range(16))

def test_matrix4_constructor_topleft():
    topleft = Matrix3.identity()
    m = Matrix4(topleft)

    assert m[0, 0] == 1.0 and m[1, 1] == 1.0 and m[2, 2] == 1.0

def test_matrix4_constructor_vectors():
    m = Matrix4(
        Vector4(1.0, 0.0, 0.0, 0.0),
        Vector4(0.0, 2.0, 0.0, 0.0),
        Vector4(0.0, 0.0, 3.0, 0.0),
        Vector4(0.0, 0.0, 0.0, 4.0))

    assert m[0, 0] == 1.0 and m[1, 1] == 2.0 and m[2, 2] == 3.0 and m[3, 3] == 4.0
