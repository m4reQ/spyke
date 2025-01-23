#include "windowEvents.h"

static PyObject *PyResizeEventData_GetSize(PyResizeEventData *self, void *UNUSED(closure))
{
    return PyTuple_Pack(2, PyLong_FromUnsignedLong(self->width), PyLong_FromUnsignedLong(self->height));
}

static PyObject *PyButtonUpEventData_GetPosition(PyButtonDownEventData *self, void *UNUSED(closure))
{
    return PyTuple_Pack(2, PyLong_FromUnsignedLong(self->x), PyLong_FromUnsignedLong(self->y));
}

static PyObject *PyButtonDownEventData_GetPosition(PyButtonDownEventData *self, void *UNUSED(closure))
{
    return PyTuple_Pack(2, PyLong_FromUnsignedLong(self->x), PyLong_FromUnsignedLong(self->y));
}

static PyObject *PyCharEventData_GetCharacter(PyCharEventData *self, void *UNUSED(closure))
{
    return PyUnicode_FromOrdinal(self->character);
}

static PyObject *PyScrollEventData_GetPosition(PyScrollEventData *self, void *UNUSED(closure))
{
    return PyTuple_Pack(2, PyLong_FromUnsignedLong(self->x), PyLong_FromUnsignedLong(self->y));
}

static PyObject *PyMouseMoveEventData_GetPosition(PyMouseMoveEventData *self, void *UNUSED(closure))
{
    return PyTuple_Pack(2, PyLong_FromUnsignedLong(self->x), PyLong_FromUnsignedLong(self->y));
}

static PyObject *PyMoveEventData_GetPosition(PyMoveEventData *self, void *UNUSED(closure))
{
    return PyTuple_Pack(2, PyLong_FromUnsignedLong(self->x), PyLong_FromUnsignedLong(self->y));
}

PyTypeObject PyResizeEventData_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.window.ResizeEventData",
    .tp_basicsize = sizeof(PyResizeEventData),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_getset = (PyGetSetDef[]){
        {"size", (getter)PyResizeEventData_GetSize, NULL, NULL, NULL},
        {0},
    },
    .tp_members = (PyMemberDef[]){
        {"width", Py_T_USHORT, offsetof(PyResizeEventData, width), 0, NULL},
        {"height", Py_T_USHORT, offsetof(PyResizeEventData, height), 0, NULL},
        {0},
    },
};

PyTypeObject PyButtonUpEventData_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.window.ButtonUpEventData",
    .tp_basicsize = sizeof(PyButtonUpEventData),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_getset = (PyGetSetDef[]){
        {"position", (getter)PyButtonUpEventData_GetPosition, NULL, NULL, NULL},
        {0},
    },
    .tp_members = (PyMemberDef[]){
        {"x", Py_T_USHORT, offsetof(PyButtonDownEventData, x), 0, NULL},
        {"y", Py_T_USHORT, offsetof(PyButtonDownEventData, y), 0, NULL},
        {"button", Py_T_UBYTE, offsetof(PyButtonDownEventData, button), 0, NULL},
        {"modifiers", Py_T_UBYTE, offsetof(PyButtonDownEventData, modifiers), 0, NULL},
        {0},
    },
};

PyTypeObject PyButtonDownEventData_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.window.ButtonDownEventData",
    .tp_basicsize = sizeof(PyButtonDownEventData),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_getset = (PyGetSetDef[]){
        {"position", (getter)PyButtonDownEventData_GetPosition, NULL, NULL, NULL},
        {0},
    },
    .tp_members = (PyMemberDef[]){
        {"x", Py_T_USHORT, offsetof(PyButtonDownEventData, x), 0, NULL},
        {"y", Py_T_USHORT, offsetof(PyButtonDownEventData, y), 0, NULL},
        {"button", Py_T_UBYTE, offsetof(PyButtonDownEventData, button), 0, NULL},
        {"modifiers", Py_T_UBYTE, offsetof(PyButtonDownEventData, modifiers), 0, NULL},
        {0},
    },
};

PyTypeObject PyCharEventData_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.window.CharEventData",
    .tp_basicsize = sizeof(PyCharEventData),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_getset = (PyGetSetDef[]){
        {"character", (getter)PyCharEventData_GetCharacter, NULL, NULL, NULL},
        {0},
    },
    .tp_members = (PyMemberDef[]){
        {"repeat_count", Py_T_USHORT, offsetof(PyCharEventData, repeatCount), 0, NULL},
        {"scan_code", Py_T_UBYTE, offsetof(PyCharEventData, scanCode), 0, NULL},
        {"was_pressed", Py_T_BOOL, offsetof(PyCharEventData, wasPressed), 0, NULL},
        {0},
    },
};

PyTypeObject PyKeyUpEventData_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.window.KeyUpEventData",
    .tp_basicsize = sizeof(PyKeyUpEventData),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_members = (PyMemberDef[]){
        {"key", Py_T_UINT, offsetof(PyKeyUpEventData, key), 0, NULL},
        {"scan_code", Py_T_UBYTE, offsetof(PyKeyUpEventData, scanCode), 0, NULL},
        {0},
    },
};

PyTypeObject PyKeyDownEventData_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.window.KeyDownEventData",
    .tp_basicsize = sizeof(PyKeyDownEventData),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_members = (PyMemberDef[]){
        {"key", Py_T_UINT, offsetof(PyKeyDownEventData, key), 0, NULL},
        {"repeat_count", Py_T_USHORT, offsetof(PyKeyDownEventData, repeatCount), 0, NULL},
        {"scan_code", Py_T_UBYTE, offsetof(PyKeyDownEventData, scanCode), 0, NULL},
        {"was_pressed", Py_T_BOOL, offsetof(PyKeyDownEventData, wasPressed), 0, NULL},
        {0},
    },
};

PyTypeObject PyScrollEventData_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.window.ScrollEventData",
    .tp_basicsize = sizeof(PyScrollEventData),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_getset = (PyGetSetDef[]){
        {"position", (getter)PyScrollEventData_GetPosition, NULL, NULL, NULL},
        {0},
    },
    .tp_members = (PyMemberDef[]){
        {"x", Py_T_USHORT, offsetof(PyScrollEventData, x), 0, NULL},
        {"y", Py_T_USHORT, offsetof(PyScrollEventData, y), 0, NULL},
        {"delta", Py_T_SHORT, offsetof(PyScrollEventData, delta), 0, NULL},
        {"modifiers", Py_T_USHORT, offsetof(PyScrollEventData, modifiers), 0, NULL},
        {0},
    },
};

PyTypeObject PyShowEventData_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.window.ShowEventData",
    .tp_basicsize = sizeof(PyShowEventData),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_members = (PyMemberDef[]){
        {"is_visible", Py_T_BOOL, offsetof(PyShowEventData, isVisible), 0, NULL},
        {0},
    },
};

PyTypeObject PyMouseMoveEventData_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.window.MouseMoveEventData",
    .tp_basicsize = sizeof(PyMouseMoveEventData),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_getset = (PyGetSetDef[]){
        {"position", (getter)PyMouseMoveEventData_GetPosition, NULL, NULL, NULL},
        {0},
    },
    .tp_members = (PyMemberDef[]){
        {"x", Py_T_USHORT, offsetof(PyMouseMoveEventData, x), 0, NULL},
        {"y", Py_T_USHORT, offsetof(PyMouseMoveEventData, y), 0, NULL},
        {"modifiers", Py_T_USHORT, offsetof(PyMouseMoveEventData, modifiers), 0, NULL},
        {0},
    },
};

PyTypeObject PyCloseEventData_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.window.CloseEventData",
    .tp_basicsize = sizeof(PyCloseEventData),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_members = (PyMemberDef[]){
        {"time", Py_T_DOUBLE, offsetof(PyCloseEventData, time), 0, NULL},
        {0},
    },
};

PyTypeObject PyMoveEventData_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.window.MoveEventData",
    .tp_basicsize = sizeof(PyMoveEventData),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_getset = (PyGetSetDef[]){
        {"position", (getter)PyMoveEventData_GetPosition, NULL, NULL, NULL},
        {0},
    },
    .tp_members = (PyMemberDef[]){
        {"x", Py_T_USHORT, offsetof(PyMoveEventData, x), 0, NULL},
        {"y", Py_T_USHORT, offsetof(PyMoveEventData, y), 0, NULL},
        {0},
    },
};
