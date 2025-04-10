#include "vector.h"

static PyVectorIter *PyVectorIter_Iter(PyVectorIter *self)
{
    return Py_NewRef(self);
}

static PyVectorIter *PyVectorIter_IterNext(PyVectorIter *self)
{
    if (self->current >= self->end)
        return NULL;

    PyObject *result = PyFloat_FromDouble((double)self->object->data[self->current]);
    self->current++;

    return result;
}

PyTypeObject PyVectorIter_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_basicsize = sizeof(PyVectorIter),
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IMMUTABLETYPE,
    .tp_new = PyType_GenericNew,
    .tp_name = "spyke.math.VectorIter",
    .tp_iter = (getiterfunc)PyVectorIter_Iter,
    .tp_iternext = (iternextfunc)PyVectorIter_IterNext,
};
