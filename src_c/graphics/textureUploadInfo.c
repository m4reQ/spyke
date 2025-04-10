#include "texture.h"

static int PyTextureUploadInfo_init(PyTextureUploadInfo *self, PyObject *args, PyObject *kwargs)
{
    static char *kwNames[] = {
        "format",
        "width",
        "height",
        /* optional */
        "depth",
        "x_offset",
        "y_offset",
        "z_offset",
        "level",
        "pixel_type",
        "image_size",
        "data_offset",
        "generate_mipmap",
        NULL,
    };

    self->depth = 1;
    self->pixelType = GL_UNSIGNED_BYTE;
    self->generateMipmap = true;

    if (!PyArg_ParseTupleAndKeywords(
            args, kwargs, "Iii|iiiiiIinp", kwNames,
            &self->format,
            &self->width, &self->height, &self->depth,
            &self->xOffset, &self->yOffset, &self->zOffset,
            &self->level,
            &self->pixelType,
            &self->imageSize, &self->dataOffset,
            &self->generateMipmap))
        return -1;

    return 0;
}

static PyObject *PyTextureUploadInfo_is_compressed_getter(PyTextureUploadInfo *self, void *closure)
{
    (void)closure;

    return PyBool_FromLong(self->imageSize > 0);
}

PyTypeObject PyTextureUploadInfo_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_name = "spyke.graphics.gl.TextureUploadInfo",
    .tp_basicsize = sizeof(PyTextureUploadInfo),
    .tp_init = (initproc)PyTextureUploadInfo_init,
    .tp_members = (PyMemberDef[]){
        {"width", Py_T_INT, offsetof(PyTextureUploadInfo, width), 0, NULL},
        {"height", Py_T_INT, offsetof(PyTextureUploadInfo, height), 0, NULL},
        {"depth", Py_T_INT, offsetof(PyTextureUploadInfo, depth), 0, NULL},
        {"x_offset", Py_T_INT, offsetof(PyTextureUploadInfo, xOffset), 0, NULL},
        {"y_offset", Py_T_INT, offsetof(PyTextureUploadInfo, yOffset), 0, NULL},
        {"z_offset", Py_T_INT, offsetof(PyTextureUploadInfo, zOffset), 0, NULL},
        {"level", Py_T_INT, offsetof(PyTextureUploadInfo, level), 0, NULL},
        {"format", Py_T_UINT, offsetof(PyTextureUploadInfo, format), 0, NULL},
        {"pixel_type", Py_T_UINT, offsetof(PyTextureUploadInfo, pixelType), 0, NULL},
        {"image_size", Py_T_INT, offsetof(PyTextureUploadInfo, imageSize), 0, NULL},
        {"data_offset", Py_T_PYSSIZET, offsetof(PyTextureUploadInfo, dataOffset), 0, NULL},
        {"generate_mipmap", Py_T_BOOL, offsetof(PyTextureUploadInfo, generateMipmap), 0, NULL},
        {0},
    },
    .tp_getset = (PyGetSetDef[]){
        {"is_compressed", (getter)PyTextureUploadInfo_is_compressed_getter, NULL, NULL, NULL},
        {0},
    },
};
