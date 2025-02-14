#pragma once
#include "../utils.h"
#include "../api.h"

#define Math_ImportAPI() (MathAPI *)PyAPI_Import("spyke.math")

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

typedef struct
{
    PyTypeObject *pyViewport2DType;
    PyTypeObject *pyViewport3DType;
} MathAPI;
