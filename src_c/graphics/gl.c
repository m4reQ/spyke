#include "buffer.h"
#include "sync.h"
#include "texture.h"
#include "vertexArray.h"
#include "shader.h"
#include "framebuffer.h"
#include "../enum.h"
#include "../utils.h"

static PyObject *s_Logger;
static PyObject *s_PyDebugCallback;

static GLenum GetGLObjectType(PyObject *object)
{
    if (PyObject_IsInstance(object, (PyObject *)&PySync_Type))
        return 0;
    if (PyObject_IsInstance(object, (PyObject *)&PyTexture_Type))
        return GL_TEXTURE;
    if (PyObject_IsInstance(object, (PyObject *)&PyBuffer_Type))
        return GL_BUFFER;
    if (PyObject_IsInstance(object, (PyObject *)&PyFramebuffer_Type))
        return GL_FRAMEBUFFER;
    if (PyObject_IsInstance(object, (PyObject *)&PyVertexArray_Type))
        return GL_VERTEX_ARRAY;
    if (PyObject_IsInstance(object, (PyObject *)&PyShaderProgram_Type))
        return GL_PROGRAM;

    return (GLenum)-1;
}

static void DebugMessageCallbackThunk(GLenum source, GLenum type, GLuint id, GLenum severity, GLsizei length, const GLchar *message, const void *userParam)
{
    (void)length;
    (void)userParam;

    if (s_PyDebugCallback != NULL)
    {
        PyObject *result = PyObject_CallFunction(s_PyDebugCallback, "IIIIs", source, type, severity, id, message);
        if (result == NULL)
        {
            fprintf(stderr, "An error ocurred during execution of OpenGL debug callback. Further program execution might be unstable.\n");
            PyErr_Print();
            PyErr_Clear();
        }
    }
}

static const char *DebugMessageSourceToString(GLenum source)
{
    switch (source)
    {
    case GL_DEBUG_SOURCE_API:
        return "API";
    case GL_DEBUG_SOURCE_APPLICATION:
        return "APPLICATION";
    case GL_DEBUG_SOURCE_OTHER:
        return "OTHER";
    case GL_DEBUG_SOURCE_SHADER_COMPILER:
        return "SHADER_COMPILER";
    case GL_DEBUG_SOURCE_THIRD_PARTY:
        return "THIRD_PARTY";
    case GL_DEBUG_SOURCE_WINDOW_SYSTEM:
        return "WINDOW_SYSTEM";
    default:
        return "UNKNOWN";
    }
}

static const char *DebugMessageTypeToString(GLenum type)
{
    switch (type)
    {
    case GL_DEBUG_TYPE_DEPRECATED_BEHAVIOR:
        return "DEPRECATED_BEHAVIOR";
    case GL_DEBUG_TYPE_ERROR:
        return "ERROR";
    case GL_DEBUG_TYPE_MARKER:
        return "MARKER";
    case GL_DEBUG_TYPE_OTHER:
        return "OTHER";
    case GL_DEBUG_TYPE_PERFORMANCE:
        return "PERFORMANCE";
    case GL_DEBUG_TYPE_POP_GROUP:
        return "POP_GROUP";
    case GL_DEBUG_TYPE_PORTABILITY:
        return "PORTABILITY";
    case GL_DEBUG_TYPE_PUSH_GROUP:
        return "PUSH_GROUP";
    case GL_DEBUG_TYPE_UNDEFINED_BEHAVIOR:
        return "UNDEFINED_BEHAVIOR";
    default:
        return "UNKNOWN";
    }
}

static const char *DebugMessageSeverityToLogFuncName(GLenum severity)
{
    switch (severity)
    {
    case GL_DEBUG_SEVERITY_NOTIFICATION:
        return "debug";
    case GL_DEBUG_SEVERITY_LOW:
        return "info";
    case GL_DEBUG_SEVERITY_MEDIUM:
        return "warning";
    case GL_DEBUG_SEVERITY_HIGH:
        return "error";
    default:
        return "debug";
    }
}

static void OpenGLDebugCallback(GLenum source, GLenum type, GLuint id, GLenum severity, GLsizei length, const GLchar *message, const void *userParam)
{
    (void)id;
    (void)userParam;

    PyObject *pyMessage = PyUnicode_FromFormat("OpenGL[%s] %s -> %.*s.", DebugMessageSourceToString(source), DebugMessageTypeToString(type), length, message);
    if (pyMessage == NULL)
    {
        PyErr_Clear();
        return;
    }

    if (!PyObject_CallMethod(s_Logger, DebugMessageSeverityToLogFuncName(severity), "N", pyMessage))
        PyErr_Clear();
}

static bool EnableOpenGLDebugOutput()
{
    if (!s_Logger)
    {
        PyObject *loggingModule = PyImport_ImportModule("logging");
        if (!loggingModule)
            return false;

        s_Logger = PyObject_CallMethod(loggingModule, "getLogger", "s", "spyke.graphics.renderer");
        Py_DecRef(loggingModule);

        if (!s_Logger)
            return false;
    }

    glEnable(GL_DEBUG_OUTPUT);
    glEnable(GL_DEBUG_OUTPUT_SYNCHRONOUS);
    glDebugMessageCallback(OpenGLDebugCallback, NULL);

    const char *debugMessage = "OpenGL debug output enabled.";
    glDebugMessageInsert(GL_DEBUG_SOURCE_APPLICATION, GL_DEBUG_TYPE_OTHER, 2137, GL_DEBUG_SEVERITY_NOTIFICATION, (GLsizei)strlen(debugMessage), debugMessage);

    return true;
}

static void PyOpengl_free(PyObject *self)
{
    (void)self;

    if (s_Logger)
    {
        Py_DecRef(s_Logger);
        s_Logger = NULL;
    }
}

static PyObject *PyOpengl_initialize(PyObject *self, PyObject *args)
{
    (void)self;
    (void)args;

    if (!gladLoaderLoadGL())
    {
        PyErr_SetString(PyExc_RuntimeError, "Failed to load OpenGL bindings.");
        return NULL;
    }

    const bool optimizationEnabled = _PyInterpreterState_GetConfig(PyInterpreterState_Get())->parser_debug;
    if (optimizationEnabled && !EnableOpenGLDebugOutput())
        return NULL;

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_draw_arrays(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    GLenum mode;
    GLint first;
    GLsizei count;
    if (!_PyArg_ParseStack(args, nArgs, "Iii", &mode, &first, &count))
        return NULL;

    glDrawArrays(mode, first, count);

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_draw_arrays_instanced(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    GLenum mode;
    GLint first;
    GLsizei count, instanceCount;
    if (!_PyArg_ParseStack(args, nArgs, "Iiii", &mode, &first, &count, &instanceCount))
        return NULL;

    glDrawArraysInstanced(mode, first, count, instanceCount);

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_draw_arrays_instanced_base_instance(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    GLenum mode;
    GLint first;
    GLsizei count, instanceCount;
    GLuint baseInstance;
    if (!_PyArg_ParseStack(args, nArgs, "IiiiI", &mode, &first, &count, &instanceCount, &baseInstance))
        return NULL;

    glDrawArraysInstancedBaseInstance(mode, first, count, instanceCount, baseInstance);

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_draw_elements(PyObject *self, PyObject *args, PyObject *kwargs)
{
    (void)self;

    static char *kwNames[] = {"mode", "count", "type", "offset", NULL};
    GLenum mode, type;
    GLsizei count;
    void *offset = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "IiI|n", kwNames, &mode, &count, &type, &offset))
        return NULL;

    glDrawElements(mode, count, type, offset);

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_draw_elements_base_vertex(PyObject *self, PyObject *args, PyObject *kwargs)
{
    (void)self;

    static char *kwNames[] = {"mode", "count", "type", "base_vertex", "offset", NULL};
    GLenum mode, type;
    GLsizei count;
    GLint baseVertex;
    void *offset = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "IiIi|n", kwNames, &mode, &count, &type, &baseVertex, &offset))
        return NULL;

    glDrawElementsBaseVertex(mode, count, type, offset, baseVertex);

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_draw_elements_instanced(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    GLenum mode, type;
    GLsizei count, instanceCount;
    if (!_PyArg_ParseStack(args, nArgs, "IiIi", &mode, &count, &type, &instanceCount))
        return NULL;

    glDrawElementsInstanced(mode, count, type, NULL, instanceCount);

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_draw_elements_instanced_base_instance(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    GLenum mode, type;
    GLsizei count, instanceCount;
    GLuint baseInstance;
    if (!_PyArg_ParseStack(args, nArgs, "IiIiI", &mode, &count, &type, &instanceCount, &baseInstance))
        return NULL;

    glDrawElementsInstancedBaseInstance(mode, count, type, NULL, instanceCount, baseInstance);

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_draw_elements_instanced_base_vertex(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    GLenum mode, type;
    GLsizei count, instanceCount;
    GLint baseVertex;
    if (!_PyArg_ParseStack(args, nArgs, "IiIii", &mode, &count, &type, &instanceCount, &baseVertex))
        return NULL;

    glDrawElementsInstancedBaseVertex(mode, count, type, NULL, instanceCount, baseVertex);

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_draw_elements_instanced_base_vertex_base_instance(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    GLenum mode, type;
    GLsizei count, instanceCount;
    GLint baseVertex;
    GLuint baseInstance;
    if (!_PyArg_ParseStack(args, nArgs, "IiIiiI", &mode, &count, &type, &instanceCount, &baseVertex, &baseInstance))
        return NULL;

    glDrawElementsInstancedBaseVertexBaseInstance(mode, count, type, NULL, instanceCount, baseVertex, baseInstance);

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_draw_arrays_indirect(PyObject *self, PyObject *mode)
{
    (void)self;

    CHECK_ARG_INT(mode, NULL);
    glDrawArraysIndirect(PyLong_AsUnsignedLong(mode), NULL);

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_draw_elements_indirect(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    GLenum mode, type;
    if (!_PyArg_ParseStack(args, nArgs, "II", &mode, &type))
        NULL;

    glDrawElementsIndirect(mode, type, NULL);

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_multi_draw_arrays_indirect(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    GLenum mode;
    GLsizei drawCount, stride;
    if (!_PyArg_ParseStack(args, nArgs, "Iii", &mode, &drawCount, &stride))
        NULL;

    glMultiDrawArraysIndirect(mode, NULL, drawCount, stride);

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_multi_draw_elements_indirect(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    GLenum mode, type;
    GLsizei drawCount, stride;
    if (!_PyArg_ParseStack(args, nArgs, "IIii", &mode, &type, &drawCount, &stride))
        NULL;

    glMultiDrawElementsIndirect(mode, type, NULL, drawCount, stride);

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_clear(PyObject *self, PyObject *clearMask)
{
    (void)self;

    CHECK_ARG_INT(clearMask, NULL);
    glClear(PyLong_AsUnsignedLong(clearMask));

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_memory_barrier(PyObject *self, PyObject *barrier)
{
    (void)self;
    CHECK_ARG_INT(barrier, NULL);
    glMemoryBarrier(PyLong_AsUnsignedLong(barrier));
    Py_RETURN_NONE;
}

static PyObject *PyOpengl_memory_barrier_by_region(PyObject *self, PyObject *barrier)
{
    (void)self;
    CHECK_ARG_INT(barrier, NULL);
    glMemoryBarrierByRegion(PyLong_AsUnsignedLong(barrier));
    Py_RETURN_NONE;
}

static PyObject *PyOpengl_flush(PyObject *self, PyObject *args)
{
    (void)self;
    (void)args;
    glFlush();
    Py_RETURN_NONE;
}

static PyObject *PyOpengl_finish(PyObject *self, PyObject *args)
{
    (void)self;
    (void)args;
    glFinish();
    Py_RETURN_NONE;
}

static PyObject *PyOpengl_bind_textures(PyObject *self, PyObject *args, PyObject *kwargs)
{
    (void)self;

    static char *kwNames[] = {"textures", "first", NULL};
    GLuint first = 0;
    PyObject *textures = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O!|I", kwNames, &PyList_Type, &textures, &first))
        return NULL;

    Py_ssize_t nTextures = PyList_GET_SIZE(textures);
    if (nTextures == 0)
        Py_RETURN_NONE;

    if (nTextures > 32)
    {
        PyErr_SetString(PyExc_RuntimeError, "Cannot bind more than 32 textures at once. Use separate bind_textures calls.");
        return NULL;
    }

    GLuint textureIds[32];
    for (Py_ssize_t i = 0; i < nTextures; i++)
    {
        PyTexture *tex = (PyTexture *)PyList_GET_ITEM(textures, i);
        textureIds[i] = tex->id;
    }

    glBindTextures(first, (GLsizei)nTextures, textureIds);

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_bind_texture_id(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    GLuint textureId;
    GLuint unit;
    if (!_PyArg_ParseStack(args, nArgs, "II", &textureId, &unit))
        return NULL;

    glBindTextureUnit(unit, textureId);

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_bind_texture_ids(PyObject *self, PyObject *args, PyObject *kwargs)
{
    (void)self;

    static char *kwNames[] = {"textures", "first", NULL};
    GLuint first = 0;
    PyObject *textures = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O!|I", kwNames, &PyList_Type, &textures, &first))
        return NULL;

    Py_ssize_t nTextures = PyList_GET_SIZE(textures);
    if (nTextures == 0)
        Py_RETURN_NONE;

    if (nTextures > 32)
    {
        PyErr_SetString(PyExc_RuntimeError, "Cannot bind more than 32 textures at once. Use separate bind_textures calls.");
        return NULL;
    }

    GLuint textureIds[32];
    for (Py_ssize_t i = 0; i < nTextures; i++)
    {
        PyObject *texId = PyList_GET_ITEM(textures, i);
        textureIds[i] = PyLong_AsUnsignedLong(texId);
    }

    glBindTextures(first, (GLsizei)nTextures, textureIds);

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_set_pixel_pack_alignment(PyObject *self, PyObject *alignment)
{
    (void)self;
    CHECK_ARG_INT(alignment, NULL);
    glPixelStorei(GL_PACK_ALIGNMENT, PyLong_AsLong(alignment));
    Py_RETURN_NONE;
}

static PyObject *PyOpengl_set_pixel_unpack_alignment(PyObject *self, PyObject *alignment)
{
    (void)self;
    CHECK_ARG_INT(alignment, NULL);
    glPixelStorei(GL_UNPACK_ALIGNMENT, PyLong_AsLong(alignment));
    Py_RETURN_NONE;
}

static PyObject *PyOpengl_enable(PyObject *self, PyObject *enableCap)
{
    (void)self;
    CHECK_ARG_INT(enableCap, NULL);
    glEnable(PyLong_AsUnsignedLong(enableCap));
    Py_RETURN_NONE;
}

static PyObject *PyOpengl_disable(PyObject *self, PyObject *enableCap)
{
    (void)self;
    CHECK_ARG_INT(enableCap, NULL);
    glDisable(PyLong_AsUnsignedLong(enableCap));
    Py_RETURN_NONE;
}

static PyObject *PyOpengl_blend_func(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    GLenum src, dst;
    if (!_PyArg_ParseStack(args, nArgs, "II", &src, &dst))
        return NULL;

    glBlendFunc(src, dst);
    Py_RETURN_NONE;
}

static PyObject *PyOpengl_blend_func_separate(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    GLenum srcRgb, dstRgb, srcAlpha, dstAlpha;
    if (!_PyArg_ParseStack(args, nArgs, "IIII", &srcRgb, &dstRgb, &srcAlpha, &dstAlpha))
        return NULL;

    glBlendFuncSeparate(srcRgb, dstRgb, srcAlpha, dstAlpha);
    Py_RETURN_NONE;
}

static PyObject *PyOpengl_blend_equation(PyObject *self, PyObject *equation)
{
    (void)self;

    CHECK_ARG_INT(equation, NULL);
    glBlendEquation(PyLong_AsUnsignedLong(equation));
    Py_RETURN_NONE;
}

static PyObject *PyOpengl_clear_color(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    GLfloat color[4];

    if (nArgs == 1)
    {
        Py_buffer buffer = {0};
        if (PyObject_GetBuffer(args[0], &buffer, PyBUF_READ) == -1)
            return NULL;

        if (PyBuffer_ToContiguous(color, &buffer, sizeof(color), 'C') == -1)
            return NULL;
    }
    else if (!_PyArg_ParseStack(args, nArgs, "ffff", &color[0], &color[1], &color[2], &color[3]))
        return NULL;

    glClearColor(color[0], color[1], color[2], color[3]);

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_scissor(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    GLint x, y;
    GLsizei width, height;
    if (!_PyArg_ParseStack(args, nArgs, "iiii", &x, &y, &width, &height))
        return NULL;

    glScissor(x, y, width, height);
    Py_RETURN_NONE;
}

static PyObject *PyOpengl_viewport(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    GLint x, y;
    GLsizei width, height;
    if (!_PyArg_ParseStack(args, nArgs, "iiii", &x, &y, &width, &height))
        return NULL;

    glViewport(x, y, width, height);
    Py_RETURN_NONE;
}

static PyObject *PyOpengl_polygon_mode(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    GLenum cullFace, mode;
    if (!_PyArg_ParseStack(args, nArgs, "II", &cullFace, &mode))
        return NULL;

    glPolygonMode(cullFace, mode);
    Py_RETURN_NONE;
}

static PyObject *PyOpengl_debug_message_callback(PyObject *self, PyObject *callback)
{
    (void)self;

    if (!PyCallable_Check(callback))
    {
        PyErr_Format(PyExc_TypeError, "Expected argument to be a callable, got: %s.", Py_TYPE(callback)->tp_name);
        return NULL;
    }

    Py_XDECREF(s_PyDebugCallback);
    s_PyDebugCallback = Py_NewRef(callback);

    glDebugMessageCallback(DebugMessageCallbackThunk, NULL);

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_debug_message_insert(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    GLenum source, type, severity;
    GLuint id;
    const char *message;
    if (!_PyArg_ParseStack(args, nArgs, "IIIIs", &source, &type, &severity, &id, &message))
        return NULL;

    glDebugMessageInsert(source, type, id, severity, (GLsizei)strlen(message), message);

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_set_object_name(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    PyObject *object;
    const char *name;
    if (!_PyArg_ParseStack(args, nArgs, "Os", &object, &name))
        return NULL;

    GLenum glObjectType = GetGLObjectType(object);
    if (glObjectType == -1)
    {
        PyErr_Format(PyExc_TypeError, "Expected argument to be an OpenGL object, got: %s.", Py_TYPE(object)->tp_name);
        return NULL;
    }

    if (glObjectType == 0)
    {
        glObjectPtrLabel(((PySync *)object)->sync, -1, name);
    }
    else
    {
        GLuint id = *(GLuint *)((uint8_t *)object + sizeof(PyObject));
        glObjectLabel(glObjectType, id, -1, name);
    }

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_depth_mask(PyObject *self, PyObject *value)
{
    (void)self;
    glDepthMask((GLboolean)PyObject_IsTrue(value));
    Py_RETURN_NONE;
}

static PyObject *PyOpengl_cull_face(PyObject *self, PyObject *face)
{
    (void)self;
    CHECK_ARG_INT(face, NULL);

    glCullFace(PyLong_AsUnsignedLong(face));

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_front_face(PyObject *self, PyObject *face)
{
    (void)self;
    CHECK_ARG_INT(face, NULL);

    glFrontFace(PyLong_AsUnsignedLong(face));

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_color_mask(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    int r, g, b, a;
    if (!_PyArg_ParseStack(args, nArgs, "pppp", &r, &g, &b, &a))
        return NULL;

    glColorMask((GLboolean)r, (GLboolean)g, (GLboolean)b, (GLboolean)a);

    Py_RETURN_NONE;
}

static PyObject *PyOpengl_get_internal_format(PyObject *self, PyObject *const *args, Py_ssize_t nArgs)
{
    (void)self;

    GLenum internalFormat;
    GLenum textureTarget;
    GLint param;
    if (!_PyArg_ParseStack(args, nArgs, "III", &internalFormat, &textureTarget, &param))
        return NULL;

    glGetInternalformativ(textureTarget, internalFormat, param, sizeof(param), &param);
    return PyLong_FromLong(param);
}

static PyModuleDef s_ModuleDef = {
    PyModuleDef_HEAD_INIT,
    .m_name = "spyke.graphics.gl",
    .m_size = -1,
    .m_free = PyOpengl_free,
    .m_methods = (PyMethodDef[]){
        {"initialize", (PyCFunction)PyOpengl_initialize, METH_NOARGS, NULL},
        {"draw_arrays", (PyCFunction)PyOpengl_draw_arrays, METH_FASTCALL, NULL},
        {"draw_arrays_instanced", (PyCFunction)PyOpengl_draw_arrays_instanced, METH_FASTCALL, NULL},
        {"draw_arrays_instanced_base_instance", (PyCFunction)PyOpengl_draw_arrays_instanced_base_instance, METH_FASTCALL, NULL},
        {"draw_elements", (PyCFunction)PyOpengl_draw_elements, METH_VARARGS | METH_KEYWORDS, NULL},
        {"draw_elements_base_vertex", (PyCFunction)PyOpengl_draw_elements_base_vertex, METH_VARARGS | METH_KEYWORDS, NULL},
        {"draw_elements_instanced", (PyCFunction)PyOpengl_draw_elements_instanced, METH_FASTCALL, NULL},
        {"draw_elements_instanced_base_instance", (PyCFunction)PyOpengl_draw_elements_instanced_base_instance, METH_FASTCALL, NULL},
        {"draw_elements_instanced_base_vertex", (PyCFunction)PyOpengl_draw_elements_instanced_base_vertex, METH_FASTCALL, NULL},
        {"draw_elements_instanced_base_vertex_base_instance", (PyCFunction)PyOpengl_draw_elements_instanced_base_vertex_base_instance, METH_FASTCALL, NULL},
        {"draw_arrays_indirect", (PyCFunction)PyOpengl_draw_arrays_indirect, METH_O, NULL},
        {"draw_elements_indirect", (PyCFunction)PyOpengl_draw_elements_indirect, METH_FASTCALL, NULL},
        {"multi_draw_arrays_indirect", (PyCFunction)PyOpengl_multi_draw_arrays_indirect, METH_FASTCALL, NULL},
        {"multi_draw_elements_indirect", (PyCFunction)PyOpengl_multi_draw_elements_indirect, METH_FASTCALL, NULL},
        {"clear", (PyCFunction)PyOpengl_clear, METH_O, NULL},
        {"memory_barrier", (PyCFunction)PyOpengl_memory_barrier, METH_O, NULL},
        {"memory_barrier_by_region", (PyCFunction)PyOpengl_memory_barrier_by_region, METH_O, NULL},
        {"flush", (PyCFunction)PyOpengl_flush, METH_NOARGS, NULL},
        {"finish", (PyCFunction)PyOpengl_finish, METH_NOARGS, NULL},
        {"bind_textures", (PyCFunction)PyOpengl_bind_textures, METH_VARARGS | METH_KEYWORDS, NULL},
        {"bind_texture_id", (PyCFunction)PyOpengl_bind_texture_id, METH_FASTCALL, NULL},
        {"bind_texture_ids", (PyCFunction)PyOpengl_bind_texture_ids, METH_VARARGS | METH_KEYWORDS, NULL},
        {"set_pixel_pack_alignment", (PyCFunction)PyOpengl_set_pixel_pack_alignment, METH_O, NULL},
        {"set_pixel_unpack_alignment", (PyCFunction)PyOpengl_set_pixel_unpack_alignment, METH_O, NULL},
        {"enable", (PyCFunction)PyOpengl_enable, METH_O, NULL},
        {"disable", (PyCFunction)PyOpengl_disable, METH_O, NULL},
        {"blend_equation", (PyCFunction)PyOpengl_blend_equation, METH_O, NULL},
        {"blend_func", (PyCFunction)PyOpengl_blend_func, METH_FASTCALL, NULL},
        {"blend_func_separate", (PyCFunction)PyOpengl_blend_func_separate, METH_FASTCALL, NULL},
        {"clear_color", (PyCFunction)PyOpengl_clear_color, METH_FASTCALL, NULL},
        {"scissor", (PyCFunction)PyOpengl_scissor, METH_FASTCALL, NULL},
        {"viewport", (PyCFunction)PyOpengl_viewport, METH_FASTCALL, NULL},
        {"polygon_mode", (PyCFunction)PyOpengl_polygon_mode, METH_FASTCALL, NULL},
        {"debug_message_callback", (PyCFunction)PyOpengl_debug_message_callback, METH_O, NULL},
        {"debug_message_insert", (PyCFunction)PyOpengl_debug_message_insert, METH_FASTCALL, NULL},
        {"set_object_name", (PyCFunction)PyOpengl_set_object_name, METH_FASTCALL, NULL},
        {"depth_mask", (PyCFunction)PyOpengl_depth_mask, METH_O, NULL},
        {"cull_face", (PyCFunction)PyOpengl_cull_face, METH_O, NULL},
        {"front_face", (PyCFunction)PyOpengl_front_face, METH_O, NULL},
        {"color_mask", (PyCFunction)PyOpengl_color_mask, METH_FASTCALL, NULL},
        {"get_internal_format", (PyCFunction)PyOpengl_get_internal_format, METH_FASTCALL, NULL},
        {0},
    },
};

#pragma region Enums
static EnumValue s_TextureFormatParameterEnumValues[] = {
    {"INTERNALFORMAT_RED_SIZE", GL_INTERNALFORMAT_RED_SIZE},
    {"INTERNALFORMAT_GREEN_SIZE", GL_INTERNALFORMAT_GREEN_SIZE},
    {"INTERNALFORMAT_BLUE_SIZE", GL_INTERNALFORMAT_BLUE_SIZE},
    {"INTERNALFORMAT_ALPHA_SIZE", GL_INTERNALFORMAT_ALPHA_SIZE},
    {"INTERNALFORMAT_DEPTH_SIZE", GL_INTERNALFORMAT_DEPTH_SIZE},
    {"INTERNALFORMAT_STENCIL_SIZE", GL_INTERNALFORMAT_STENCIL_SIZE},
    {"INTERNALFORMAT_SHARED_SIZE", GL_INTERNALFORMAT_SHARED_SIZE},
    {0},
};

static EnumValue s_FrontFaceEnumValues[] = {
    {"CW", GL_CW},
    {"CCW", GL_CCW},
    {0},
};
static EnumValue s_DebugTypeEnumValues[] = {
    {"DEPRECATED_BEHAVIOR", GL_DEBUG_TYPE_DEPRECATED_BEHAVIOR},
    {"ERROR", GL_DEBUG_TYPE_ERROR},
    {"MARKER", GL_DEBUG_TYPE_MARKER},
    {"OTHER", GL_DEBUG_TYPE_OTHER},
    {"PERFORMANCE", GL_DEBUG_TYPE_PERFORMANCE},
    {"POP_GROUP", GL_DEBUG_TYPE_POP_GROUP},
    {"PORTABILITY", GL_DEBUG_TYPE_PORTABILITY},
    {"PUSH_GROUP", GL_DEBUG_TYPE_PUSH_GROUP},
    {"UNDEFINED_BEHAVIOR", GL_DEBUG_TYPE_UNDEFINED_BEHAVIOR},
    {0},
};

static EnumValue s_DebugSourceEnumValues[] = {
    {"API", GL_DEBUG_SOURCE_API},
    {"APPLICATION", GL_DEBUG_SOURCE_APPLICATION},
    {"OTHER", GL_DEBUG_SOURCE_OTHER},
    {"SHADER_COMPILER", GL_DEBUG_SOURCE_SHADER_COMPILER},
    {"THIRD_PARTY", GL_DEBUG_SOURCE_THIRD_PARTY},
    {"WINDOW_SYSTEM", GL_DEBUG_SOURCE_WINDOW_SYSTEM},
    {0},
};

static EnumValue s_DebugSeverityEnumValues[] = {
    {"HIGH", GL_DEBUG_SEVERITY_HIGH},
    {"LOW", GL_DEBUG_SEVERITY_LOW},
    {"MEDIUM", GL_DEBUG_SEVERITY_MEDIUM},
    {"NOTIFICATION", GL_DEBUG_SEVERITY_NOTIFICATION},
    {0},
};

static EnumValue s_PolygonModeEnumValues[] = {
    {"FILL", GL_FILL},
    {"POINT", GL_POINT},
    {"LINE", GL_LINE},
    {0},
};

static EnumValue s_CullFaceEnumValues[] = {
    {"FRONT", GL_FRONT},
    {"BACK", GL_BACK},
    {"FRONT_AND_BACK", GL_FRONT_AND_BACK},
    {0},
};

static EnumValue s_BlendEquationEnumValues[] = {
    {"FUNC_ADD", GL_FUNC_ADD},
    {"FUNC_SUBTRACT", GL_FUNC_SUBTRACT},
    {"FUNC_REVERSE_SUBTRACT", GL_FUNC_REVERSE_SUBTRACT},
    {"MIN", GL_MIN},
    {"MAX", GL_MAX},
    {0},
};

static EnumValue s_BlendFactorEnumValues[] = {
    {"ZERO", GL_ZERO},
    {"ONE", GL_ONE},
    {"SRC_COLOR", GL_SRC_COLOR},
    {"ONE_MINUS_SRC_COLOR", GL_ONE_MINUS_SRC_COLOR},
    {"DST_COLOR", GL_DST_COLOR},
    {"ONE_MINUS_DST_COLOR", GL_ONE_MINUS_DST_COLOR},
    {"SRC_ALPHA", GL_SRC_ALPHA},
    {"ONE_MINUS_SRC_ALPHA", GL_ONE_MINUS_SRC_ALPHA},
    {"DST_ALPHA", GL_DST_ALPHA},
    {"ONE_MINUS_DST_ALPHA", GL_ONE_MINUS_DST_ALPHA},
    {"CONSTANT_COLOR", GL_CONSTANT_COLOR},
    {"ONE_MINUS_CONSTANT_COLOR", GL_ONE_MINUS_CONSTANT_COLOR},
    {"CONSTANT_ALPHA", GL_CONSTANT_ALPHA},
    {"ONE_MINUS_CONSTANT_ALPHA", GL_ONE_MINUS_CONSTANT_ALPHA},
    {0},
};

static EnumValue s_EnableCapEnumValues[] = {
    {"BLEND", GL_BLEND},
    {"CLIP_DISTANCE0", GL_CLIP_DISTANCE0},
    {"CLIP_DISTANCE1", GL_CLIP_DISTANCE1},
    {"CLIP_DISTANCE2", GL_CLIP_DISTANCE2},
    {"CLIP_DISTANCE3", GL_CLIP_DISTANCE3},
    {"CLIP_DISTANCE4", GL_CLIP_DISTANCE4},
    {"CLIP_DISTANCE5", GL_CLIP_DISTANCE5},
    {"CLIP_DISTANCE6", GL_CLIP_DISTANCE6},
    {"CLIP_DISTANCE7", GL_CLIP_DISTANCE7},
    {"COLOR_LOGIC_OP", GL_COLOR_LOGIC_OP},
    {"CULL_FACE", GL_CULL_FACE},
    {"DEBUG_OUTPUT", GL_DEBUG_OUTPUT},
    {"DEBUG_OUTPUT_SYNCHRONOUS", GL_DEBUG_OUTPUT_SYNCHRONOUS},
    {"DEPTH_CLAMP", GL_DEPTH_CLAMP},
    {"DEPTH_TEST", GL_DEPTH_TEST},
    {"DITHER", GL_DITHER},
    {"FRAMEBUFFER_SRGB", GL_FRAMEBUFFER_SRGB},
    {"LINE_SMOOTH", GL_LINE_SMOOTH},
    {"MULTISAMPLE", GL_MULTISAMPLE},
    {"POLYGON_OFFSET_FILL", GL_POLYGON_OFFSET_FILL},
    {"POLYGON_OFFSET_LINE", GL_POLYGON_OFFSET_LINE},
    {"POLYGON_OFFSET_POINT", GL_POLYGON_OFFSET_POINT},
    {"POLYGON_SMOOTH", GL_POLYGON_SMOOTH},
    {"PRIMITIVE_RESTART", GL_PRIMITIVE_RESTART},
    {"PRIMITIVE_RESTART_FIXED_INDEX", GL_PRIMITIVE_RESTART_FIXED_INDEX},
    {"RASTERIZER_DISCARD", GL_RASTERIZER_DISCARD},
    {"SAMPLE_ALPHA_TO_COVERAGE", GL_SAMPLE_ALPHA_TO_COVERAGE},
    {"SAMPLE_ALPHA_TO_ONE", GL_SAMPLE_ALPHA_TO_ONE},
    {"SAMPLE_COVERAGE", GL_SAMPLE_COVERAGE},
    {"SAMPLE_SHADING", GL_SAMPLE_SHADING},
    {"SAMPLE_MASK", GL_SAMPLE_MASK},
    {"SCISSOR_TEST", GL_SCISSOR_TEST},
    {"STENCIL_TEST", GL_STENCIL_TEST},
    {"TEXTURE_CUBE_MAP_SEAMLESS", GL_TEXTURE_CUBE_MAP_SEAMLESS},
    {"PROGRAM_POINT_SIZE", GL_PROGRAM_POINT_SIZE},
    {0},
};

static EnumValue s_GLTypeEnumValues[] = {
    {"BYTE", GL_BYTE},
    {"UNSIGNED_BYTE", GL_UNSIGNED_BYTE},
    {"SHORT", GL_SHORT},
    {"UNSIGNED_SHORT", GL_UNSIGNED_SHORT},
    {"INT", GL_INT},
    {"UNSIGNED_INT", GL_UNSIGNED_INT},
    {"FIXED", GL_FIXED},
    {"HALF_FLOAT", GL_HALF_FLOAT},
    {"FLOAT", GL_FLOAT},
    {"DOUBLE", GL_DOUBLE},
    {0},
};

static EnumValue s_BufferTargetEnumValues[] = {
    {"ARRAY_BUFFER", GL_ARRAY_BUFFER},
    {"ATOMIC_COUNTER_BUFFER", GL_ATOMIC_COUNTER_BUFFER},
    {"COPY_READ_BUFFER", GL_COPY_READ_BUFFER},
    {"COPY_WRITE_BUFFER", GL_COPY_WRITE_BUFFER},
    {"DISPATCH_INDIRECT_BUFFER", GL_DISPATCH_INDIRECT_BUFFER},
    {"DRAW_INDIRECT_BUFFER", GL_DRAW_INDIRECT_BUFFER},
    {"ELEMENT_ARRAY_BUFFER", GL_ELEMENT_ARRAY_BUFFER},
    {"PIXEL_PACK_BUFFER", GL_PIXEL_PACK_BUFFER},
    {"PIXEL_UNPACK_BUFFER", GL_PIXEL_UNPACK_BUFFER},
    {"QUERY_BUFFER", GL_QUERY_BUFFER},
    {"SHADER_STORAGE_BUFFER", GL_SHADER_STORAGE_BUFFER},
    {"TEXTURE_BUFFER", GL_TEXTURE_BUFFER},
    {"TRANSFORM_FEEDBACK_BUFFER", GL_TRANSFORM_FEEDBACK_BUFFER},
    {"UNIFORM_BUFFER", GL_UNIFORM_BUFFER},
    {0},
};

static EnumValue s_BufferBaseTargetEnumValues[] = {
    {"ATOMIC_COUNTER_BUFFER", GL_ATOMIC_COUNTER_BUFFER},
    {"TRANSFORM_FEEDBACK_BUFFER", GL_TRANSFORM_FEEDBACK_BUFFER},
    {"UNIFORM_BUFFER", GL_UNIFORM_BUFFER},
    {"SHADER_STORAGE_BUFFER", GL_SHADER_STORAGE_BUFFER},
    {0},
};

static EnumValue s_BufferFlagEnumValues[] = {
    {"DYNAMIC_STORAGE_BIT", GL_DYNAMIC_STORAGE_BIT},
    {"MAP_READ_BIT", GL_MAP_READ_BIT},
    {"MAP_WRITE_BIT", GL_MAP_WRITE_BIT},
    {"MAP_PERSISTENT_BIT", GL_MAP_PERSISTENT_BIT},
    {"MAP_COHERENT_BIT", GL_MAP_COHERENT_BIT},
    {"CLIENT_STORAGE_BIT", GL_CLIENT_STORAGE_BIT},
    {"NONE", 0},
    {0},
};

static EnumValue s_MagFilterEnumValues[] = {
    {"NEAREST", GL_NEAREST},
    {"LINEAR", GL_LINEAR},
    {0},
};

static EnumValue s_MinFilterEnumValues[] = {
    {"NEAREST", GL_NEAREST},
    {"LINEAR", GL_LINEAR},
    {"NEAREST_MIPMAP_NEAREST", GL_NEAREST_MIPMAP_NEAREST},
    {"LINEAR_MIPMAP_NEAREST", GL_LINEAR_MIPMAP_NEAREST},
    {"NEAREST_MIPMAP_LINEAR", GL_NEAREST_MIPMAP_LINEAR},
    {"LINEAR_MIPMAP_LINEAR", GL_LINEAR_MIPMAP_LINEAR},
    {0},
};

static EnumValue s_TextureParameterEnumValues[] = {
    {"DEPTH_STENCIL_TEXTURE_MODE", GL_DEPTH_STENCIL_TEXTURE_MODE},
    {"TEXTURE_BASE_LEVEL", GL_TEXTURE_BASE_LEVEL},
    {"TEXTURE_BORDER_COLOR", GL_TEXTURE_BORDER_COLOR},
    {"TEXTURE_COMPARE_FUNC", GL_TEXTURE_COMPARE_FUNC},
    {"TEXTURE_COMPARE_MODE", GL_TEXTURE_COMPARE_MODE},
    {"TEXTURE_LOD_BIAS", GL_TEXTURE_LOD_BIAS},
    {"TEXTURE_MIN_FILTER", GL_TEXTURE_MIN_FILTER},
    {"TEXTURE_MAG_FILTER", GL_TEXTURE_MAG_FILTER},
    {"TEXTURE_MIN_LOD", GL_TEXTURE_MIN_LOD},
    {"TEXTURE_MAX_LOD", GL_TEXTURE_MAX_LOD},
    {"TEXTURE_MAX_LEVEL", GL_TEXTURE_MAX_LEVEL},
    {"TEXTURE_SWIZZLE_R", GL_TEXTURE_SWIZZLE_R},
    {"TEXTURE_SWIZZLE_G", GL_TEXTURE_SWIZZLE_G},
    {"TEXTURE_SWIZZLE_B", GL_TEXTURE_SWIZZLE_B},
    {"TEXTURE_SWIZZLE_A", GL_TEXTURE_SWIZZLE_A},
    {"TEXTURE_SWIZZLE_RGBA", GL_TEXTURE_SWIZZLE_RGBA},
    {"TEXTURE_WRAP_S", GL_TEXTURE_WRAP_S},
    {"TEXTURE_WRAP_T", GL_TEXTURE_WRAP_T},
    {"TEXTURE_WRAP_R", GL_TEXTURE_WRAP_R},
    {0},
};

static EnumValue s_WrapModeEnumValues[] = {
    {"CLAMP_TO_EDGE", GL_CLAMP_TO_EDGE},
    {"CLAMP_TO_BORDER", GL_CLAMP_TO_BORDER},
    {"MIRROR_CLAMP_TO_EDGE", GL_MIRROR_CLAMP_TO_EDGE},
    {"REPEAT", GL_REPEAT},
    {"MIRRORED_REPEAT", GL_MIRRORED_REPEAT},
    {0},
};

static EnumValue s_InternalFormatEnumValues[] = {
    {"R8", GL_R8},
    {"R8_SNORM", GL_R8_SNORM},
    {"R16", GL_R16},
    {"R16_SNORM", GL_R16_SNORM},
    {"RG8", GL_RG8},
    {"RG8_SNORM", GL_RG8_SNORM},
    {"RG16", GL_RG16},
    {"RG16_SNORM", GL_RG16_SNORM},
    {"R3_G3_B2", GL_R3_G3_B2},
    {"RGB4", GL_RGB4},
    {"RGB5", GL_RGB5},
    {"RGB8", GL_RGB8},
    {"RGB8_SNORM", GL_RGB8_SNORM},
    {"RGB10", GL_RGB10},
    {"RGB12", GL_RGB12},
    {"RGB16", GL_RGB16},
    {"RGB16_SNORM", GL_RGB16_SNORM},
    {"RGBA2", GL_RGBA2},
    {"RGBA4", GL_RGBA4},
    {"RGB5_A1", GL_RGB5_A1},
    {"RGBA8", GL_RGBA8},
    {"RGBA8_SNORM", GL_RGBA8_SNORM},
    {"RGB10_A2", GL_RGB10_A2},
    {"RGB10_A2UI", GL_RGB10_A2UI},
    {"RGBA12", GL_RGBA12},
    {"RGBA16", GL_RGBA16},
    {"SRGB8", GL_SRGB8},
    {"SRGB8_ALPHA8", GL_SRGB8_ALPHA8},
    {"R16F", GL_R16F},
    {"RG16F", GL_RG16F},
    {"RGB16F", GL_RGB16F},
    {"RGBA16F", GL_RGBA16F},
    {"R32F", GL_R32F},
    {"RG32F", GL_RG32F},
    {"RGB32F", GL_RGB32F},
    {"RGBA32F", GL_RGBA32F},
    {"R11F_G11F_B10F", GL_R11F_G11F_B10F},
    {"RGB9_E5", GL_RGB9_E5},
    {"R8I", GL_R8I},
    {"R8UI", GL_R8UI},
    {"R16I", GL_R16I},
    {"R16UI", GL_R16UI},
    {"R32I", GL_R32I},
    {"R32UI", GL_R32UI},
    {"RG8I", GL_RG8I},
    {"RG8UI", GL_RG8UI},
    {"RG16I", GL_RG16I},
    {"RG16UI", GL_RG16UI},
    {"RG32I", GL_RG32I},
    {"RG32UI", GL_RG32UI},
    {"RGB8I", GL_RGB8I},
    {"RGB8UI", GL_RGB8UI},
    {"RGB16I", GL_RGB16I},
    {"RGB16UI", GL_RGB16UI},
    {"RGB32I", GL_RGB32I},
    {"RGB32UI", GL_RGB32UI},
    {"RGBA8I", GL_RGBA8I},
    {"RGBA8UI", GL_RGBA8UI},
    {"RGBA16I", GL_RGBA16I},
    {"RGBA16UI", GL_RGBA16UI},
    {"RGBA32I", GL_RGBA32I},
    {"RGBA32UI", GL_RGBA32UI},
    {0},
};

static EnumValue s_PixelFormatEnumValues[] = {
    {"RED", GL_RED},
    {"RG", GL_RG},
    {"RGB", GL_RGB},
    {"BGR", GL_BGR},
    {"RGBA", GL_RGBA},
    {"BGRA", GL_BGRA},
    {"DEPTH_COMPONENT", GL_DEPTH_COMPONENT},
    {"STENCIL_INDEX", GL_STENCIL_INDEX},
    {0},
};

static EnumValue s_PixelTypeEnumValues[] = {
    {"UNSIGNED_BYTE", GL_UNSIGNED_BYTE},
    {"BYTE", GL_BYTE},
    {"UNSIGNED_SHORT", GL_UNSIGNED_SHORT},
    {"SHORT", GL_SHORT},
    {"UNSIGNED_INT", GL_UNSIGNED_INT},
    {"INT", GL_INT},
    {"FLOAT", GL_FLOAT},
    {"UNSIGNED_BYTE_3_3_2", GL_UNSIGNED_BYTE_3_3_2},
    {"UNSIGNED_BYTE_2_3_3_REV", GL_UNSIGNED_BYTE_2_3_3_REV},
    {"UNSIGNED_SHORT_5_6_5", GL_UNSIGNED_SHORT_5_6_5},
    {"UNSIGNED_SHORT_5_6_5_REV", GL_UNSIGNED_SHORT_5_6_5_REV},
    {"UNSIGNED_SHORT_4_4_4_4", GL_UNSIGNED_SHORT_4_4_4_4},
    {"UNSIGNED_SHORT_4_4_4_4_REV", GL_UNSIGNED_SHORT_4_4_4_4_REV},
    {"UNSIGNED_SHORT_5_5_5_1", GL_UNSIGNED_SHORT_5_5_5_1},
    {"UNSIGNED_SHORT_1_5_5_5_REV", GL_UNSIGNED_SHORT_1_5_5_5_REV},
    {"UNSIGNED_INT_8_8_8_8", GL_UNSIGNED_INT_8_8_8_8},
    {"UNSIGNED_INT_8_8_8_8_REV", GL_UNSIGNED_INT_8_8_8_8_REV},
    {"UNSIGNED_INT_10_10_10_2", GL_UNSIGNED_INT_10_10_10_2},
    {"UNSIGNED_INT_2_10_10_10_REV", GL_UNSIGNED_INT_2_10_10_10_REV},
    {0},
};

static EnumValue s_CompressedInternalFormatEnumValues[] = {
    {"COMPRESSED_RGB_S3TC_DXT1_EXT", GL_COMPRESSED_RGB_S3TC_DXT1_EXT},
    {"COMPRESSED_RGBA_S3TC_DXT1_EXT", GL_COMPRESSED_RGBA_S3TC_DXT1_EXT},
    {"COMPRESSED_RGBA_S3TC_DXT3_EXT", GL_COMPRESSED_RGBA_S3TC_DXT3_EXT},
    {"COMPRESSED_RGBA_S3TC_DXT5_EXT", GL_COMPRESSED_RGBA_S3TC_DXT5_EXT},
    {0},
};

static EnumValue s_TextureTargetEnumValues[] = {
    {"TEXTURE_1D", GL_TEXTURE_1D},
    {"TEXTURE_2D", GL_TEXTURE_2D},
    {"TEXTURE_3D", GL_TEXTURE_3D},
    {"TEXTURE_1D_ARRAY", GL_TEXTURE_1D_ARRAY},
    {"TEXTURE_2D_ARRAY", GL_TEXTURE_2D_ARRAY},
    {"TEXTURE_RECTANGLE", GL_TEXTURE_RECTANGLE},
    {"TEXTURE_CUBE_MAP", GL_TEXTURE_CUBE_MAP},
    {"TEXTURE_CUBE_MAP_ARRAY", GL_TEXTURE_CUBE_MAP_ARRAY},
    {"TEXTURE_BUFFER", GL_TEXTURE_BUFFER},
    {"TEXTURE_2D_MULTISAMPLE", GL_TEXTURE_2D_MULTISAMPLE},
    {"TEXTURE_2D_MULTISAMPLE_ARRAY", GL_TEXTURE_2D_MULTISAMPLE_ARRAY},
    {0},
};

static EnumValue s_VertexAttribTypeEnumValues[] = {
    {"FLOAT", GL_FLOAT},
    {"HALF_FLOAT", GL_HALF_FLOAT},
    {"DOUBLE", GL_DOUBLE},
    {"BYTE", GL_BYTE},
    {"UNSIGNED_BYTE", GL_UNSIGNED_BYTE},
    {"SHORT", GL_SHORT},
    {"UNSIGNED_SHORT", GL_UNSIGNED_SHORT},
    {"INT", GL_INT},
    {"UNSIGNED_INT", GL_UNSIGNED_INT},
    {0},
};

static EnumValue s_UniformTypeEnumValues[] = {
    {"FLOAT", GL_FLOAT},
    {"DOUBLE", GL_DOUBLE},
    {"INT", GL_INT},
    {"UNSIGNED_INT", GL_UNSIGNED_INT},
    {0},
};

static EnumValue s_ShaderTypeEnumValues[] = {
    {"FRAGMENT_SHADER", GL_FRAGMENT_SHADER},
    {"VERTEX_SHADER", GL_VERTEX_SHADER},
    {"GEOMETRY_SHADER", GL_GEOMETRY_SHADER},
    {"COMPUTE_SHADER", GL_COMPUTE_SHADER},
    {"TESS_CONTROL_SHADER", GL_TESS_CONTROL_SHADER},
    {"TESS_EVALUATION_SHADER", GL_TESS_EVALUATION_SHADER},
    {0},
};

static EnumValue s_ShaderBinaryFormatEnumValues[] = {
    {"SHADER_BINARY_FORMAT_SPIR_V", GL_SHADER_BINARY_FORMAT_SPIR_V},
    {0},
};

static EnumValue s_FramebufferAttachmentFormatEnumValues[] = {
    {"RGBA8", GL_RGBA8},
    {"RGB8", GL_RGB8},
    {"RG8", GL_RG8},
    {"R8", GL_R8},
    {"RGBA16", GL_RGBA16},
    {"RGB16", GL_RGB16},
    {"RG16", GL_RG16},
    {"R16", GL_R16},
    {"RGBA16F", GL_RGBA16F},
    {"RGB16F", GL_RGB16F},
    {"RG16F", GL_RG16F},
    {"R16F", GL_R16F},
    {"RGBA32F", GL_RGBA32F},
    {"RGB32F", GL_RGB32F},
    {"RG32F", GL_RG32F},
    {"R32F", GL_R32F},
    {"RGBA8I", GL_RGBA8I},
    {"RGB8I", GL_RGB8I},
    {"RG8I", GL_RG8I},
    {"R8I", GL_R8I},
    {"RGBA16I", GL_RGBA16I},
    {"RGB16I", GL_RGB16I},
    {"RG16I", GL_RG16I},
    {"R16I", GL_R16I},
    {"RGBA32I", GL_RGBA32I},
    {"RGB32I", GL_RGB32I},
    {"RG32I", GL_RG32I},
    {"R32I", GL_R32I},
    {"RGBA8UI", GL_RGBA8UI},
    {"RGB8UI", GL_RGB8UI},
    {"RG8UI", GL_RG8UI},
    {"R8UI", GL_R8UI},
    {"RGBA16UI", GL_RGBA16UI},
    {"RGB16UI", GL_RGB16UI},
    {"RG16UI", GL_RG16UI},
    {"R16UI", GL_R16UI},
    {"RGBA32UI", GL_RGBA32UI},
    {"RGB32UI", GL_RGB32UI},
    {"RG32UI", GL_RG32UI},
    {"R32UI", GL_R32UI},
    {"RGBA4", GL_RGBA4},
    {"RGB5_A1", GL_RGB5_A1},
    {"RGB565", GL_RGB565},
    {"RGB10_A2", GL_RGB10_A2},
    {"RGB10_A2UI", GL_RGB10_A2UI},
    {"R11F_G11F_B10F", GL_R11F_G11F_B10F},
    {"SRGB8_ALPHA8", GL_SRGB8_ALPHA8},
    {"DEPTH_COMPONENT16", GL_DEPTH_COMPONENT16},
    {"DEPTH_COMPONENT24", GL_DEPTH_COMPONENT24},
    {"DEPTH_COMPONENT32F", GL_DEPTH_COMPONENT32F},
    {"DEPTH24_STENCIL8", GL_DEPTH24_STENCIL8},
    {"DEPTH32F_STENCIL8", GL_DEPTH32F_STENCIL8},
    {"STENCIL_INDEX8", GL_STENCIL_INDEX8},
    {0},
};

static EnumValue s_FramebufferAttachmentPointEnumValues[] = {
    {"DEPTH_ATTACHMENT", GL_DEPTH_ATTACHMENT},
    {"STENCIL_ATTACHMENT", GL_STENCIL_ATTACHMENT},
    {"DEPTH_STENCIL_ATTACHMENT", GL_DEPTH_STENCIL_ATTACHMENT},
    {0},
};

static EnumValue s_DrawModeEnumValues[] = {
    {"POINTS", GL_POINTS},
    {"LINE_STRIP", GL_LINE_STRIP},
    {"LINE_LOOP", GL_LINE_LOOP},
    {"LINES", GL_LINES},
    {"LINE_STRIP_ADJACENCY", GL_LINE_STRIP_ADJACENCY},
    {"LINES_ADJACENCY", GL_LINES_ADJACENCY},
    {"TRIANGLE_STRIP", GL_TRIANGLE_STRIP},
    {"TRIANGLE_FAN", GL_TRIANGLE_FAN},
    {"TRIANGLES", GL_TRIANGLES},
    {"TRIANGLE_STRIP_ADJACENCY", GL_TRIANGLE_STRIP_ADJACENCY},
    {"TRIANGLES_ADJACENCY", GL_TRIANGLES_ADJACENCY},
    {"PATCHES", GL_PATCHES},
    {0},
};

static EnumValue s_ElementsTypeEnumValues[] = {
    {"UNSIGNED_BYTE", GL_UNSIGNED_BYTE},
    {"UNSIGNED_SHORT", GL_UNSIGNED_SHORT},
    {"UNSIGNED_INT", GL_UNSIGNED_INT},
    {0},
};

static EnumValue s_ClearMaskEnumValues[] = {
    {"COLOR_BUFFER_BIT", GL_COLOR_BUFFER_BIT},
    {"DEPTH_BUFFER_BIT", GL_DEPTH_BUFFER_BIT},
    {"STENCIL_BUFFER_BIT", GL_STENCIL_BUFFER_BIT},
    {0},
};

static EnumValue s_BarrierEnumValues[] = {
    {"VERTEX_ATTRIB_ARRAY_BARRIER_BIT", GL_VERTEX_ATTRIB_ARRAY_BARRIER_BIT},
    {"ELEMENT_ARRAY_BARRIER_BIT", GL_ELEMENT_ARRAY_BARRIER_BIT},
    {"UNIFORM_BARRIER_BIT", GL_UNIFORM_BARRIER_BIT},
    {"TEXTURE_FETCH_BARRIER_BIT", GL_TEXTURE_FETCH_BARRIER_BIT},
    {"SHADER_IMAGE_ACCESS_BARRIER_BIT", GL_SHADER_IMAGE_ACCESS_BARRIER_BIT},
    {"COMMAND_BARRIER_BIT", GL_COMMAND_BARRIER_BIT},
    {"PIXEL_BUFFER_BARRIER_BIT", GL_PIXEL_BUFFER_BARRIER_BIT},
    {"TEXTURE_UPDATE_BARRIER_BIT", GL_TEXTURE_UPDATE_BARRIER_BIT},
    {"BUFFER_UPDATE_BARRIER_BIT", GL_BUFFER_UPDATE_BARRIER_BIT},
    {"CLIENT_MAPPED_BUFFER_BARRIER_BIT", GL_CLIENT_MAPPED_BUFFER_BARRIER_BIT},
    {"FRAMEBUFFER_BARRIER_BIT", GL_FRAMEBUFFER_BARRIER_BIT},
    {"TRANSFORM_FEEDBACK_BARRIER_BIT", GL_TRANSFORM_FEEDBACK_BARRIER_BIT},
    {"ATOMIC_COUNTER_BARRIER_BIT", GL_ATOMIC_COUNTER_BARRIER_BIT},
    {"SHADER_STORAGE_BARRIER_BIT", GL_SHADER_STORAGE_BARRIER_BIT},
    {"QUERY_BUFFER_BARRIER_BIT", GL_QUERY_BUFFER_BARRIER_BIT},
    {"ALL_BARRIER_BITS", GL_ALL_BARRIER_BITS},
    {0},
};
#pragma endregion

PyMODINIT_FUNC PyInit_gl()
{
    PyObject *module = PyModule_Create(&s_ModuleDef);
    if (!module)
        return NULL;

    ADD_TYPE_OR_FAIL(module, PyBuffer_Type);
    ADD_TYPE_OR_FAIL(module, PySync_Type);
    ADD_TYPE_OR_FAIL(module, PyTextureSpec_Type);
    ADD_TYPE_OR_FAIL(module, PyTextureUploadInfo_Type);
    ADD_TYPE_OR_FAIL(module, PyTexture_Type);
    ADD_TYPE_OR_FAIL(module, PyVertexDescriptor_Type);
    ADD_TYPE_OR_FAIL(module, PyVertexInput_Type);
    ADD_TYPE_OR_FAIL(module, PyVertexArray_Type);
    ADD_TYPE_OR_FAIL(module, PyShaderSpecializeInfo_Type);
    ADD_TYPE_OR_FAIL(module, PyShaderStageInfo_Type);
    ADD_TYPE_OR_FAIL(module, PyShaderProgram_Type);
    ADD_TYPE_OR_FAIL(module, PyFramebufferAttachment_Type);
    ADD_TYPE_OR_FAIL(module, PyFramebuffer_Type);

    ADD_ENUM_OR_FAIL(module, "GLType", s_GLTypeEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "BufferTarget", s_BufferTargetEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "BufferBaseTarget", s_BufferBaseTargetEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "BufferFlag", s_BufferFlagEnumValues, true);
    ADD_ENUM_OR_FAIL(module, "MagFilter", s_MagFilterEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "MinFilter", s_MinFilterEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "MinFilter", s_MinFilterEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "TextureTarget", s_TextureTargetEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "CompressedInternalFormat", s_CompressedInternalFormatEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "PixelType", s_PixelTypeEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "PixelFormat", s_PixelFormatEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "InternalFormat", s_InternalFormatEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "WrapMode", s_WrapModeEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "TextureParameter", s_TextureParameterEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "VertexAttribType", s_VertexAttribTypeEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "UniformType", s_UniformTypeEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "ShaderType", s_ShaderTypeEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "ShaderBinaryFormat", s_ShaderBinaryFormatEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "FramebufferAttachmentFormat", s_FramebufferAttachmentFormatEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "FramebufferAttachmentPoint", s_FramebufferAttachmentPointEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "DrawMode", s_DrawModeEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "ElementsType", s_ElementsTypeEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "ClearMask", s_ClearMaskEnumValues, true);
    ADD_ENUM_OR_FAIL(module, "Barrier", s_BarrierEnumValues, true);
    ADD_ENUM_OR_FAIL(module, "EnableCap", s_EnableCapEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "BlendEquation", s_BlendEquationEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "BlendFactor", s_BlendFactorEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "PolygonMode", s_PolygonModeEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "CullFace", s_CullFaceEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "DebugSource", s_DebugSourceEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "DebugType", s_DebugTypeEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "DebugSeverity", s_DebugSeverityEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "FrontFace", s_FrontFaceEnumValues, false);
    ADD_ENUM_OR_FAIL(module, "TextureFormatParameter", s_TextureFormatParameterEnumValues, false);

    return module;
}
