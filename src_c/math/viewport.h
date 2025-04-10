#pragma once
#include "../utils.h"

typedef struct
{
    PY_OBJECT_HEAD;
    float left;
    float right;
    float bottom;
    float top;
} PyViewport2D;

typedef struct
{
    PY_OBJECT_HEAD;
    float left;
    float right;
    float bottom;
    float top;
    float near;
    float far;
} PyViewport3D;

extern PyTypeObject PyViewport2D_Type;
extern PyTypeObject PyViewport3D_Type;
