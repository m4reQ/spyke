#include "sync.h"

#define AUTO_SYNC_TIMEOUT_NS 100
#define SYNC_SIGNALED(state) (state == GL_ALREADY_SIGNALED || state == GL_CONDITION_SATISFIED)

static PyObject *PySync_set(PySync *self, PyObject *args)
{
    (void)args;
    glDeleteSync(self->sync);
    self->sync = glFenceSync(GL_SYNC_GPU_COMMANDS_COMPLETE, 0);

    Py_RETURN_NONE;
}

static PyObject *PySync_wait(PySync *self, PyObject *args, PyObject *kwargs)
{
    static char *kwNames[] = {"timeout", NULL};

    if (self->sync == NULL)
        Py_RETURN_TRUE;

    GLuint64 timeout = 0;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|K", kwNames, &timeout))
        return NULL;

    GLenum waitState;
    if (timeout == 0)
    {
        do
        {
            waitState = glClientWaitSync(self->sync, GL_SYNC_FLUSH_COMMANDS_BIT, AUTO_SYNC_TIMEOUT_NS);
        } while (!SYNC_SIGNALED(waitState));
        waitState = GL_CONDITION_SATISFIED;
    }
    else
    {
        waitState = glClientWaitSync(self->sync, GL_SYNC_FLUSH_COMMANDS_BIT, timeout);
    }

    glDeleteSync(self->sync);
    self->sync = NULL;

    return PyBool_FromLong(SYNC_SIGNALED(waitState));
}

static PyObject *PySync_delete(PySync *self, PyObject *args)
{
    (void)args;

    glDeleteSync(self->sync);
    self->sync = NULL;

    Py_RETURN_NONE;
}

static PyObject *PySync_is_signaled(PySync *self, PyObject *args)
{
    (void)args;

    if (self->sync == NULL)
        Py_RETURN_TRUE;

    GLint syncStatus;
    glGetSynciv(self->sync, GL_SYNC_STATUS, 1, NULL, &syncStatus);

    return PyBool_FromLong(syncStatus == GL_SIGNALED);
}

static PyObject *PySync_set_debug_name(PySync *self, PyObject *name)
{
    CHECK_ARG_STRING(name, NULL);

    Py_ssize_t nameLength = 0;
    const char *nameStr = PyUnicode_AsUTF8AndSize(name, &nameLength);

    glObjectPtrLabel(self->sync, nameLength, nameStr);

    Py_RETURN_NONE;
}

PyTypeObject PySync_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.graphics.gl.Sync",
    .tp_basicsize = sizeof(PySync),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_methods = (PyMethodDef[]){
        {"set", (PyCFunction)PySync_set, METH_NOARGS, NULL},
        {"wait", (PyCFunction)PySync_wait, METH_VARARGS | METH_KEYWORDS, NULL},
        {"delete", (PyCFunction)PySync_delete, METH_NOARGS, NULL},
        {"is_signaled", (PyCFunction)PySync_is_signaled, METH_NOARGS, NULL},
        {"set_debug_name", (PyCFunction)PySync_set_debug_name, METH_O, NULL},
        {0},
    },
};
