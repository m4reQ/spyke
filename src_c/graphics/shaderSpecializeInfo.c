#include "shader.h"

static int PyShaderSpecializeInfo_init(PyShaderSpecializeInfo *self, PyObject *args, PyObject *kwargs)
{
    (void)kwargs;

    if (!PyArg_ParseTuple(args, "UO!", &self->entryPoint, &PyList_Type, &self->constants))
        return -1;

    for (Py_ssize_t i = 0; i < PyList_GET_SIZE(self->constants); i++)
    {
        PyObject *item = PyList_GET_ITEM(self->constants, i);
        if (!PyTuple_Check(item))
        {
            PyErr_Format(PyExc_TypeError, "constants must be a list of tuples of (int, int), got %s at position %d.", Py_TYPE(item)->tp_name, i);
            return -1;
        }

        const Py_ssize_t itemLength = PyTuple_GET_SIZE(item);
        if (itemLength != 2)
        {
            PyErr_Format(PyExc_ValueError, "Each item of constants list must be of length 2 (got %d at position %d).", itemLength, i);
            return -1;
        }

        PyObject *constantIndex = PyTuple_GET_ITEM(item, 0);
        if (!PyLong_Check(constantIndex))
        {
            PyErr_Format(PyExc_TypeError, "Expected item 0 of specialization constant %d to be an int, got: %s.", i, Py_TYPE(constantIndex)->tp_name);
            return -1;
        }

        PyObject *constantValue = PyTuple_GET_ITEM(item, 1);
        if (!PyLong_Check(constantValue))
        {
            PyErr_Format(PyExc_TypeError, "Expected item 1 of specialization constant %d to be an int, got: %s.", i, Py_TYPE(constantValue)->tp_name);
            return -1;
        }
    }

    Py_INCREF(self->entryPoint);
    Py_INCREF(self->constants);

    return 0;
}

static void PyShaderSpecializeInfo_dealloc(PyShaderSpecializeInfo *self)
{
    Py_XDECREF(self->constants);
    Py_XDECREF(self->entryPoint);
    Py_TYPE(self)->tp_free(self);
}

PyTypeObject PyShaderSpecializeInfo_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.graphics.gl.ShaderSpecializeInfo",
    .tp_basicsize = sizeof(PyShaderSpecializeInfo),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)PyShaderSpecializeInfo_init,
    .tp_dealloc = (destructor)PyShaderSpecializeInfo_dealloc,
    .tp_members = (PyMemberDef[]){
        {"entry_point", Py_T_OBJECT_EX, offsetof(PyShaderSpecializeInfo, entryPoint), 0, NULL},
        {"constants", Py_T_OBJECT_EX, offsetof(PyShaderSpecializeInfo, constants), 0, NULL},
        {0},
    },
};
