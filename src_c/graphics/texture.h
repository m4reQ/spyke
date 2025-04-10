#pragma once
#include <stdbool.h>
#include <glad/gl.h>
#include "../utils.h"

typedef struct
{
    PY_OBJECT_HEAD;
    GLenum target;
    GLsizei width;
    GLsizei height;
    GLsizei depth;
    GLsizei samples;
    GLsizei mipmaps;
    GLenum internalFormat;
    GLenum minFilter;
    GLenum magFilter;
    GLenum wrapMode;
} PyTextureSpec;

typedef struct
{
    PY_OBJECT_HEAD;
    GLsizei width;
    GLsizei height;
    GLsizei depth;
    GLint xOffset;
    GLint yOffset;
    GLint zOffset;
    GLint level;
    GLenum format;
    GLenum pixelType;
    Py_ssize_t dataOffset;
    GLsizei imageSize;
    bool generateMipmap;
} PyTextureUploadInfo;

typedef struct
{
    PY_OBJECT_HEAD;
    GLuint id;
    GLenum target;
    GLenum internalFormat;
    GLsizei width;
    GLsizei height;
    GLsizei depth;
    GLsizei mipmaps;
} PyTexture;

extern PyTypeObject PyTextureSpec_Type;
extern PyTypeObject PyTextureUploadInfo_Type;
extern PyTypeObject PyTexture_Type;
