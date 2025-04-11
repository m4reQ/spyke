#define VEC_LEN 2
#include "vectorTemplate.h"

static int PyVector2_init_multiple_args(PyVector2 *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, "ff", &self->data[0], &self->data[1]))
        return -1;

    return 0;
}

static PyObject *PyVector2_str(PyVector2 *self)
{
    char buffer[128];
    int size = snprintf(
        buffer,
        sizeof(buffer),
        "<%s (%.3f, %.3f) at 0x%p>",
        Py_TYPE(self)->tp_name,
        self->data[0],
        self->data[1],
        (void *)self);

    return PyUnicode_FromStringAndSize(buffer, size);
}

static bool PyVector2_check_zero(PyVector2 *self)
{
    return self->data[0] == 0.0f || self->data[1] == 0.0f;
}
