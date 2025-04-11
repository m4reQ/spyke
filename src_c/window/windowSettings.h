#pragma once
#include "../utils.h"
#include <stdbool.h>
#include <Python.h>

typedef enum
{
    WND_FLAGS_DEFAULT = 0,
    WND_FLAGS_RESIZABLE = 1 << 0,
    WND_FLAGS_FULLSCREEN = 1 << 1,
    WND_FLAGS_BORDERLESS = 1 << 2,
    WND_FLAGS_TRANSPARENT_FRAMEBUFFER = 1 << 3,
    WND_FLAGS_CURSOR_HIDDEN = 1 << 4,
    WND_FLAGS_ENABLE_VSYNC = 1 << 5,
    WND_FLAGS_ALLOW_FILE_DROP = 1 << 6,
    WND_FLAGS_REQUIRE_DEPTH_STENCIL = 1 << 7,
} WindowFlags;

typedef struct
{
    PY_OBJECT_HEAD;
    uint32_t width;
    uint32_t height;
    PyObject *pyTitle;
    WindowFlags flags;
    bool useDebugContext;
} PyWindowSettings;

extern PyTypeObject PyWindowSettings_Type;

inline const char *PyWindowSettings_GetTitle(PyWindowSettings *settings)
{
    return PyUnicode_AsUTF8(settings->pyTitle);
}
