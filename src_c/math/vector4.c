#define VEC_LEN 4
#include "vectorTemplate.h"

static int PyVector4_init(PyVector4 *self, PyObject *args, PyObject *kwargs)
{
    (void)kwargs;
    const Py_ssize_t nArgs = PyTuple_GET_SIZE(args);
    if (nArgs == 1)
    {
        PyObject *valueObj = PyTuple_GET_ITEM(args, 0);
        CHECK_ARG_FLOAT(valueObj, -1);

        float value = (float)PyFloat_AS_DOUBLE(valueObj);
        self->data[0] = value;
        self->data[1] = value;
        self->data[2] = value;
        self->data[3] = value;
    }
    else if (nArgs == 4)
    {
        if (!PyArg_ParseTuple(args, "ffff", &self->data[0], &self->data[1], &self->data[2], &self->data[3]))
            return -1;
    }
    else
    {
        PyErr_Format(PyExc_ValueError, "Expected 1 or 4 arguments, got: %d.", nArgs);
        return -1;
    }

    return 0;
}

static PyObject *PyVector4_str(PyVector4 *self)
{
    char buffer[128];
    int size = snprintf(
        buffer,
        sizeof(buffer),
        "<%s (%.3f, %.3f, %.3f, %.3f) at 0x%p>",
        Py_TYPE(self)->tp_name,
        self->data[0],
        self->data[1],
        self->data[2],
        self->data[3],
        (void *)self);

    return PyUnicode_FromStringAndSize(buffer, size);
}

static bool PyVector4_check_zero(PyVector4 *self)
{
    return self->data[0] == 0.0f || self->data[1] == 0.0f || self->data[2] == 0.0f || self->data[3] == 0.0f;
}
