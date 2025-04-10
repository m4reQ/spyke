#pragma once
#include <glad/gl.h>
#include <stdbool.h>
#include "../utils.h"

typedef struct
{
    PY_OBJECT_HEAD;
    PyObject *entryPoint;
    PyObject *constants;
} PyShaderSpecializeInfo;

typedef struct
{
    PY_OBJECT_HEAD;
    PyObject *filepathOrSource;
    PyShaderSpecializeInfo *specializeInfo;
    GLenum shaderType;
    GLenum binaryFormat;
    bool useBinary;
    bool useFile;
} PyShaderStageInfo;

typedef struct
{
    PY_OBJECT_HEAD;
    GLuint id;
    PyObject *uniforms;
    PyObject *attributes;
} PyShaderProgram;

extern PyTypeObject PyShaderSpecializeInfo_Type;
extern PyTypeObject PyShaderStageInfo_Type;
extern PyTypeObject PyShaderProgram_Type;
