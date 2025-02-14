#include "events.h"
#include "../api.h"
#include <stdlib.h>
#include <stb_ds.h>

static _PyArg_Parser PyEvent_Subscribe_parser = {
    .format = "O|ip",
    .keywords = (const char *[]){"", "priority", "should_consume", NULL},
};

static int HandlersSortFunc(const EventHandler *a, const EventHandler *b)
{
    return a->priority < b->priority;
}

static void PyEvent_Dealloc(PyEvent *self)
{
    for (size_t i = 0; i < arrlenu(self->handlers); i++)
        Py_DecRef(self->handlers[i].pyCallback);

    arrfree(self->handlers);

    Py_TYPE(self)->tp_free(self);
}

static PyObject *PyEvent_New(PyTypeObject *cls, PyObject *args, PyObject *kwargs)
{
    (void)args;
    (void)kwargs;

    PyEvent *self = (PyEvent *)cls->tp_alloc(cls, 1);
    self->handlers = NULL;

    return (PyObject *)self;
}

static PyObject *PyEvent_Subscribe(PyEvent *self, PyObject **args, Py_ssize_t argsCount, PyObject *kwargs)
{
    PyObject *callback;
    int priority = 0;
    bool shouldConsume = false;
    if (!_PyArg_ParseStackAndKeywords(
            args,
            argsCount,
            kwargs,
            &PyEvent_Subscribe_parser,
            &callback,
            &priority,
            &shouldConsume))
        return NULL;

    CHECK_ARG_CALLABLE(callback, NULL);

    const EventHandler handler = {Py_NewRef(callback), priority, shouldConsume};
    arrput(self->handlers, handler);
    qsort(self->handlers, arrlenu(self->handlers), sizeof(EventHandler), HandlersSortFunc);

    Py_RETURN_NONE;
}

static PyObject *PyEvent_Unsubscribe(PyEvent *self, PyObject *callback)
{
    CHECK_ARG_CALLABLE(callback, NULL);

    for (size_t i = 0; i < arrlenu(self->handlers); i++)
    {
        if (self->handlers[i].pyCallback == callback)
        {
            arrdel(self->handlers, i);
            break;
        }
    }

    Py_RETURN_NONE;
}

static PyObject *PyEvent_Invoke(PyEvent *self, PyObject *eventData)
{
    for (size_t i = 0; i < arrlenu(self->handlers); i++)
    {
        const EventHandler *handler = &self->handlers[i];
        if (!PyObject_CallOneArg(handler->pyCallback, Py_NewRef(eventData)))
            return NULL;

        if (handler->shouldConsume)
            break;
    }

    Py_RETURN_NONE;
}

static PyObject *PyEvent_ClearHandlers(PyEvent *self, PyObject *args)
{
    (void)args;

    for (size_t i = 0; i < arrlenu(self->handlers); i++)
        Py_DecRef(self->handlers[i].pyCallback);

    arrsetlen(self->handlers, 0);

    Py_RETURN_NONE;
}

static PyTypeObject s_EventType = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.events.Event",
    .tp_basicsize = sizeof(PyEvent),
    .tp_dealloc = (destructor)PyEvent_Dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyEvent_New,
    .tp_methods = (PyMethodDef[]){
        {"__class_getitem__", Py_GenericAlias, METH_O | METH_CLASS, NULL},
        {"subscribe", (PyCFunction)PyEvent_Subscribe, METH_FASTCALL | METH_KEYWORDS, NULL},
        {"unsubscribe", (PyCFunction)PyEvent_Subscribe, METH_O, NULL},
        {"invoke", (PyCFunction)PyEvent_Invoke, METH_O, NULL},
        {"clear_handlers", (PyCFunction)PyEvent_ClearHandlers, METH_NOARGS, NULL},
        {0},
    },
};

static EventsAPI s_API = {
    .pyEventType = &s_EventType,
    .pyEventInvoke = PyEvent_Invoke,
};

static PyModuleDef s_ModuleDef = {
    PyModuleDef_HEAD_INIT,
    .m_name = "spyke.events",
    .m_size = -1,
};

PyMODINIT_FUNC PyInit_events()
{
    PyObject *module = PyModule_Create(&s_ModuleDef);
    if (!module ||
        !PyAPI_Add(module, &s_API) ||
        PyModule_AddType(module, &s_EventType))
        return NULL;

    return module;
}
