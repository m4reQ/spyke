#include "vertexArray.h"

static int PyVertexDescriptor_init(PyVertexDescriptor *self, PyObject *args, PyObject *kwargs)
{
    static char *kwNames[] = {"attrib_index", "type", "count", "rows", "is_normalized", NULL};

    self->rows = 1;
    if (!PyArg_ParseTupleAndKeywords(
            args,
            kwargs,
            "IIi|Ip",
            kwNames,
            &self->attribIndex,
            &self->type,
            &self->count,
            &self->rows,
            &self->isNormalized))
        return -1;

    return 0;
}

PyTypeObject PyVertexDescriptor_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.graphics.gl.VertexDescriptor",
    .tp_basicsize = sizeof(PyVertexDescriptor),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)PyVertexDescriptor_init,
    .tp_members = (PyMemberDef[]){
        {"attrib_index", Py_T_UINT, offsetof(PyVertexDescriptor, attribIndex), 0, NULL},
        {"type", Py_T_UINT, offsetof(PyVertexDescriptor, type), 0, NULL},
        {"count", Py_T_INT, offsetof(PyVertexDescriptor, count), 0, NULL},
        {"rows", Py_T_INT, offsetof(PyVertexDescriptor, rows), 0, NULL},
        {"is_normalized", Py_T_BOOL, offsetof(PyVertexDescriptor, isNormalized), 0, NULL},
        {0},
    },
};
