#define VEC_LEN 4
#include "vectorTemplate.h"

static int PyVector4_init_multiple_args(PyVector4 *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, "ffff", &self->data[0], &self->data[1], &self->data[2], &self->data[3]))
        return -1;

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
