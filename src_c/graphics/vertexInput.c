#include "vertexArray.h"
#include "buffer.h"

static int PyVertexInput_init(PyVertexInput *self, PyObject *args, PyObject *kwargs)
{
    static char *kwNames[] = {"buffer", "stride", "descriptors", "offset", "divisor", NULL};

    PyObject *buffer = NULL;
    PyObject *descriptors = NULL;
    if (!PyArg_ParseTupleAndKeywords(
            args, kwargs, "OiO!|LI", kwNames,
            &buffer, &self->stride, &PyList_Type, &descriptors,
            &self->offset, &self->divisor))
        return -1;

    if (Py_IsNone(buffer))
    {
        self->bufferId = (GLuint)-1;
    }
    else
    {
        if (!PyObject_IsInstance(buffer, (PyObject *)&PyBuffer_Type))
        {
            PyErr_Format(PyExc_TypeError, "Expected buffer to be of type spyke.graphics.gl.Buffer, got: %s", Py_TYPE(buffer)->tp_name);
            return -1;
        }

        self->bufferId = ((PyBuffer *)buffer)->id;
    }

    // check types of every element in `descriptors` here to avoid later errors
    Py_ssize_t nDesc = PyList_GET_SIZE(descriptors);
    for (Py_ssize_t i = 0; i < nDesc; i++)
    {
        if (!PyObject_IsInstance(PyList_GET_ITEM(descriptors, i), (PyObject *)&PyVertexDescriptor_Type))
        {
            PyErr_SetString(PyExc_TypeError, "Every element in descriptors list has to be of type spyke.graphics.gl.VertexDescriptor");
            return -1;
        }
    }

    self->descriptors = Py_NewRef(descriptors);

    return 0;
}

static void PyVertexInput_dealloc(PyVertexInput *self)
{
    Py_CLEAR(self->descriptors);
    Py_TYPE(self)->tp_free(self);
}

PyTypeObject PyVertexInput_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_name = "spyke.graphics.gl.VertexInput",
    .tp_init = (initproc)PyVertexInput_init,
    .tp_dealloc = (destructor)PyVertexInput_dealloc,
    .tp_basicsize = sizeof(PyVertexInput),
    .tp_members = (PyMemberDef[]){
        {"buffer_id", Py_T_UINT, offsetof(PyVertexInput, bufferId), 0, NULL},
        {"stride", Py_T_INT, offsetof(PyVertexInput, stride), 0, NULL},
        {"descriptors", Py_T_OBJECT_EX, offsetof(PyVertexInput, descriptors), 0, NULL},
        {"offset", Py_T_LONGLONG, offsetof(PyVertexInput, offset), 0, NULL},
        {"divisor", Py_T_UINT, offsetof(PyVertexInput, divisor), 0, NULL},
        {0},
    },
};
