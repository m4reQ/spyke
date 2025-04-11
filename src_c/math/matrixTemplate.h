// Do not add include guard to this file
#include "matrix.h"
#include "vector.h"

#ifndef MAT_LEN
#error "Matrix template: MAT_LEN not defined"
#endif

#define GLM_TYPE_NAME MACRO_CONCAT(mat, MAT_LEN)
#define PY_TYPE_NAME MACRO_CONCAT(PyMatrix, MAT_LEN)
#define PY_TYPE_OBJECT_NAME MACRO_CONCAT(PY_TYPE_NAME, _Type)
#define GLM_CALL_FUNC(func, ...) MACRO_CONCAT(MACRO_CONCAT(glm_, GLM_TYPE_NAME), MACRO_CONCAT(_, func))(##__VA_ARGS__)
#define GLM_ZERO MACRO_CONCAT(MACRO_CONCAT(GLM_MAT, MAT_LEN), ZERO)
#define GLM_ONE MACRO_CONCAT(MACRO_CONCAT(GLM_MAT, MAT_LEN), ONE)
#define GLM_IDENTITY MACRO_CONCAT(MACRO_CONCAT(GLM_MAT, MAT_LEN), IDENTITY)

static size_t GetIndex(PyObject *index)
{
    size_t idx = 0;
    if (PyLong_Check(index))
    {
        idx = PyLong_AsSize_t(index);
    }
    else if (PyTuple_Check(index))
    {
        if (PyTuple_GET_SIZE(index) != 2)
            goto invalid_index_type;

        PyObject *n = PyTuple_GET_ITEM(index, 0);
        if (!PyLong_Check(n))
            goto invalid_index_type;

        PyObject *m = PyTuple_GET_ITEM(index, 0);
        if (!PyLong_Check(m))
            goto invalid_index_type;

        idx = PyLong_AsSize_t(m) * MAT_LEN + PyLong_AsSize_t(n);
    }
    else
    {
        goto invalid_index_type;
    }

    if (idx >= MAT_LEN * MAT_LEN)
    {
        PyErr_Format(PyExc_IndexError, "Invalid index for Matrix" MACRO_STRINGIFY(MAT_LEN) ": %d", idx);
        return (size_t)-1;
    }

    return idx;

invalid_index_type:
    PyErr_Format(PyExc_RuntimeError, "Matrix index must either be int or tuple[int, int], not %s.", Py_TYPE(index)->tp_name);
    return (size_t)-1;
}

#pragma region as_buffer
static int PyMatrix_bf_getbuffer(PY_TYPE_NAME *self, Py_buffer *view, int flags)
{
    view->obj = Py_NewRef(self);
    view->buf = &self->data[0];
    view->itemsize = sizeof(float);
    view->len = sizeof(GLM_TYPE_NAME);
    view->readonly = !FLAG_IS_SET(flags, PyBUF_WRITABLE);
    view->format = FLAG_IS_SET(flags, PyBUF_FORMAT) ? "f" : NULL;

    if (FLAG_IS_SET(flags, PyBUF_ANY_CONTIGUOUS))
    {
        view->ndim = 1;
        view->strides = FLAG_IS_SET(flags, PyBUF_STRIDES) ? (Py_ssize_t[]){sizeof(float)} : NULL;
        view->shape = FLAG_IS_SET(flags, PyBUF_ND) ? (Py_ssize_t[]){MAT_LEN * MAT_LEN} : NULL;
    }
    else
    {
        view->ndim = 2;
        view->strides = FLAG_IS_SET(flags, PyBUF_STRIDES) ? (Py_ssize_t[]){sizeof(float), MAT_LEN * sizeof(float)} : NULL;
        view->shape = FLAG_IS_SET(flags, PyBUF_ND) ? (Py_ssize_t[]){MAT_LEN, MAT_LEN} : NULL;
    }

    return 0;
}
#pragma endregion

#pragma region as_mapping
static Py_ssize_t PyMatrix_mp_length(PY_TYPE_NAME *self)
{
    (void)self;
    return MAT_LEN * MAT_LEN;
}

static PyObject *PyMatrix_mp_subscript(PY_TYPE_NAME *self, PyObject *index)
{
    float value;

    const Py_ssize_t idx = PyLong_AsSsize_t(index);
    if (!PyErr_Occurred())
    {
        if (idx >= MAT_LEN * MAT_LEN)
        {
            PyErr_Format(PyExc_IndexError, "Index outside of bounds for matrix %dx%d: %zu.", MAT_LEN, MAT_LEN, idx);
            return NULL;
        }

        value = ((float *)self->data)[idx];
        goto success;
    }

    PyErr_Clear();

    Py_ssize_t m, n;
    if (PyArg_ParseTuple(index, "nn", &m, &n))
    {
        if (m >= MAT_LEN || n >= MAT_LEN)
        {
            PyErr_Format(PyExc_IndexError, "Index outside of bounds for matrix %dx%d: %zux%zu.", MAT_LEN, MAT_LEN, m, n);
            return NULL;
        }

        value = self->data[m][n];
        goto success;
    }

    PyErr_Format(PyExc_IndexError, "Invalid index for Matrix" MACRO_STRINGIFY(MAT_LEN) ": %d", idx);
    return NULL;

success:
    return PyFloat_FromDouble((double)value);
}

static int PyMatrix_ass_subscript(PY_TYPE_NAME *self, PyObject *index, PyObject *value)
{
    PyObject *valueFloat = PyNumber_Float(value);
    if (valueFloat == NULL)
    {
        PyErr_Format(PyExc_TypeError, "Matrix value must be convertible to float, not: %s.", Py_TYPE(value)->tp_name);
        return -1;
    }

    float _value = (float)PyFloat_AS_DOUBLE(valueFloat);
    Py_DecRef(valueFloat);

    const Py_ssize_t idx = PyLong_AsSsize_t(index);
    if (!PyErr_Occurred())
    {
        if (idx >= MAT_LEN * MAT_LEN)
        {
            PyErr_Format(PyExc_IndexError, "Index outside of bounds for matrix %dx%d: %zu.", MAT_LEN, MAT_LEN, idx);
            return -1;
        }

        ((float *)self->data)[idx] = _value;
        goto success;
    }

    PyErr_Clear();

    Py_ssize_t m, n;
    if (PyArg_ParseTuple(index, "nn", &m, &n))
    {
        if (m >= MAT_LEN || n >= MAT_LEN)
        {
            PyErr_Format(PyExc_IndexError, "Index outside of bounds for matrix %dx%d: %zux%zu.", MAT_LEN, MAT_LEN, m, n);
            return -1;
        }

        self->data[m][n] = _value;
        goto success;
    }

    PyErr_Format(PyExc_IndexError, "Invalid index for Matrix" MACRO_STRINGIFY(MAT_LEN) ": %d", idx);
    return -1;

success:
    return 0;
}
#pragma endregion

#pragma region as_number
static PY_TYPE_NAME *PyMatrix_nb_add(PY_TYPE_NAME *self, PY_TYPE_NAME *other)
{
    if (!PyObject_IsInstance((PyObject *)self, (PyObject *)&PY_TYPE_OBJECT_NAME))
    {
        PyErr_Format(PyExc_RuntimeError, "Cannot add %s and %s.", Py_TYPE(self)->tp_name, Py_TYPE(other)->tp_name);
        return NULL;
    }

    float *data = &self->data[0][0];
    float *otherData = &other->data[0][0];

    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, &PY_TYPE_OBJECT_NAME);
    for (size_t i = 0; i < MAT_LEN * MAT_LEN; i++)
        ((float *)new->data)[i] = data[i] + otherData[i];

    return new;
}

static PY_TYPE_NAME *PyMatrix_nb_inplace_add(PY_TYPE_NAME *self, PY_TYPE_NAME *other)
{
    if (!PyObject_IsInstance((PyObject *)self, (PyObject *)&PY_TYPE_OBJECT_NAME))
    {
        PyErr_Format(PyExc_RuntimeError, "Cannot add %s and %s.", Py_TYPE(self)->tp_name, Py_TYPE(other)->tp_name);
        return NULL;
    }

    float *data = &self->data[0][0];
    float *otherData = &other->data[0][0];

    for (size_t i = 0; i < MAT_LEN * MAT_LEN; i++)
        data[i] += otherData[i];

    return (PY_TYPE_NAME *)Py_NewRef(self);
}

static PY_TYPE_NAME *PyMatrix_nb_subtract(PY_TYPE_NAME *self, PY_TYPE_NAME *other)
{
    if (!PyObject_IsInstance((PyObject *)self, (PyObject *)&PY_TYPE_OBJECT_NAME))
    {
        PyErr_Format(PyExc_RuntimeError, "Cannot add %s and %s.", Py_TYPE(self)->tp_name, Py_TYPE(other)->tp_name);
        return NULL;
    }

    float *data = &self->data[0][0];
    float *otherData = &other->data[0][0];

    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, &PY_TYPE_OBJECT_NAME);
    for (size_t i = 0; i < MAT_LEN * MAT_LEN; i++)
        ((float *)new->data)[i] = data[i] - otherData[i];

    return new;
}

static PY_TYPE_NAME *PyMatrix_nb_inplace_subtract(PY_TYPE_NAME *self, PY_TYPE_NAME *other)
{
    if (!PyObject_IsInstance((PyObject *)self, (PyObject *)&PY_TYPE_OBJECT_NAME))
    {
        PyErr_Format(PyExc_RuntimeError, "Cannot add %s and %s.", Py_TYPE(self)->tp_name, Py_TYPE(other)->tp_name);
        return NULL;
    }

    float *data = &self->data[0][0];
    float *otherData = &other->data[0][0];
    for (size_t i = 0; i < MAT_LEN * MAT_LEN; i++)
        data[i] -= otherData[i];

    return (PY_TYPE_NAME *)Py_NewRef(self);
}

static PY_TYPE_NAME *PyMatrix_nb_multiply(PY_TYPE_NAME *self, PY_TYPE_NAME *other)
{
    if (!PyObject_IsInstance((PyObject *)self, (PyObject *)&PY_TYPE_OBJECT_NAME))
    {
        PyErr_Format(PyExc_RuntimeError, "Cannot add %s and %s.", Py_TYPE(self)->tp_name, Py_TYPE(other)->tp_name);
        return NULL;
    }

    float *data = &self->data[0][0];
    float *otherData = &other->data[0][0];

    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, &PY_TYPE_OBJECT_NAME);
    for (size_t i = 0; i < MAT_LEN * MAT_LEN; i++)
        ((float *)new->data)[i] = data[i] * otherData[i];

    return new;
}

static PY_TYPE_NAME *PyMatrix_nb_inplace_multiply(PY_TYPE_NAME *self, PY_TYPE_NAME *other)
{
    if (!PyObject_IsInstance((PyObject *)self, (PyObject *)&PY_TYPE_OBJECT_NAME))
    {
        PyErr_Format(PyExc_RuntimeError, "Cannot add %s and %s.", Py_TYPE(self)->tp_name, Py_TYPE(other)->tp_name);
        return NULL;
    }

    float *data = &self->data[0][0];
    float *otherData = &other->data[0][0];
    for (size_t i = 0; i < MAT_LEN * MAT_LEN; i++)
        data[i] *= otherData[i];

    return (PY_TYPE_NAME *)Py_NewRef(self);
}

static PY_TYPE_NAME *PyMatrix_nb_matrix_multiply(PY_TYPE_NAME *self, PY_TYPE_NAME *other)
{
    if (!PyObject_IsInstance((PyObject *)self, (PyObject *)&PY_TYPE_OBJECT_NAME))
    {
        PyErr_Format(PyExc_RuntimeError, "Cannot add %s and %s.", Py_TYPE(self)->tp_name, Py_TYPE(other)->tp_name);
        return NULL;
    }

    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, &PY_TYPE_OBJECT_NAME);
    GLM_CALL_FUNC(mul, self->data, other->data, new->data);

    return new;
}

static PY_TYPE_NAME *PyMatrix_nb_inplace_matrix_multiply(PY_TYPE_NAME *self, PY_TYPE_NAME *other)
{
    if (!PyObject_IsInstance((PyObject *)self, (PyObject *)&PY_TYPE_OBJECT_NAME))
    {
        PyErr_Format(PyExc_RuntimeError, "Cannot add %s and %s.", Py_TYPE(self)->tp_name, Py_TYPE(other)->tp_name);
        return NULL;
    }

    GLM_CALL_FUNC(mul, self->data, other->data, self->data);
    return (PY_TYPE_NAME *)Py_NewRef(self);
}
#pragma endregion

static PyObject *PyMatrix_transpose(PY_TYPE_NAME *self, PyObject *args)
{
    (void)args;
    GLM_CALL_FUNC(transpose, self->data);
    Py_RETURN_NONE;
}

static PY_TYPE_NAME *PyMatrix_transposed(PY_TYPE_NAME *self, PyObject *args)
{
    (void)args;

    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, &PY_TYPE_OBJECT_NAME);
    GLM_CALL_FUNC(transpose_to, self->data, new->data);

    return new;
}

static PyObject *PyMatrix_inverse(PY_TYPE_NAME *self, PyObject *args)
{
    (void)args;
    GLM_CALL_FUNC(inv, self->data, self->data);
    Py_RETURN_NONE;
}

static PY_TYPE_NAME *PyMatrix_inversed(PY_TYPE_NAME *self, PyObject *args)
{
    (void)args;

    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, &PY_TYPE_OBJECT_NAME);
    GLM_CALL_FUNC(inv, self->data, new->data);

    return new;
}

#if MAT_LEN == 4
static PyObject *PyMatrix_inverse_fast(PY_TYPE_NAME *self, PyObject *args)
{
    (void)args;
    GLM_CALL_FUNC(inv_fast, self->data, self->data);
    Py_RETURN_NONE;
}

static PY_TYPE_NAME *PyMatrix_inversed_fast(PY_TYPE_NAME *self, PyObject *args)
{
    (void)args;

    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, &PY_TYPE_OBJECT_NAME);
    GLM_CALL_FUNC(inv_fast, self->data, new->data);

    return new;
}

static PyObject *PyMatrix_translate(PY_TYPE_NAME *self, PyVector3 *translation)
{
    if (!PyObject_IsInstance((PyObject *)translation, (PyObject *)&PyVector3_Type))
    {
        PyErr_Format(PyExc_TypeError, "Expected argument to be of type %s, got: %s.", PyVector3_Type.tp_name, Py_TYPE(translation)->tp_name);
        return NULL;
    }

    glm_translate(self->data, translation->data);

    Py_RETURN_NONE;
}

static PyObject *PyMatrix_scale(PY_TYPE_NAME *self, PyVector3 *scale)
{
    if (!PyObject_IsInstance((PyObject *)scale, (PyObject *)&PyVector3_Type))
    {
        PyErr_Format(PyExc_TypeError, "Expected argument to be of type %s, got: %s.", PyVector3_Type.tp_name, Py_TYPE(scale)->tp_name);
        return NULL;
    }

    glm_scale(self->data, scale->data);

    Py_RETURN_NONE;
}

static PyObject *PyMatrix_rotate(PY_TYPE_NAME *self, PyObject *const *args, Py_ssize_t nArgs)
{
    PyVector3 *rotation;
    float angle;

    if (nArgs == 2)
    {
        if (!_PyArg_ParseStack(args, nArgs, "fO!", &angle, &PyVector3_Type, &rotation))
            return NULL;

        glm_rotate(self->data, angle, rotation->data);
    }
    else if (nArgs == 1)
    {
        rotation = args[0];
        if (!PyObject_IsInstance((PyObject *)rotation, (PyObject *)&PyVector3_Type))
        {
            PyErr_Format(PyExc_TypeError, "Expected argument to be of type %s, got: %s.", PyVector3_Type.tp_name, Py_TYPE(rotation)->tp_name);
            return NULL;
        }

        glm_rotate_x(self->data, rotation->data[0], self->data);
        glm_rotate_y(self->data, rotation->data[1], self->data);
        glm_rotate_z(self->data, rotation->data[2], self->data);
    }

    Py_RETURN_NONE;
}

static PyObject *PyMatrix_perspective_resize(PY_TYPE_NAME *self, PyObject *fov)
{
    PyObject *fovFloat = PyNumber_Float(fov);
    if (fovFloat == NULL)
        return NULL;

    glm_perspective_resize((float)PyFloat_AS_DOUBLE(fovFloat), self->data);

    Py_RETURN_NONE;
}

static PY_TYPE_NAME *PyMatrix_transform(PyTypeObject *cls, PyObject *const *args, Py_ssize_t nArgs)
{
    PyVector3 *translation, *rotation, *scale;
    if (!_PyArg_ParseStack(args, nArgs, "O!O!O!", &PyVector3_Type, &translation, &PyVector3_Type, &scale, &PyVector3_Type, &rotation))
        return NULL;

    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, cls);
    new = (PY_TYPE_NAME *)PyObject_Init((PyObject *)new, cls);

    glm_mat4_identity(new->data);
    glm_translate(new->data, translation->data);
    glm_rotate_x(new->data, rotation->data[0], new->data);
    glm_rotate_y(new->data, rotation->data[1], new->data);
    glm_rotate_z(new->data, rotation->data[2], new->data);
    glm_scale(new->data, scale->data);

    return new;
}

static PY_TYPE_NAME *PyMatrix_ortho(PyTypeObject *cls, PyObject *const *args, Py_ssize_t nArgs)
{
    float l, r, b, t, n, f;
    if (!_PyArg_ParseStack(args, nArgs, "ffffff", &l, &r, &b, &t, &n, &f))
        return NULL;

    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, cls);
    new = (PY_TYPE_NAME *)PyObject_Init((PyObject *)new, cls);

    glm_ortho(l, r, b, t, n, f, new->data);

    return new;
}

static PY_TYPE_NAME *PyMatrix_perspective(PyTypeObject *cls, PyObject *const *args, Py_ssize_t nArgs)
{
    float fov, aspect, near, far;
    if (!_PyArg_ParseStack(args, nArgs, "ffff", &fov, &aspect, &near, &far))
        return NULL;

    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, cls);
    new = (PY_TYPE_NAME *)PyObject_Init((PyObject *)new, cls);

    glm_perspective(fov, aspect, near, far, new->data);

    return new;
}

static PY_TYPE_NAME *PyMatrix_look_at(PyTypeObject *cls, PyObject *const *args, Py_ssize_t nArgs)
{
    PyVector3 *eye, *center, *up;
    if (!_PyArg_ParseStack(args, nArgs, "O!O!O!", &PyVector3_Type, &eye, &PyVector3_Type, &center, &PyVector3_Type, &up))
        return NULL;

    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, cls);
    new = (PY_TYPE_NAME *)PyObject_Init((PyObject *)new, cls);

    glm_lookat(eye->data, center->data, up->data, new->data);

    return new;
}
#endif

static PyObject *PyMatrix_determinant(PY_TYPE_NAME *self, PyObject *args)
{
    (void)args;
    return PyFloat_FromDouble((double)GLM_CALL_FUNC(det, self->data));
}

static PY_TYPE_NAME *PyMatrix_identity(PyTypeObject *cls, PyObject *args, PyObject *kwargs)
{
    (void)args;
    (void)kwargs;

    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, cls);
    new = (PY_TYPE_NAME *)PyObject_Init((PyObject *)new, cls);
    GLM_CALL_FUNC(identity, new->data);

    return new;
}

static PY_TYPE_NAME *PyMatrix_zero(PyTypeObject *cls, PyObject *args, PyObject *kwargs)
{
    (void)args;
    (void)kwargs;

    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, cls);
    new = (PY_TYPE_NAME *)PyObject_Init((PyObject *)new, cls);

    GLM_CALL_FUNC(zero, new->data);

    return new;
}

PyTypeObject PY_TYPE_OBJECT_NAME = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_basicsize = sizeof(PY_TYPE_NAME),
    .tp_name = MACRO_CONCAT("spyke.math.Matrix", MACRO_STRINGIFY(MAT_LEN)),
    .tp_new = PyType_GenericNew,
    .tp_as_buffer = &(PyBufferProcs){
        .bf_getbuffer = (getbufferproc)PyMatrix_bf_getbuffer,
    },
    .tp_as_mapping = &(PyMappingMethods){
        .mp_length = (lenfunc)PyMatrix_mp_length,
        .mp_subscript = (binaryfunc)PyMatrix_mp_subscript,
        .mp_ass_subscript = (objobjargproc)PyMatrix_ass_subscript,
    },
    .tp_as_number = &(PyNumberMethods){
        .nb_add = (binaryfunc)PyMatrix_nb_add,
        .nb_inplace_add = (binaryfunc)PyMatrix_nb_inplace_add,
        .nb_subtract = (binaryfunc)PyMatrix_nb_subtract,
        .nb_inplace_subtract = (binaryfunc)PyMatrix_nb_inplace_subtract,
        .nb_multiply = (binaryfunc)PyMatrix_nb_multiply,
        .nb_inplace_multiply = (binaryfunc)PyMatrix_nb_inplace_multiply,
        .nb_matrix_multiply = (binaryfunc)PyMatrix_nb_matrix_multiply,
        .nb_inplace_matrix_multiply = (binaryfunc)PyMatrix_nb_inplace_matrix_multiply,
    },
    .tp_methods = (PyMethodDef[]){
        {"identity", (PyCFunction)PyMatrix_identity, METH_NOARGS | METH_CLASS, NULL},
        {"zero", (PyCFunction)PyMatrix_zero, METH_NOARGS | METH_CLASS, NULL},
        {"transpose", (PyCFunction)PyMatrix_transpose, METH_NOARGS, NULL},
        {"transposed", (PyCFunction)PyMatrix_transposed, METH_NOARGS, NULL},
        {"inverse", (PyCFunction)PyMatrix_inverse, METH_NOARGS, NULL},
        {"inversed", (PyCFunction)PyMatrix_inversed, METH_NOARGS, NULL},
#if MAT_LEN == 4
        {"inverse_fast", (PyCFunction)PyMatrix_inverse_fast, METH_NOARGS, NULL},
        {"inversed_fast", (PyCFunction)PyMatrix_inversed_fast, METH_NOARGS, NULL},
        {"translate", (PyCFunction)PyMatrix_translate, METH_O, NULL},
        {"rotate", (PyCFunction)PyMatrix_rotate, METH_FASTCALL, NULL},
        {"scale", (PyCFunction)PyMatrix_scale, METH_O, NULL},
        {"perspective_resize", (PyCFunction)PyMatrix_perspective_resize, METH_O, NULL},
        {"transform", (PyCFunction)PyMatrix_transform, METH_FASTCALL | METH_CLASS, NULL},
        {"ortho", (PyCFunction)PyMatrix_ortho, METH_FASTCALL | METH_CLASS, NULL},
        {"perspective", (PyCFunction)PyMatrix_perspective, METH_FASTCALL | METH_CLASS, NULL},
        {"look_at", (PyCFunction)PyMatrix_look_at, METH_FASTCALL | METH_CLASS, NULL},
#endif
        {"determinant", (PyCFunction)PyMatrix_determinant, METH_NOARGS, NULL},
        {0},
    },
};
