// Do not add include guard to this file
#include "vector.h"

#ifndef VEC_LEN
#error "Vector template: VEC_LEN not defined"
#endif

#define GLM_TYPE_NAME MACRO_CONCAT(vec, VEC_LEN)
#define PY_TYPE_NAME MACRO_CONCAT(PyVector, VEC_LEN)
#define PY_TYPE_OBJECT_NAME MACRO_CONCAT(PY_TYPE_NAME, _Type)
#define GLM_CALL_FUNC(func, ...) MACRO_CONCAT(MACRO_CONCAT(glm_, GLM_TYPE_NAME), MACRO_CONCAT(_, func))(##__VA_ARGS__)
#define GLM_ZERO MACRO_CONCAT(MACRO_CONCAT(GLM_VEC, VEC_LEN), ZERO)
#define GLM_ONE MACRO_CONCAT(MACRO_CONCAT(GLM_VEC, VEC_LEN), ONE)
#define VECTOR_INIT_FUNC MACRO_CONCAT(MACRO_CONCAT(PyVector, VEC_LEN), _init)
#define VECTOR_STR_FUNC MACRO_CONCAT(MACRO_CONCAT(PyVector, VEC_LEN), _str)
#define VECTOR_RICH_COMPARE_FUNC MACRO_CONCAT(MACRO_CONCAT(PyVector, VEC_LEN), _richcompare)
#define VECTOR_CHECK_ZERO MACRO_CONCAT(MACRO_CONCAT(PyVector, VEC_LEN), _check_zero)

static int VECTOR_INIT_FUNC(PY_TYPE_NAME *self, PyObject *args, PyObject *kwargs);
static PyObject *VECTOR_STR_FUNC(PY_TYPE_NAME *self);
static bool VECTOR_CHECK_ZERO(PY_TYPE_NAME *self);

static float GetVectorLengthSquared(PY_TYPE_NAME *self)
{
    float length = 0.0f;
    for (size_t i = 0; i < VEC_LEN; i++)
        length += self->data[i] * self->data[i];

    return length;
}

static bool CheckTypeSelf(PyObject *other)
{
    if (!PyObject_IsInstance((PyObject *)other, (PyObject *)&PY_TYPE_OBJECT_NAME))
    {
        PyErr_Format(PyExc_TypeError, "Expected value to be of type %s, got: %s.", PY_TYPE_OBJECT_NAME.tp_name, Py_TYPE(other)->tp_name);
        return false;
    }

    return true;
}

#pragma region tp_as_buffer
static int PyVector_bf_getbuffer(PY_TYPE_NAME *self, Py_buffer *view, int flags)
{
    *view = (Py_buffer){
        .obj = Py_NewRef(self),
        .buf = &self->data[0],
        .len = sizeof(GLM_TYPE_NAME),
        .itemsize = sizeof(float),
        .ndim = 1,
        .readonly = !FLAG_IS_SET(flags, PyBUF_WRITABLE),
        .format = FLAG_IS_SET(flags, PyBUF_FORMAT) ? "f" : NULL,
        .shape = FLAG_IS_SET(flags, PyBUF_ND) ? (Py_ssize_t[]){VEC_LEN} : NULL,
        .strides = FLAG_IS_SET(flags, PyBUF_STRIDES) ? (Py_ssize_t[]){sizeof(float)} : NULL,
    };

    return 0;
}
#pragma endregion

#pragma region tp_as_sequence
static Py_ssize_t PyVector_sq_length(PY_TYPE_NAME *self)
{
    (void)self;
    return VEC_LEN;
}

static PyObject *PyVector_sq_item(PY_TYPE_NAME *self, Py_ssize_t idx)
{
    if (idx >= VEC_LEN)
    {
        PyErr_Format(PyExc_IndexError, "Index too large.");
        return NULL;
    }

    return PyFloat_FromDouble((double)self->data[idx]);
}

static int PyVector_sq_ass_item(PY_TYPE_NAME *self, Py_ssize_t idx, PyObject *value)
{
    if (idx >= VEC_LEN)
    {
        PyErr_SetString(PyExc_IndexError, "Index too large.");
        return -1;
    }

    if (value == NULL)
    {
        PyErr_Format(PyExc_RuntimeError, "%s does not support item deletion.", Py_TYPE(self)->tp_name);
        return -1;
    }

    PyObject *floatValue = PyNumber_Float(value);
    if (floatValue == NULL)
    {
        PyErr_Format(PyExc_TypeError, "Expected value to be convertible to float, got: %s.", Py_TYPE(value)->tp_name);
        return -1;
    }

    self->data[idx] = (float)PyFloat_AS_DOUBLE(floatValue);
    Py_DECREF(floatValue);

    return 0;
}
#pragma endregion

#pragma region tp_as_number
static PY_TYPE_NAME *PyVector_nb_add(PY_TYPE_NAME *self, PyObject *other)
{
    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, &PY_TYPE_OBJECT_NAME);

    if (PyObject_IsInstance(other, (PyObject *)&PY_TYPE_OBJECT_NAME))
    {
        GLM_CALL_FUNC(add, self->data, ((PY_TYPE_NAME *)other)->data, new->data);
        return new;
    }

    PyObject *otherFloat = PyNumber_Float(other);
    if (otherFloat == NULL)
    {
        Py_DECREF(new);
        return (PY_TYPE_NAME *)&_Py_NotImplementedStruct;
    }

    GLM_CALL_FUNC(adds, self->data, (float)PyFloat_AS_DOUBLE(otherFloat), new->data);
    Py_DECREF(otherFloat);
    return new;
}

static PY_TYPE_NAME *PyVector_nb_inplace_add(PY_TYPE_NAME *self, PyObject *other)
{
    if (PyObject_IsInstance(other, (PyObject *)&PY_TYPE_OBJECT_NAME))
    {
        GLM_CALL_FUNC(add, self->data, ((PY_TYPE_NAME *)other)->data, self->data);
        return (PY_TYPE_NAME *)Py_NewRef(self);
    }

    PyObject *otherFloat = PyNumber_Float(other);
    if (otherFloat == NULL)
        return (PY_TYPE_NAME *)&_Py_NotImplementedStruct;

    GLM_CALL_FUNC(adds, self->data, (float)PyFloat_AS_DOUBLE(otherFloat), self->data);
    Py_DECREF(otherFloat);
    return (PY_TYPE_NAME *)Py_NewRef(self);
}

static PY_TYPE_NAME *PyVector_nb_subtract(PY_TYPE_NAME *self, PyObject *other)
{
    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, &PY_TYPE_OBJECT_NAME);

    if (PyObject_IsInstance(other, (PyObject *)&PY_TYPE_OBJECT_NAME))
    {
        GLM_CALL_FUNC(sub, self->data, ((PY_TYPE_NAME *)other)->data, new->data);
        return new;
    }

    PyObject *otherFloat = PyNumber_Float(other);
    if (otherFloat == NULL)
    {
        Py_DECREF(new);
        return (PY_TYPE_NAME *)&_Py_NotImplementedStruct;
    }

    GLM_CALL_FUNC(subs, self->data, (float)PyFloat_AS_DOUBLE(otherFloat), new->data);
    Py_DECREF(otherFloat);
    return new;
}

static PY_TYPE_NAME *PyVector_nb_inplace_subtract(PY_TYPE_NAME *self, PyObject *other)
{
    if (PyObject_IsInstance(other, (PyObject *)&PY_TYPE_OBJECT_NAME))
    {
        GLM_CALL_FUNC(sub, self->data, ((PY_TYPE_NAME *)other)->data, self->data);
        return (PY_TYPE_NAME *)Py_NewRef(self);
    }

    PyObject *otherFloat = PyNumber_Float(other);
    if (otherFloat == NULL)
        return (PY_TYPE_NAME *)&_Py_NotImplementedStruct;

    GLM_CALL_FUNC(subs, self->data, (float)PyFloat_AS_DOUBLE(otherFloat), self->data);
    Py_DECREF(otherFloat);
    return (PY_TYPE_NAME *)Py_NewRef(self);
}

static PY_TYPE_NAME *PyVector_nb_multiply(PY_TYPE_NAME *self, PyObject *other)
{
    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, &PY_TYPE_OBJECT_NAME);

    if (PyObject_IsInstance(other, (PyObject *)&PY_TYPE_OBJECT_NAME))
    {
        GLM_CALL_FUNC(mul, self->data, ((PY_TYPE_NAME *)other)->data, new->data);
        return new;
    }

    PyObject *otherFloat = PyNumber_Float(other);
    if (otherFloat == NULL)
    {
        Py_DECREF(new);
        return (PY_TYPE_NAME *)&_Py_NotImplementedStruct;
    }

    GLM_CALL_FUNC(scale, self->data, (float)PyFloat_AS_DOUBLE(otherFloat), new->data);
    Py_DECREF(otherFloat);
    return new;
}

static PY_TYPE_NAME *PyVector_nb_inplace_multiply(PY_TYPE_NAME *self, PyObject *other)
{
    if (PyObject_IsInstance(other, (PyObject *)&PY_TYPE_OBJECT_NAME))
    {
        GLM_CALL_FUNC(mul, self->data, ((PY_TYPE_NAME *)other)->data, self->data);
        return (PY_TYPE_NAME *)Py_NewRef(self);
    }

    PyObject *otherFloat = PyNumber_Float(other);
    if (otherFloat == NULL)
        return (PY_TYPE_NAME *)&_Py_NotImplementedStruct;

    GLM_CALL_FUNC(scale, self->data, (float)PyFloat_AS_DOUBLE(otherFloat), self->data);
    Py_DECREF(otherFloat);
    return (PY_TYPE_NAME *)Py_NewRef(self);
}

static PY_TYPE_NAME *PyVector_nb_true_divide(PY_TYPE_NAME *self, PyObject *other)
{
    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, &PY_TYPE_OBJECT_NAME);

    if (PyObject_IsInstance(other, (PyObject *)&PY_TYPE_OBJECT_NAME))
    {
        if (VECTOR_CHECK_ZERO(other))
        {
            PyErr_SetString(PyExc_ZeroDivisionError, "division by zero");
            return NULL;
        }

        GLM_CALL_FUNC(div, self->data, ((PY_TYPE_NAME *)other)->data, new->data);
        return new;
    }

    other = PyNumber_Float(other);
    if (other == NULL)
    {
        Py_DECREF(new);
        return (PY_TYPE_NAME *)&_Py_NotImplementedStruct;
    }

    float value = (float)PyFloat_AS_DOUBLE(other);
    if (value == 0.0f)
    {
        PyErr_SetString(PyExc_ZeroDivisionError, "division by zero");
        Py_DECREF(other);
        return NULL;
    }

    GLM_CALL_FUNC(divs, self->data, value, new->data);
    Py_DECREF(other);
    return new;
}

static PY_TYPE_NAME *PyVector_nb_inplace_true_divide(PY_TYPE_NAME *self, PyObject *other)
{
    if (PyObject_IsInstance(other, (PyObject *)&PY_TYPE_OBJECT_NAME))
    {
        if (VECTOR_CHECK_ZERO(other))
        {
            PyErr_SetString(PyExc_ZeroDivisionError, "division by zero");
            return NULL;
        }

        GLM_CALL_FUNC(div, self->data, ((PY_TYPE_NAME *)other)->data, self->data);
        return (PY_TYPE_NAME *)Py_NewRef(self);
    }

    other = PyNumber_Float(other);
    if (other == NULL)
        return (PY_TYPE_NAME *)&_Py_NotImplementedStruct;

    float value = (float)PyFloat_AS_DOUBLE(other);
    if (value == 0.0f)
    {
        PyErr_SetString(PyExc_ZeroDivisionError, "division by zero");
        Py_DECREF(other);
        return NULL;
    }

    GLM_CALL_FUNC(divs, self->data, value, self->data);
    Py_DECREF(other);
    return (PY_TYPE_NAME *)Py_NewRef(self);
}

static PY_TYPE_NAME *PyVector_nb_remainder(PY_TYPE_NAME *self, PyObject *other)
{
    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, &PY_TYPE_OBJECT_NAME);

    if (PyObject_IsInstance(other, (PyObject *)&PY_TYPE_OBJECT_NAME))
    {
        if (VECTOR_CHECK_ZERO(other))
        {
            PyErr_SetString(PyExc_ZeroDivisionError, "division by zero");
            return NULL;
        }

        for (Py_ssize_t i = 0; i < VEC_LEN; i++)
            new->data[i] = fmodf(self->data[i], ((PY_TYPE_NAME *)other)->data[i]);

        return new;
    }

    other = PyNumber_Float(other);
    if (other == NULL)
    {
        Py_DECREF(new);
        return (PY_TYPE_NAME *)&_Py_NotImplementedStruct;
    }

    float value = (float)PyFloat_AS_DOUBLE(other);
    if (value == 0.0f)
    {
        PyErr_SetString(PyExc_ZeroDivisionError, "division by zero");
        Py_DECREF(other);
        return NULL;
    }

    for (Py_ssize_t i = 0; i < VEC_LEN; i++)
        new->data[i] = fmodf(self->data[i], value);

    Py_DECREF(other);
    return new;
}

static PY_TYPE_NAME *PyVector_nb_inplace_remainder(PY_TYPE_NAME *self, PyObject *other)
{
    if (PyObject_IsInstance(other, (PyObject *)&PY_TYPE_OBJECT_NAME))
    {
        if (VECTOR_CHECK_ZERO(other))
        {
            PyErr_SetString(PyExc_ZeroDivisionError, "division by zero");
            return NULL;
        }

        for (Py_ssize_t i = 0; i < VEC_LEN; i++)
            self->data[i] = fmodf(self->data[i], ((PY_TYPE_NAME *)other)->data[i]);

        return (PY_TYPE_NAME *)Py_NewRef(self);
    }

    other = PyNumber_Float(other);
    if (other == NULL)
        return (PY_TYPE_NAME *)&_Py_NotImplementedStruct;

    float value = (float)PyFloat_AS_DOUBLE(other);
    if (value == 0.0f)
    {
        PyErr_SetString(PyExc_ZeroDivisionError, "division by zero");
        Py_DECREF(other);
        return NULL;
    }

    for (Py_ssize_t i = 0; i < VEC_LEN; i++)
        self->data[i] = fmodf(self->data[i], value);

    Py_DECREF(other);
    return (PY_TYPE_NAME *)Py_NewRef(self);
}

static PY_TYPE_NAME *PyVector_nb_negative(PY_TYPE_NAME *self)
{
    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, &PY_TYPE_OBJECT_NAME);
    GLM_CALL_FUNC(negate_to, self->data, new->data);
    return new;
}
#pragma endregion

static PyVectorIter *PyVector_Iter(PY_TYPE_NAME *self)
{
    PyVectorIter *iter = PyObject_New(PyVectorIter, &PyVectorIter_Type);
    if (iter == NULL)
        return NULL;

    iter->object = (_PyVectorAbstract *)Py_NewRef((PyObject *)self);
    iter->current = 0;
    iter->end = VEC_LEN;

    return iter;
}

#if VEC_LEN != 4
static PyObject *PyVector_cross(PY_TYPE_NAME *self, PY_TYPE_NAME *other)
{
    if (!CheckTypeSelf((PyObject *)other))
        return NULL;

#if VEC_LEN == 2
    return PyFloat_FromDouble((double)GLM_CALL_FUNC(cross, self->data, other->data));
#else
    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, &PY_TYPE_OBJECT_NAME);
    GLM_CALL_FUNC(cross, self->data, other->data, new->data);

    return (PyObject *)new;
#endif
}
#endif

static PyObject *PyVector_dot(PY_TYPE_NAME *self, PY_TYPE_NAME *other)
{
    if (!CheckTypeSelf((PyObject *)other))
        return NULL;

    return PyFloat_FromDouble((double)GLM_CALL_FUNC(dot, self->data, other->data));
}

static PyObject *PyVector_length(PY_TYPE_NAME *self, PyObject *args)
{
    (void)args;
    return PyFloat_FromDouble((double)sqrtf(GetVectorLengthSquared(self)));
}

static PyObject *PyVector_length_squared(PY_TYPE_NAME *self, PyObject *args)
{
    (void)args;

    return PyFloat_FromDouble((double)GetVectorLengthSquared(self));
}

#if VEC_LEN == 3
static PyObject *PyVector_angle(PY_TYPE_NAME *self, PY_TYPE_NAME *other)
{
    if (!CheckTypeSelf((PyObject *)other))
        return NULL;

    return PyFloat_FromDouble((double)GLM_CALL_FUNC(angle, self->data, other->data));
}
#endif

static PyObject *PyVector_distance(PY_TYPE_NAME *self, PY_TYPE_NAME *other)
{
    if (!CheckTypeSelf((PyObject *)other))
        return NULL;

    return PyFloat_FromDouble((double)GLM_CALL_FUNC(distance, self->data, other->data));
}

static PyObject *PyVector_distance_squared(PY_TYPE_NAME *self, PY_TYPE_NAME *other)
{
    if (!CheckTypeSelf((PyObject *)other))
        return NULL;

    return PyFloat_FromDouble((double)GLM_CALL_FUNC(distance2, self->data, other->data));
}

static PyObject *PyVector_normalize(PY_TYPE_NAME *self, PyObject *args)
{
    (void)args;
    GLM_CALL_FUNC(normalize, self->data);
    Py_RETURN_NONE;
}

static PY_TYPE_NAME *PyVector_normalized(PY_TYPE_NAME *self, PyObject *args)
{
    (void)args;
    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, &PY_TYPE_OBJECT_NAME);
    GLM_CALL_FUNC(normalize_to, self->data, new->data);

    return new;
}

static PY_TYPE_NAME *PyVector_interpolate(PY_TYPE_NAME *self, PyObject *const *args, Py_ssize_t nArgs)
{
    PY_TYPE_NAME *other;
    float t;
    if (!_PyArg_ParseStack(args, nArgs, "O!f", &PY_TYPE_OBJECT_NAME, &other, &t))
        return NULL;

    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, &PY_TYPE_OBJECT_NAME);
    GLM_CALL_FUNC(lerp, self->data, other->data, t, new->data);

    return new;
}

static PY_TYPE_NAME *PyVector_one(PyTypeObject *cls, PyObject *args)
{
    (void)args;

    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, cls);
    new = (PY_TYPE_NAME *)PyObject_Init((PyObject *)new, cls);

    GLM_CALL_FUNC(one, new->data);

    return new;
}

static PY_TYPE_NAME *PyVector_zero(PyTypeObject *cls, PyObject *args)
{
    (void)args;

    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, cls);
    new = (PY_TYPE_NAME *)PyObject_Init((PyObject *)new, cls);

    GLM_CALL_FUNC(zero, new->data);

    return new;
}

static PY_TYPE_NAME *PyVector_unit_x(PyTypeObject *cls, PyObject *args)
{
    (void)args;

    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, cls);
    new = (PY_TYPE_NAME *)PyObject_Init((PyObject *)new, cls);
    GLM_CALL_FUNC(zero, new->data);
    new->data[0] = 1.0f;

    return new;
}

static PY_TYPE_NAME *PyVector_unit_y(PyTypeObject *cls, PyObject *args)
{
    (void)args;

    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, cls);
    new = (PY_TYPE_NAME *)PyObject_Init((PyObject *)new, cls);
    GLM_CALL_FUNC(zero, new->data);
    new->data[1] = 1.0f;

    return new;
}

#if VEC_LEN > 2
static PY_TYPE_NAME *PyVector_unit_z(PyTypeObject *cls, PyObject *args)
{
    (void)args;

    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, cls);
    new = (PY_TYPE_NAME *)PyObject_Init((PyObject *)new, cls);
    GLM_CALL_FUNC(zero, new->data);
    new->data[2] = 1.0f;

    return new;
}
#endif

#if VEC_LEN > 3
static PY_TYPE_NAME *PyVector_unit_w(PyTypeObject *cls, PyObject *args)
{
    (void)args;

    PY_TYPE_NAME *new = PyObject_New(PY_TYPE_NAME, cls);
    new = (PY_TYPE_NAME *)PyObject_Init((PyObject *)new, cls);
    GLM_CALL_FUNC(zero, new->data);
    new->data[3] = 1.0f;

    return new;
}
#endif

static PyObject *PyVector_richcompare(PY_TYPE_NAME *self, PY_TYPE_NAME *other, int func)
{
    switch (func)
    {
    case Py_EQ:
        if (self == other)
            Py_RETURN_TRUE;

        if (!PyObject_IsInstance((PyObject *)other, (PyObject *)Py_TYPE(self)))
            Py_RETURN_NOTIMPLEMENTED;

        return PyBool_FromLong(GLM_CALL_FUNC(eqv, self->data, other->data));
    case Py_NE:
        if (self != other)
            Py_RETURN_TRUE;

        if (!PyObject_IsInstance((PyObject *)other, (PyObject *)Py_TYPE(self)))
            Py_RETURN_NOTIMPLEMENTED;

        return PyBool_FromLong(!GLM_CALL_FUNC(eqv, self->data, other->data));
    }

    PyErr_SetString(PyExc_TypeError, "Vector types do not support less than or greater than comparisons.");
    return NULL;
}

PyTypeObject PY_TYPE_OBJECT_NAME = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_basicsize = sizeof(PY_TYPE_NAME),
    .tp_name = MACRO_CONCAT("spyke.math.Vector", MACRO_STRINGIFY(VEC_LEN)),
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)VECTOR_INIT_FUNC,
    .tp_str = (reprfunc)VECTOR_STR_FUNC,
    .tp_richcompare = (richcmpfunc)PyVector_richcompare,
    .tp_iter = (getiterfunc)PyVector_Iter,
    .tp_as_buffer = &(PyBufferProcs){
        .bf_getbuffer = (getbufferproc)PyVector_bf_getbuffer,
        .bf_releasebuffer = NULL,
    },
    .tp_as_sequence = &(PySequenceMethods){
        .sq_length = (lenfunc)PyVector_sq_length,
        .sq_item = (ssizeargfunc)PyVector_sq_item,
        .sq_ass_item = (ssizeobjargproc)PyVector_sq_ass_item,
    },
    .tp_as_number = &(PyNumberMethods){
        .nb_add = (binaryfunc)PyVector_nb_add,
        .nb_inplace_add = (binaryfunc)PyVector_nb_inplace_add,
        .nb_subtract = (binaryfunc)PyVector_nb_subtract,
        .nb_inplace_subtract = (binaryfunc)PyVector_nb_inplace_subtract,
        .nb_multiply = (binaryfunc)PyVector_nb_multiply,
        .nb_inplace_multiply = (binaryfunc)PyVector_nb_inplace_multiply,
        .nb_true_divide = (binaryfunc)PyVector_nb_true_divide,
        .nb_inplace_true_divide = (binaryfunc)PyVector_nb_inplace_true_divide,
        .nb_remainder = (binaryfunc)PyVector_nb_remainder,
        .nb_inplace_remainder = (binaryfunc)PyVector_nb_inplace_remainder,
        .nb_negative = (unaryfunc)PyVector_nb_negative,
    },
    .tp_members = (PyMemberDef[]){
        {"x", Py_T_FLOAT, offsetof(PY_TYPE_NAME, data[0]), 0, NULL},
        {"y", Py_T_FLOAT, offsetof(PY_TYPE_NAME, data[1]), 0, NULL},
#if VEC_LEN > 2
        {"z", Py_T_FLOAT, offsetof(PY_TYPE_NAME, data[2]), 0, NULL},
#endif
#if VEC_LEN > 3
        {"w", Py_T_FLOAT, offsetof(PY_TYPE_NAME, data[3]), 0, NULL},
#endif
        {0},
    },
    .tp_methods = (PyMethodDef[]){
        {"one", (PyCFunction)PyVector_one, METH_NOARGS | METH_CLASS, NULL},
        {"zero", (PyCFunction)PyVector_zero, METH_NOARGS | METH_CLASS, NULL},
        {"unit_x", (PyCFunction)PyVector_unit_x, METH_NOARGS | METH_CLASS, NULL},
        {"unit_y", (PyCFunction)PyVector_unit_y, METH_NOARGS | METH_CLASS, NULL},
#if VEC_LEN > 2
        {"unit_z", (PyCFunction)PyVector_unit_z, METH_NOARGS | METH_CLASS, NULL},
#endif
#if VEC_LEN > 3
        {"unit_w", (PyCFunction)PyVector_unit_w, METH_NOARGS | METH_CLASS, NULL},
#endif
        {"length", (PyCFunction)PyVector_length, METH_NOARGS, NULL},
        {"length_squared", (PyCFunction)PyVector_length_squared, METH_NOARGS, NULL},
        {"dot", (PyCFunction)PyVector_dot, METH_O, NULL},
#if VEC_LEN == 3
        {"angle", (PyCFunction)PyVector_angle, METH_O, NULL},
#endif
        {"distance", (PyCFunction)PyVector_distance, METH_O, NULL},
        {"distance_squared", (PyCFunction)PyVector_distance_squared, METH_O, NULL},
        {"normalize", (PyCFunction)PyVector_normalize, METH_NOARGS, NULL},
        {"normalized", (PyCFunction)PyVector_normalized, METH_NOARGS, NULL},
        {"interpolate", (PyCFunction)PyVector_interpolate, METH_FASTCALL, NULL},
#if VEC_LEN != 4
        {"cross", (PyCFunction)PyVector_cross, METH_O, NULL},
#endif
        {0},
    },
};
