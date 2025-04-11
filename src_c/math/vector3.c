#define VEC_LEN 3
#include "vectorTemplate.h"

static int PyVector3_init_multiple_args(PyVector3 *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, "fff", &self->data[0], &self->data[1], &self->data[2]))
        return -1;

    return 0;
}

static PyObject *PyVector3_str(PyVector3 *self)
{
    char buffer[128];
    int size = snprintf(
        buffer,
        sizeof(buffer),
        "<%s (%.3f, %.3f, %.3f) at 0x%p>",
        Py_TYPE(self)->tp_name,
        self->data[0],
        self->data[1],
        self->data[2],
        (void *)self);

    return PyUnicode_FromStringAndSize(buffer, size);
}

static bool PyVector3_check_zero(PyVector3 *self)
{
    return self->data[0] == 0.0f || self->data[1] == 0.0f || self->data[2] == 0.0f;
}
