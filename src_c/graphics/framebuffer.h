#pragma once
#include <stdbool.h>
#include <glad/gl.h>
#include "../utils.h"

typedef struct
{
    PY_OBJECT_HEAD;
    GLsizei width;
    GLsizei height;
    GLsizei samples;
    GLenum format;
    GLenum minFilter;
    GLenum magFilter;
    GLenum attachment;
    bool isRenderbuffer;
    bool isWritable;
} PyFramebufferAttachment;

typedef struct
{
    PyFramebufferAttachment *settings;
    GLuint id;
} Attachment;

typedef struct
{
    PY_OBJECT_HEAD;
    GLuint id;
    Attachment *attachments;
    size_t nAttachments;
    GLsizei width;
    GLsizei height;
} PyFramebuffer;

bool _PyFramebufferAttachment_IsDepthAttachment(PyFramebufferAttachment *attachment);
GLenum _PyFramebufferAttachment_ObjectToAttachmentPoint(PyObject *value);

extern PyTypeObject PyFramebufferAttachment_Type;
extern PyTypeObject PyFramebuffer_Type;
