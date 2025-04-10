#include "texture.h"
#include "buffer.h"

static bool Create1DTextureStorage(const PyTexture *texture, const PyTextureSpec *spec)
{
    if (texture->width <= 0)
    {
        PyErr_SetString(PyExc_ValueError, "Texture width must be positive for 1D texture.");
        return false;
    }

    glTextureStorage1D(texture->id, spec->mipmaps, spec->internalFormat, texture->width);
    return true;
}

static bool Create2DTextureStorage(const PyTexture *texture, const PyTextureSpec *spec)
{
    if (texture->width <= 0 || texture->height <= 0)
    {
        PyErr_SetString(PyExc_ValueError, "Texture width and height must be positive for 2D texture or 1D texture array.");
        return false;
    }

    if (texture->target == GL_TEXTURE_2D_MULTISAMPLE)
        glTextureStorage2DMultisample(
            texture->id,
            spec->samples,
            spec->internalFormat,
            texture->width,
            texture->height,
            GL_TRUE);
    else
        glTextureStorage2D(
            texture->id,
            texture->mipmaps,
            spec->internalFormat,
            texture->width,
            texture->height);

    return true;
}

static bool Create3DTextureStorage(const PyTexture *texture, const PyTextureSpec *spec)
{
    if (texture->width <= 0 || texture->height <= 0 || texture->depth <= 0)
    {
        PyErr_SetString(PyExc_ValueError, "Texture width, height and depth must be positive for 3D texture, 2D array texture or cubemap texture.");
        return false;
    }

    if (texture->target == GL_TEXTURE_2D_MULTISAMPLE_ARRAY)
        glTextureStorage3DMultisample(
            texture->id,
            spec->samples,
            spec->internalFormat,
            texture->width,
            texture->height,
            texture->depth,
            GL_TRUE);
    else
        glTextureStorage3D(
            texture->id,
            texture->mipmaps,
            spec->internalFormat,
            texture->width,
            texture->height,
            texture->depth);

    return true;
}

static bool CheckTextureImmutableFormat(GLuint textureID)
{
    GLint immutableFormat = GL_FALSE;
    glGetTextureParameteriv(textureID, GL_TEXTURE_IMMUTABLE_FORMAT, &immutableFormat);
    if (!immutableFormat)
    {
        PyErr_SetString(PyExc_RuntimeError, "Couldn't create immutable texture storage.");
        return false;
    }

    return true;
}

static bool UploadTexture1D(PyTexture *texture, const PyTextureUploadInfo *info, const void *dataPtr)
{
    if (info->width <= 0 || info->xOffset < 0)
    {
        PyErr_SetString(PyExc_ValueError, "1D texture upload requires width to be greater than 0 and x_offset to be non-negative.");
        return false;
    }

    if (info->imageSize != 0)
        glCompressedTextureSubImage1D(
            texture->id,
            info->level,
            info->xOffset,
            info->width,
            info->format,
            info->imageSize,
            dataPtr);
    else
        glTextureSubImage1D(
            texture->id,
            info->level,
            info->xOffset,
            info->width,
            info->format,
            info->pixelType,
            dataPtr);

    return true;
}

static bool UploadTexture2D(PyTexture *texture, const PyTextureUploadInfo *info, const void *dataPtr)
{
    if (info->width <= 0 ||
        info->height <= 0 ||
        info->xOffset < 0 ||
        info->yOffset < 0)
    {
        PyErr_SetString(PyExc_ValueError, "2D texture upload requires width and height to be greater than 0 and x_offset, y_offset to be non-negative.");
        return false;
    }

    if (info->imageSize != 0)
        glCompressedTextureSubImage2D(
            texture->id,
            info->level,
            info->xOffset,
            info->yOffset,
            info->width,
            info->height,
            info->format,
            info->imageSize,
            dataPtr);
    else
        glTextureSubImage2D(
            texture->id,
            info->level,
            info->xOffset,
            info->yOffset,
            info->width,
            info->height,
            info->format,
            info->pixelType,
            dataPtr);

    return true;
}

static bool UploadTexture3D(PyTexture *texture, const PyTextureUploadInfo *info, const void *dataPtr)
{
    if (info->width <= 0 ||
        info->height <= 0 ||
        info->depth <= 0 ||
        info->xOffset < 0 ||
        info->yOffset < 0 ||
        info->zOffset < 0)
    {
        PyErr_SetString(PyExc_ValueError, "3D texture upload requires width, height and depth to be greater than 0 and x_offset, y_offset, z_offset to be non-negative.");
        return false;
    }

    if (info->imageSize != 0)
        glCompressedTextureSubImage3D(
            texture->id,
            info->level,
            info->xOffset,
            info->yOffset,
            info->zOffset,
            info->width,
            info->height,
            info->depth,
            info->format,
            info->imageSize,
            dataPtr);
    else
        glTextureSubImage3D(
            texture->id,
            info->level,
            info->xOffset,
            info->yOffset,
            info->zOffset,
            info->width,
            info->height,
            info->depth,
            info->format,
            info->pixelType,
            dataPtr);

    return true;
}

static bool Requires2DUpload(GLenum textureTarget)
{
    return textureTarget == GL_TEXTURE_1D_ARRAY ||
           textureTarget == GL_TEXTURE_2D ||
           textureTarget == GL_TEXTURE_2D_MULTISAMPLE;
}

static bool Requires3DUpload(GLenum textureTarget)
{
    return textureTarget == GL_TEXTURE_3D ||
           textureTarget == GL_TEXTURE_2D_ARRAY ||
           textureTarget == GL_TEXTURE_2D_MULTISAMPLE_ARRAY ||
           textureTarget == GL_TEXTURE_CUBE_MAP;
}

static const char *TextureTargetToString(GLenum target)
{
    switch (target)
    {
    case GL_TEXTURE_1D:
        return "TEXTURE_1D";
    case GL_TEXTURE_2D:
        return "TEXTURE_2D";
    case GL_TEXTURE_3D:
        return "TEXTURE_3D";
    case GL_TEXTURE_1D_ARRAY:
        return "TEXTURE_1D_ARRAY";
    case GL_TEXTURE_2D_ARRAY:
        return "TEXTURE_2D_ARRAY";
    case GL_TEXTURE_RECTANGLE:
        return "TEXTURE_RECTANGLE";
    case GL_TEXTURE_CUBE_MAP:
        return "TEXTURE_CUBE_MAP";
    case GL_TEXTURE_CUBE_MAP_ARRAY:
        return "TEXTURE_CUBE_MAP_ARRAY";
    case GL_TEXTURE_BUFFER:
        return "TEXTURE_BUFFER";
    case GL_TEXTURE_2D_MULTISAMPLE:
        return "TEXTURE_2D_MULTISAMPLE";
    case GL_TEXTURE_2D_MULTISAMPLE_ARRAY:
        return "TEXTURE_2D_MULTISAMPLE_ARRAY";
    default:
        return "UNKNOWN";
    }
}

static Py_ssize_t PixelTypeToSize(GLenum pixelType)
{
    switch (pixelType)
    {
    case GL_BYTE:
    case GL_UNSIGNED_BYTE:
    case GL_UNSIGNED_BYTE_3_3_2:
    case GL_UNSIGNED_BYTE_2_3_3_REV:
        return sizeof(GLbyte);
    case GL_SHORT:
    case GL_UNSIGNED_SHORT:
    case GL_UNSIGNED_SHORT_5_6_5:
    case GL_UNSIGNED_SHORT_5_6_5_REV:
    case GL_UNSIGNED_SHORT_4_4_4_4:
    case GL_UNSIGNED_SHORT_4_4_4_4_REV:
    case GL_UNSIGNED_SHORT_5_5_5_1:
    case GL_UNSIGNED_SHORT_1_5_5_5_REV:
        return sizeof(GLshort);
    case GL_INT:
    case GL_UNSIGNED_INT:
    case GL_UNSIGNED_INT_8_8_8_8:
    case GL_UNSIGNED_INT_8_8_8_8_REV:
    case GL_UNSIGNED_INT_10_10_10_2:
    case GL_UNSIGNED_INT_2_10_10_10_REV:
        return sizeof(GLint);
    case GL_FLOAT:
        return sizeof(GLfloat);
    default:
        return 0;
    }
}

static bool CheckDataBufferLength(const PyTextureUploadInfo *uploadInfo, const Py_buffer *buffer)
{
    if (buffer == NULL)
        return true;

    Py_ssize_t lengthBytes = (uploadInfo->imageSize > 0)
                                 ? uploadInfo->imageSize
                                 : uploadInfo->width * uploadInfo->height * uploadInfo->depth * PixelTypeToSize(uploadInfo->pixelType);

    if (uploadInfo->dataOffset + lengthBytes > buffer->len)
    {
        PyErr_Format(
            PyExc_RuntimeError,
            "Requested transfer data size exceeds provided buffer size (offset: %zu, calculated: %zu, provided: %zu).",
            uploadInfo->dataOffset,
            lengthBytes,
            buffer->len);
        return false;
    }

    return true;
}

static int PyTexture_init(PyTexture *self, PyObject *args, PyObject *kwargs)
{
    static char *kwNames[] = {"spec", "set_parameters", NULL};

    PyTextureSpec *spec;
    bool setParameters = true;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O!|p", kwNames, &PyTextureSpec_Type, &spec, &setParameters))
        return -1;

    self->width = spec->width;
    self->height = spec->height;
    self->depth = self->target == GL_TEXTURE_CUBE_MAP ? 6 : spec->depth;
    self->target = spec->target;
    self->mipmaps = spec->mipmaps;
    self->internalFormat = spec->internalFormat;

    if (self->target == GL_TEXTURE_BUFFER)
    {
        setParameters = false;
        self->mipmaps = 1;
    }
    else
    {
        if (self->mipmaps <= 0)
        {
            PyErr_SetString(PyExc_ValueError, "Mipmaps count for texture must be positive.");
            return -1;
        }
    }

    glCreateTextures(self->target, 1, &self->id);

    bool storageCreateSuccess = false;
    if (self->target == GL_TEXTURE_1D)
        storageCreateSuccess = Create1DTextureStorage(self, spec);
    else if (self->target == GL_TEXTURE_1D_ARRAY ||
             self->target == GL_TEXTURE_2D ||
             self->target == GL_TEXTURE_2D_MULTISAMPLE)
        storageCreateSuccess = Create2DTextureStorage(self, spec);
    else if (self->target == GL_TEXTURE_2D_ARRAY ||
             self->target == GL_TEXTURE_2D_MULTISAMPLE_ARRAY ||
             self->target == GL_TEXTURE_3D ||
             self->target == GL_TEXTURE_CUBE_MAP)
        storageCreateSuccess = Create3DTextureStorage(self, spec);
    else if (self->target == GL_TEXTURE_BUFFER)
        storageCreateSuccess = true;

    if (!storageCreateSuccess || (self->target != GL_TEXTURE_BUFFER && !CheckTextureImmutableFormat(self->id)))
        return -1;

    if (setParameters)
    {
        glTextureParameteri(self->id, GL_TEXTURE_BASE_LEVEL, 0);
        glTextureParameteri(self->id, GL_TEXTURE_MAX_LEVEL, spec->mipmaps - 1);
        glTextureParameteri(self->id, GL_TEXTURE_MIN_FILTER, (GLint)spec->minFilter);
        glTextureParameteri(self->id, GL_TEXTURE_MAG_FILTER, (GLint)spec->magFilter);
        glTextureParameteri(self->id, GL_TEXTURE_WRAP_S, (GLint)spec->wrapMode);
        glTextureParameteri(self->id, GL_TEXTURE_WRAP_R, (GLint)spec->wrapMode);
        glTextureParameteri(self->id, GL_TEXTURE_WRAP_T, (GLint)spec->wrapMode);
    }

    return 0;
}

static PyObject *PyTexture_repr(PyTexture *self)
{
    return PyUnicode_FromFormat(
        "<%s object at %p [target: %s, width: %d, height: %d, depth: %d, mipmaps: %d]>",
        Py_TYPE(self)->tp_name,
        self,
        TextureTargetToString(self->target),
        self->width,
        self->height,
        self->depth,
        self->mipmaps);
}

static PyObject *PyTexture_delete(PyTexture *self, PyObject *args)
{
    (void)args;
    glDeleteTextures(1, &self->id);
    Py_RETURN_NONE;
}

static PyObject *PyTexture_set_debug_name(PyTexture *self, PyObject *name)
{
    CHECK_ARG_STRING(name, NULL);

    Py_ssize_t nameLength = 0;
    const char *nameStr = PyUnicode_AsUTF8AndSize(name, &nameLength);

    glObjectLabel(GL_TEXTURE, self->id, nameLength, nameStr);

    Py_RETURN_NONE;
}

static PyObject *PyTexture_bind(PyTexture *self, PyObject *args)
{
    (void)args;
    glBindTexture(self->target, self->id);
    Py_RETURN_NONE;
}

static PyObject *PyTexture_bind_to_unit(PyTexture *self, PyObject *textureUnit)
{
    CHECK_ARG_INT(textureUnit, NULL);
    glBindTextureUnit(PyLong_AsUnsignedLong(textureUnit), self->id);
    Py_RETURN_NONE;
}

static PyObject *PyTexture_set_parameter(PyTexture *self, PyObject *args)
{
    if (self->target == GL_TEXTURE_BUFFER)
    {
        PyErr_SetString(PyExc_RuntimeError, "Cannot set parameters of texture which is a buffer texture.");
        return NULL;
    }

    GLenum parameterName;
    PyObject *value;
    if (!PyArg_ParseTuple(args, "IO", &parameterName, &value))
        return NULL;

    if (PyLong_Check(value))
        glTextureParameteri(self->id, parameterName, PyLong_AsLong(value));
    else if (PyFloat_Check(value))
        glTextureParameterf(self->id, parameterName, (float)PyFloat_AS_DOUBLE(value));
    else
    {
        PyErr_Format(PyExc_TypeError, "Expected argument 2 to be of type int or float, got: %s.", Py_TYPE(value)->tp_name);
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject *PyTexture_set_texture_buffer(PyTexture *self, PyBuffer *buffer)
{
    if (self->target != GL_TEXTURE_BUFFER)
    {
        PyErr_SetString(PyExc_RuntimeError, "Texture whose target is not GL_TEXTURE_BUFFER cannot be used as buffer texture.");
        return NULL;
    }

    if (!PyObject_IsInstance((PyObject *)buffer, (PyObject *)&PyBuffer_Type))
    {
        PyErr_Format(PyExc_TypeError, "Expected argument to be of type spyke.buffers.gl.Buffer, got: %s.", Py_TYPE(buffer)->tp_name);
        return NULL;
    }

    glTextureBuffer(self->id, self->internalFormat, buffer->id);

    Py_RETURN_NONE;
}

static PyObject *PyTexture_upload(PyTexture *self, PyObject *args)
{
    PyObject *result = NULL;

    if (self->target == GL_TEXTURE_BUFFER)
    {
        PyErr_SetString(PyExc_RuntimeError, "Cannot use `Texture.upload` on a texture with GL_TEXTURE_BUFFER target. To upload data to buffer textures update appropriate buffer contents.");
        return NULL;
    }

    PyTextureUploadInfo *info;
    PyObject *bufferObject = NULL;
    if (!PyArg_ParseTuple(args, "O!O", &PyTextureUploadInfo_Type, &info, &bufferObject))
        return NULL;

    Py_buffer buffer = {0};
    void *dataPtr = NULL;

    if (!Py_IsNone(bufferObject))
    {
        if (PyObject_GetBuffer(bufferObject, &buffer, PyBUF_READ | PyBUF_C_CONTIGUOUS))
        {
            PyErr_Format(PyExc_TypeError, "Expected data to be an object that is a c-contiguous readable buffer or None, got: %s.", Py_TYPE(bufferObject)->tp_name);
            goto end;
        }

        if (!CheckDataBufferLength(info, &buffer))
            goto end;

        dataPtr = (char *)buffer.buf + info->dataOffset;
    }

    bool uploadSuccess = false;
    if (self->target == GL_TEXTURE_1D)
        uploadSuccess = UploadTexture1D(self, info, dataPtr);
    else if (Requires2DUpload(self->target))
        uploadSuccess = UploadTexture2D(self, info, dataPtr);
    else if (Requires3DUpload(self->target))
        uploadSuccess = UploadTexture3D(self, info, dataPtr);
    else
    {
        // TODO Implement support for array cubemap textures
        PyErr_SetString(PyExc_NotImplementedError, "Support for array cubemap textures is not implemented yet.");
        goto end;
    }

    if (!uploadSuccess)
        goto end;

    if (info->generateMipmap)
        glGenerateTextureMipmap(self->id);

    result = Py_NewRef(Py_None);

end:
    if (buffer.buf != NULL)
        PyBuffer_Release(&buffer);

    return result;
}

static PyObject *PyTexture_is_cubemap_getter(PyTexture *self, void *closure)
{
    (void)closure;
    return PyBool_FromLong(self->target == GL_TEXTURE_CUBE_MAP);
}

static PyObject *PyTexture_is_array_getter(PyTexture *self, void *closure)
{
    (void)closure;
    return PyBool_FromLong(
        self->target == GL_TEXTURE_1D_ARRAY ||
        self->target == GL_TEXTURE_2D_ARRAY ||
        self->target == GL_TEXTURE_2D_MULTISAMPLE_ARRAY);
}

static PyObject *PyTexture_is_1d_getter(PyTexture *self, void *closure)
{
    (void)closure;
    return PyBool_FromLong(
        self->target == GL_TEXTURE_1D ||
        self->target == GL_TEXTURE_1D_ARRAY);
}

static PyObject *PyTexture_is_2d_getter(PyTexture *self, void *closure)
{
    (void)closure;
    return PyBool_FromLong(
        self->target == GL_TEXTURE_2D ||
        self->target == GL_TEXTURE_2D_ARRAY ||
        self->target == GL_TEXTURE_2D_MULTISAMPLE ||
        self->target == GL_TEXTURE_2D_MULTISAMPLE_ARRAY);
}

static PyObject *PyTexture_is_3d_getter(PyTexture *self, void *closure)
{
    (void)closure;
    return PyBool_FromLong(self->target == GL_TEXTURE_3D);
}

PyTypeObject PyTexture_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.graphics.gl.Texture",
    .tp_basicsize = sizeof(PyTexture),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)PyTexture_init,
    .tp_repr = (reprfunc)PyTexture_repr,
    .tp_members = (PyMemberDef[]){
        {"id", Py_T_UINT, offsetof(PyTexture, id), Py_READONLY, NULL},
        {"target", Py_T_UINT, offsetof(PyTexture, target), Py_READONLY, NULL},
        {"width", Py_T_INT, offsetof(PyTexture, width), Py_READONLY, NULL},
        {"height", Py_T_INT, offsetof(PyTexture, height), Py_READONLY, NULL},
        {"depth", Py_T_INT, offsetof(PyTexture, depth), Py_READONLY, NULL},
        {"mipmaps", Py_T_INT, offsetof(PyTexture, mipmaps), Py_READONLY, NULL},
        {"internal_format", Py_T_UINT, offsetof(PyTexture, internalFormat), Py_READONLY, NULL},
        {0},
    },
    .tp_methods = (PyMethodDef[]){
        {"delete", (PyCFunction)PyTexture_delete, METH_NOARGS, NULL},
        {"bind", (PyCFunction)PyTexture_bind, METH_NOARGS, NULL},
        {"bind_to_unit", (PyCFunction)PyTexture_bind_to_unit, METH_O, NULL},
        {"set_parameter", (PyCFunction)PyTexture_set_parameter, METH_VARARGS, NULL},
        {"set_texture_buffer", (PyCFunction)PyTexture_set_texture_buffer, METH_O, NULL},
        {"upload", (PyCFunction)PyTexture_upload, METH_VARARGS, NULL},
        {"set_debug_name", (PyCFunction)PyTexture_set_debug_name, METH_O, NULL},
        {0},
    },
    .tp_getset = (PyGetSetDef[]){
        {"is_cubemap", (getter)PyTexture_is_cubemap_getter, NULL, NULL, NULL},
        {"is_array", (getter)PyTexture_is_array_getter, NULL, NULL, NULL},
        {"id_1d", (getter)PyTexture_is_1d_getter, NULL, NULL, NULL},
        {"is_2d", (getter)PyTexture_is_2d_getter, NULL, NULL, NULL},
        {"is_3d", (getter)PyTexture_is_3d_getter, NULL, NULL, NULL},
        {0},
    },
};
