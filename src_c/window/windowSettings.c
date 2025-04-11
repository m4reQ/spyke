#include "windowSettings.h"
#include "../utils.h"

static int PyWindowSettings_Init(PyWindowSettings *self, PyObject *args, PyObject *kwargs)
{
    self->flags = WND_FLAGS_DEFAULT;
    self->useDebugContext = false;
    if (!PyArg_ParseTupleAndKeywords(
            args,
            kwargs,
            "IIU|Ip",
            (char *[]){"width", "height", "title", "flags", "use_debug_context", NULL},
            &self->width,
            &self->height,
            &self->pyTitle,
            &self->flags,
            &self->useDebugContext))
        return -1;

    Py_IncRef(self->pyTitle);

    return 0;
}

static void PyWindowSettings_Dealloc(PyWindowSettings *self)
{
    Py_DecRef(self->pyTitle);
    Py_TYPE(self)->tp_free(self);
}

PyTypeObject PyWindowSettings_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.graphics.window.WindowSettings",
    .tp_basicsize = sizeof(PyWindowSettings),
    .tp_new = PyType_GenericNew,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_dealloc = (destructor)PyWindowSettings_Dealloc,
    .tp_init = (initproc)PyWindowSettings_Init,
    .tp_members = (PyMemberDef[]){
        {"width", Py_T_UINT, offsetof(PyWindowSettings, width), 0, NULL},
        {"height", Py_T_UINT, offsetof(PyWindowSettings, height), 0, NULL},
        {"title", Py_T_OBJECT_EX, offsetof(PyWindowSettings, pyTitle), 0, NULL},
        {"flags", Py_T_UINT, offsetof(PyWindowSettings, flags), 0, NULL},
        {"use_debug_context", Py_T_BOOL, offsetof(PyWindowSettings, useDebugContext), 0, NULL},
        {0},
    },
};
