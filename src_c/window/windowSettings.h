#pragma once
#include "../utils.h"
#include <Python.h>

typedef enum
{
    WND_FLAGS_DEFAULT = 0,
    WND_FLAGS_RESIZABLE = 1,
    WND_FLAGS_FULLSCREEN = 2,
    WND_FLAGS_BORDERLESS = 4,
    WND_FLAGS_TRANSPARENT_FRAMEBUFFER = 8,
    WND_FLAGS_CURSOR_HIDDEN = 16,
    WND_FLAGS_ENABLE_VSYNC = 32,
    WND_FLAGS_ALLOW_FILE_DROP = 64,
} WindowFlags;

typedef struct
{
    PY_OBJECT_HEAD;
    uint32_t width;
    uint32_t height;
    PyObject *pyTitle;
    WindowFlags flags;
} PyWindowSettings;

extern PyTypeObject PyWindowSettings_Type;

inline const char *PyWindowSettings_GetTitle(PyWindowSettings *settings)
{
    return PyUnicode_AsUTF8(settings->pyTitle);
}
