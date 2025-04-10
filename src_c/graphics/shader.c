#include "shader.h"
#include <stdbool.h>

#define READ_FILE_CHUNK_SIZE 1024 * 64 // 64 KiB

static void *ReadWholeFile(FILE *file, size_t *outSize)
{
    // Do not use PyMem_Malloc/Realloc/Free here - GIL not held
    void *buffer = PyMem_RawMalloc(sizeof(uint8_t) * READ_FILE_CHUNK_SIZE);
    size_t bytesRead = 0;
    size_t bufSize = sizeof(uint8_t) * READ_FILE_CHUNK_SIZE;

    while (true)
    {
        if (bytesRead + READ_FILE_CHUNK_SIZE + 1 > bufSize)
        {
            bufSize = bytesRead + READ_FILE_CHUNK_SIZE + 1;
            buffer = PyMem_RawRealloc(buffer, bufSize);
        }

        size_t readCurrent = fread_s((uint8_t *)buffer + bytesRead, bufSize, sizeof(char), bufSize, file);
        bytesRead += readCurrent;

        if (readCurrent < READ_FILE_CHUNK_SIZE)
            break;
    }

    *outSize = bytesRead;
    return buffer;
}

static char *GetShaderSource(PyShaderStageInfo *info, size_t *outSize)
{
    if (info->useFile)
    {
        FILE *file = NULL;
        const char *mode = info->useBinary ? "rb" : "r";
        const char *filepath = PyUnicode_AsUTF8(info->filepathOrSource);

        PyThreadState *tState = PyEval_SaveThread();
        if (fopen_s(&file, filepath, mode))
        {
            PyEval_RestoreThread(tState);
            PyErr_SetFromErrno(PyExc_IOError);
            return NULL;
        }

        void *source = ReadWholeFile(file, outSize);
        fclose(file);
        PyEval_RestoreThread(tState);

        return source;
    }

    if (info->useBinary)
    {
        Py_buffer sourceBuffer = {0};
        if (PyObject_GetBuffer(info->filepathOrSource, &sourceBuffer, PyBUF_READ | PyBUF_C_CONTIGUOUS) == -1)
            return NULL;

        uint8_t *source = PyMem_RawMalloc(sourceBuffer.len); // use raw memory domain for consistency with ReadWholeFile
        PyBuffer_ToContiguous(source, &sourceBuffer, sourceBuffer.len, 'C');
        PyBuffer_Release(&sourceBuffer);

        *outSize = sourceBuffer.len;
        return (char *)source;
    }

    return (char *)PyUnicode_AsUTF8AndSize(info->filepathOrSource, (Py_ssize_t *)outSize);
}

static GLuint CreateStage(PyShaderStageInfo *info)
{
    GLuint stage = glCreateShader(info->shaderType);

    size_t sourceSize = 0;
    void *source = GetShaderSource(info, &sourceSize);
    if (source == NULL)
        return (GLuint)-1;

    if (info->useBinary)
    {
        const Py_ssize_t nSpecializeConstants = PyList_GET_SIZE(info->specializeInfo->constants);
        GLuint *specializeIndices = PyMem_Malloc(sizeof(GLuint) * nSpecializeConstants);
        GLuint *specializeConstants = PyMem_Malloc(sizeof(GLuint) * nSpecializeConstants);

        for (Py_ssize_t i = 0; i < nSpecializeConstants; i++)
        {
            specializeIndices[i] = PyLong_AsUnsignedLong(PyList_GET_ITEM(info->specializeInfo->constants, 0));
            specializeConstants[i] = PyLong_AsUnsignedLong(PyList_GET_ITEM(info->specializeInfo->constants, 1));
        }

        const char *entryPoint = PyUnicode_AsUTF8(info->specializeInfo->entryPoint);
        PyThreadState *tState = PyEval_SaveThread();

        glShaderBinary(1, &stage, info->binaryFormat, source, (GLsizei)sourceSize);
        glSpecializeShaderARB(
            stage,
            entryPoint,
            // TODO Handle overflows where downcasting integer types
            (GLuint)nSpecializeConstants,
            specializeIndices,
            specializeConstants);

        PyEval_RestoreThread(tState);
        PyMem_Free(specializeIndices);
        PyMem_Free(specializeConstants);
    }
    else
    {
        // FIXME If we disable GIL here and any of these 2 GL functions call python log callback we will crash
        // PyThreadState *tState = PyEval_SaveThread();

        glShaderSource(stage, 1, (const char *const *)&source, (GLint *)&sourceSize);
        glCompileShader(stage);

        // PyEval_RestoreThread(tState);
    }

    GLint compileStatus = GL_FALSE;
    glGetShaderiv(stage, GL_COMPILE_STATUS, &compileStatus);
    if (!compileStatus)
    {
        GLint infoLogLength = 0;
        glGetShaderiv(stage, GL_INFO_LOG_LENGTH, &infoLogLength);

        char *infoBuffer = PyMem_Malloc(sizeof(char) * infoLogLength);
        glGetShaderInfoLog(stage, sizeof(char) * infoLogLength, NULL, infoBuffer);

        PyErr_Format(PyExc_RuntimeError, "Failed to compile shader (id: %d, type: %d).\n%.*s", stage, info->shaderType, infoLogLength, infoBuffer);
        return (GLuint)-1;
    }

    if (info->useFile || info->useBinary)
        PyMem_RawFree(source);

    return stage;
}

static bool CheckLinkStatus(GLuint program)
{
    GLint linkStatus = GL_FALSE;
    glGetProgramiv(program, GL_LINK_STATUS, &linkStatus);

    if (!linkStatus)
    {
        GLint logLength = 0;
        glGetProgramiv(program, GL_INFO_LOG_LENGTH, &logLength);

        char *infoLog = PyMem_Malloc(sizeof(char) * logLength);
        glGetProgramInfoLog(program, sizeof(char) * logLength, NULL, infoLog);

        PyErr_Format(PyExc_RuntimeError, "Shader link failure:\n%s", infoLog);

        PyMem_Free(infoLog);
        return false;
    }

    return true;
}

static bool LinkProgram(GLuint program)
{
    Py_BEGIN_ALLOW_THREADS;
    glLinkProgram(program);
    Py_END_ALLOW_THREADS;

    return CheckLinkStatus(program);
}

static void NormalizeArrayName(char *name)
{
    char *bracket = strchr(name, '[');
    if (bracket)
        *bracket = '\0';
}

static PyObject *RetrieveInterface(GLuint program, GLenum interface)
{
    PyObject *result = PyDict_New();

    GLint nResources = 0;
    glGetProgramInterfaceiv(program, interface, GL_ACTIVE_RESOURCES, &nResources);

    for (GLint i = 0; i < nResources; i++)
    {
        GLint properties[2];
        glGetProgramResourceiv(
            program,
            interface,
            (GLuint)i,
            2,
            (const GLenum[]){GL_LOCATION, GL_NAME_LENGTH},
            sizeof(properties),
            NULL,
            properties);

        if (properties[0] == -1)
            continue;

        const GLsizei nameBufSize = sizeof(char) * (properties[1] + 1);
        char *name = PyMem_Malloc(nameBufSize);
        glGetProgramResourceName(program, interface, i, nameBufSize, NULL, name);
        name[nameBufSize - 1] = '\0';

        NormalizeArrayName(name);
        PyDict_SetItemString(result, name, PyLong_FromLong(properties[0]));
        PyMem_Free(name);
    }

    return result;
}

static size_t GetUniformTypeSize(GLenum uniformType)
{
    switch (uniformType)
    {
    case GL_UNSIGNED_INT:
        return sizeof(GLuint);
    case GL_INT:
        return sizeof(GLint);
    case GL_FLOAT:
        return sizeof(GLfloat);
    case GL_DOUBLE:
        return sizeof(GLdouble);
    default:
        return 0;
    }
}

static bool GetUniformLocationString(PyShaderProgram *self, const char *uniformName, GLint *outLocation)
{
    PyObject *locationObj = PyDict_GetItemString(self->uniforms, uniformName);
    if (locationObj == NULL)
    {
        PyErr_Format(PyExc_RuntimeError, "Failed to find uniform with name \"%s\".", uniformName);
        return false;
    }

    *outLocation = PyLong_AsLong(locationObj);
    return true;
}

static bool GetUniformLocation(PyShaderProgram *self, PyObject *uniformNameObj, GLint *outLocation)
{
    PyObject *uniformLocationObj = PyDict_GetItem(self->uniforms, uniformNameObj);
    if (uniformLocationObj == NULL)
    {
        PyErr_Format(PyExc_RuntimeError, "Failed to find uniform with name \"%O\".", uniformNameObj);
        return false;
    }

    *outLocation = PyLong_AsLong(uniformLocationObj);
    return true;
}

static bool ConvertLongUniformValue(PyObject *value, GLenum uniformType, uint32_t *resultPtr)
{
    switch (uniformType)
    {
    case GL_INT:
    {
        GLint _value = PyLong_AsLong(value);
        *resultPtr = *(uint32_t *)&_value; // basically a reinterpret_cast
        break;
    }
    case GL_UNSIGNED_INT:
    {
        GLuint _value = PyLong_AsUnsignedLong(value);
        *resultPtr = *(uint32_t *)&_value;
        break;
    }
    case GL_FLOAT:
    {
        GLfloat _value = (float)PyLong_AsDouble(value);
        *resultPtr = *(uint32_t *)&_value;
        break;
    }
    case GL_DOUBLE:
    {
        GLdouble _value = PyLong_AsDouble(value);
        *resultPtr = *(uint32_t *)&_value;
        break;
    }
    default:
        PyErr_Format(PyExc_ValueError, "Invalid uniform type: %d.", uniformType);
        return false;
    }

    return true;
}

static bool ConvertFloatUniformValue(PyObject *value, GLenum uniformType, uint32_t *resultPtr)
{
    switch (uniformType)
    {
    case GL_FLOAT:
    {
        GLfloat _value = (float)PyFloat_AS_DOUBLE(value);
        *resultPtr = *(uint32_t *)&_value;
        break;
    }
    case GL_DOUBLE:
    {
        GLdouble _value = PyFloat_AS_DOUBLE(value);
        *resultPtr = *(uint32_t *)&_value;
        break;
    }
    default:
        PyErr_Format(PyExc_ValueError, "Invalid uniform type: %d.", uniformType);
        return false;
    }

    return true;
}

static bool ConvertUniformValue(PyObject *value, GLenum uniformType, uint32_t *resultPtr)
{
    if (PyLong_Check(value))
        return ConvertLongUniformValue(value, uniformType, resultPtr);
    else if (PyFloat_Check(value))
        return ConvertFloatUniformValue(value, uniformType, resultPtr);

    PyErr_Format(PyExc_TypeError, "Expected value to be either int or float, got: %s.", Py_TYPE(value)->tp_name);
    return false;
}

static bool ParseUniformMatrixArgs(
    PyShaderProgram *self,
    Py_ssize_t matrixLength,
    PyObject *const *args,
    Py_ssize_t nArgs,
    GLint *outUniformLocation,
    GLenum *outUniformType,
    bool *outTranspose,
    uint32_t *outValues)
{
    const char *uniformName;
    Py_buffer matrixBuffer = {0};

    if (!_PyArg_ParseStack(args, nArgs, "sIy*p", &uniformName, outUniformType, &matrixBuffer, outTranspose))
        return false;

    if (PyBuffer_ToContiguous(outValues, &matrixBuffer, sizeof(uint32_t) * matrixLength * matrixLength, 'C') == -1)
    {
        PyBuffer_Release(&matrixBuffer);
        return false;
    }

    PyBuffer_Release(&matrixBuffer);

    if (!GetUniformLocationString(self, uniformName, outUniformLocation))
        return false;

    return true;
}

static bool ParseUniformVectorArgs(
    PyShaderProgram *self,
    Py_ssize_t vectorLength,
    PyObject *const *args,
    Py_ssize_t nArgs,
    GLint *outUniformLocation,
    GLenum *outUniformType,
    uint32_t *outValues)
{
    const char *uniformName;
    if (nArgs == 3)
    {
        Py_buffer valuesBuffer = {0};
        if (!_PyArg_ParseStack(args, nArgs, "sI*y", &uniformName, outUniformType, &valuesBuffer))
            return false;

        if (PyBuffer_ToContiguous(outValues, &valuesBuffer, vectorLength * sizeof(uint32_t), 'C') == -1)
        {
            PyBuffer_Release(&valuesBuffer);
            return false;
        }

        PyBuffer_Release(&valuesBuffer);
    }
    else if (nArgs == vectorLength + 2)
    {
        if (!_PyArg_ParseStack(args, 2, "sI", &uniformName, outUniformType))
            return false;

        for (Py_ssize_t i = 0; i < vectorLength; i++)
            if (!ConvertUniformValue(args[i + 2], *outUniformType, &outValues[i]))
                return false;
    }
    else
    {
        PyErr_Format(PyExc_ValueError, "Function excepts 3 or 5 arguments, got: %d.", nArgs);
        return false;
    }

    return GetUniformLocationString(self, uniformName, outUniformLocation);
}

static int PyShaderProgram_init(PyShaderProgram *self, PyObject *args, PyObject *kwargs)
{
    (void)kwargs;

    PyObject *stageInfos;
    if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &stageInfos))
        return -1;

    self->id = glCreateProgram();

    Py_ssize_t nStages = PyList_GET_SIZE(stageInfos);
    GLuint *stages = PyMem_Malloc(sizeof(GLuint) * nStages);

    for (Py_ssize_t i = 0; i < nStages; i++)
    {
        PyShaderStageInfo *stageInfo = (PyShaderStageInfo *)PyList_GET_ITEM(stageInfos, i);
        if (!PyObject_IsInstance((PyObject *)stageInfo, (PyObject *)&PyShaderStageInfo_Type))
        {
            PyErr_SetString(PyExc_TypeError, "stages must be a list of ShaderStageInfo objects.");
            return -1;
        }

        GLuint stage = CreateStage(stageInfo);
        if (stage == -1)
            return -1;

        glAttachShader(self->id, stage);
        stages[i] = stage;
    }

    if (!LinkProgram(self->id))
        return -1;

    self->attributes = RetrieveInterface(self->id, GL_PROGRAM_INPUT);
    self->uniforms = RetrieveInterface(self->id, GL_UNIFORM);

    for (Py_ssize_t i = 0; i < nStages; i++)
    {
        glDetachShader(self->id, stages[i]);
        glDeleteShader(stages[i]);
    }

    PyMem_Free(stages);
    return 0;
}

static void PyShaderProgram_dealloc(PyShaderProgram *self)
{
    Py_XDECREF(self->uniforms);
    Py_XDECREF(self->attributes);
    Py_TYPE(self)->tp_free(self);
}

static PyShaderProgram *PyShaderProgram_from_binary(PyTypeObject *cls, PyObject *args)
{
    Py_buffer binaryData = {0};
    GLuint binaryFormat;
    if (!PyArg_ParseTuple(args, "y*I", &binaryData, &binaryFormat))
        return NULL;

    uint8_t *data = PyMem_Malloc(sizeof(uint8_t) * binaryData.len);
    if (PyBuffer_ToContiguous(data, &binaryData, binaryData.len, 'C') == -1)
    {
        PyMem_Free(data);
        PyBuffer_Release(&binaryData);
        return NULL;
    }

    PyShaderProgram *new = PyObject_New(PyShaderProgram, cls);
    new = (PyShaderProgram *)PyObject_Init((PyObject *)new, cls);

    new->id = glCreateProgram();
    glProgramBinary(new->id, binaryFormat, data, binaryData.len);

    PyMem_Free(data);
    PyBuffer_Release(&binaryData);

    if (!CheckLinkStatus(new->id))
        return NULL;

    new->uniforms = RetrieveInterface(new->id, GL_UNIFORM);
    new->attributes = RetrieveInterface(new->id, GL_PROGRAM_INPUT);

    return new;
}

static PyObject *PyShaderProgram_delete(PyShaderProgram *self, PyObject *args)
{
    (void)args;

    glDeleteProgram(self->id);
    self->id = 0;

    Py_RETURN_NONE;
}

static PyObject *PyShaderProgram_use(PyShaderProgram *self, PyObject *args)
{
    (void)args;
    glUseProgram(self->id);
    Py_RETURN_NONE;
}

static PyObject *PyShaderProgram_validate(PyShaderProgram *self, PyObject *args)
{
    (void)args;

    PyThreadState *tState = PyEval_SaveThread();

    glValidateProgram(self->id);

    GLint validateStatus = GL_FALSE;
    glGetProgramiv(self->id, GL_VALIDATE_STATUS, &validateStatus);

    if (!validateStatus)
    {
        GLint infoLogLength = 0;
        glGetProgramiv(self->id, GL_INFO_LOG_LENGTH, &infoLogLength);

        char *infoLog = PyMem_RawMalloc(sizeof(char) * infoLogLength);
        glGetProgramInfoLog(self->id, sizeof(char) * infoLogLength, NULL, infoLog);

        PyEval_RestoreThread(tState);
        PyErr_Format(PyExc_RuntimeError, "Failed to validate shader program (id: %s).\n%*.s", self->id, infoLogLength, infoLog);
        PyMem_RawFree(infoLog);

        return NULL;
    }

    PyEval_RestoreThread(tState);
    Py_RETURN_NONE;
}

static PyObject *PyShaderProgram_get_binary(PyShaderProgram *self, PyObject *args)
{
    (void)args;

    static bool binaryFormatsSupported = false;
    static bool binaryFormatsSupportChecked = false;
    if (!binaryFormatsSupportChecked)
    {
        GLint nBinaryFormatsSupported = 0;
        glGetIntegerv(GL_NUM_PROGRAM_BINARY_FORMATS, &nBinaryFormatsSupported);

        binaryFormatsSupported = nBinaryFormatsSupported != 0;
    }

    if (!binaryFormatsSupported)
    {
        PyErr_SetString(PyExc_RuntimeError, "The current driver doesn't support binary shader program formats.");
        return NULL;
    }

    GLint binaryLength = 0;
    glGetProgramiv(self->id, GL_PROGRAM_BINARY_LENGTH, &binaryLength);

    GLenum format;
    PyObject *bytesObj = PyBytes_FromStringAndSize(NULL, binaryLength);
    glGetProgramBinary(self->id, binaryLength * sizeof(uint8_t), NULL, &format, PyBytes_AS_STRING(bytesObj));

    return PyTuple_Pack(2, bytesObj, PyLong_FromUnsignedLong(format));
}

static PyObject *PyShaderProgram_set_uniform_block_binding(PyShaderProgram *self, PyObject *const *args, Py_ssize_t nArgs)
{
    const char *uniformBlockName;
    GLuint binding;
    if (!_PyArg_ParseStack(args, nArgs, "sI", &uniformBlockName, &binding))
        return NULL;

    GLuint blockIndex = glGetUniformBlockIndex(self->id, uniformBlockName);
    if (blockIndex == -1)
    {
        PyErr_Format(PyExc_RuntimeError, "Failed to find uniform block named \"%s\".", uniformBlockName);
        return NULL;
    }

    glUniformBlockBinding(self->id, blockIndex, binding);

    Py_RETURN_NONE;
}

static PyObject *PyShaderProgram_set_uniform(PyShaderProgram *self, PyObject *const *args, Py_ssize_t nArgs)
{
    const char *uniformName;
    PyObject *value;
    GLenum uniformType;
    if (!_PyArg_ParseStack(args, nArgs, "sOI", &uniformName, &value, &uniformType))
        return NULL;

    void *dataPtr;
    if (PyFloat_Check(value))
    {
        double data = PyFloat_AS_DOUBLE(value);
        dataPtr = &data;
    }
    else if (PyLong_Check(value))
    {
        int64_t data = PyLong_AsUnsignedLongLong(value);
        dataPtr = &data;
    }
    else
    {
        PyErr_Format(PyExc_TypeError, "Expected value to be of type int or float, got: %s.", Py_TYPE(value)->tp_name);
        return NULL;
    }

    PyObject *uniformLocationObj = PyDict_GetItemString(self->uniforms, uniformName);
    if (uniformLocationObj == NULL)
    {
        PyErr_Format(PyExc_RuntimeError, "Failed to find uniform named \"%s\".", uniformName);
        return NULL;
    }

    GLuint location = PyLong_AsUnsignedLong(uniformLocationObj);

    switch (uniformType)
    {
    case GL_FLOAT:
        glProgramUniform1f(self->id, location, *(float *)dataPtr);
        break;
    case GL_DOUBLE:
        glProgramUniform1d(self->id, location, *(double *)dataPtr);
        break;
    case GL_INT:
        glProgramUniform1i(self->id, location, *(GLint *)dataPtr);
        break;
    case GL_UNSIGNED_INT:
        glProgramUniform1ui(self->id, location, *(GLuint *)dataPtr);
        break;
    default:
        PyErr_Format(PyExc_ValueError, "Invalid OpenGL uniform type: %d.", uniformType);
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject *PyShaderProgram_set_uniform_array(PyShaderProgram *self, PyObject *const *args, Py_ssize_t nArgs)
{
    const char *uniformName;
    Py_buffer dataBuffer = {0};
    GLenum uniformType;
    if (!_PyArg_ParseStack(args, nArgs, "sy*I", &uniformName, &dataBuffer, &uniformType))
        return NULL;

    PyObject *uniformLocationObj = PyDict_GetItemString(self->uniforms, uniformName);
    if (uniformLocationObj == NULL)
    {
        PyErr_Format(PyExc_RuntimeError, "Failed to find uniform named \"%s\".", uniformName);
        return NULL;
    }

    GLuint location = PyLong_AsUnsignedLong(uniformLocationObj);
    void *dataPtr = PyMem_Malloc(dataBuffer.len);
    if (PyBuffer_ToContiguous(dataPtr, &dataBuffer, dataBuffer.len, 'C') == -1)
    {
        PyBuffer_Release(&dataBuffer);
        return NULL;
    }

    if (dataBuffer.itemsize != (Py_ssize_t)GetUniformTypeSize(uniformType))
    {
        PyErr_Format(PyExc_RuntimeError, "Item size of data inside provided buffer do not match item size of required uniform type. Stopping to prevent access violation.");
        return NULL;
    }

    const GLsizei count = (GLsizei)(dataBuffer.len / dataBuffer.itemsize);

    switch (uniformType)
    {
    case GL_FLOAT:
        glProgramUniform1fv(self->id, location, count, (float *)dataPtr);
        break;
    case GL_DOUBLE:
        glProgramUniform1dv(self->id, location, count, (double *)dataPtr);
        break;
    case GL_INT:
        glProgramUniform1iv(self->id, location, count, (GLint *)dataPtr);
        break;
    case GL_UNSIGNED_INT:
        glProgramUniform1uiv(self->id, location, count, (GLuint *)dataPtr);
        break;
    default:
        PyBuffer_Release(&dataBuffer);
        PyMem_Free(dataPtr);
        PyErr_Format(PyExc_ValueError, "Invalid OpenGL uniform type: %d.", uniformType);
        return NULL;
    }

    PyBuffer_Release(&dataBuffer);
    PyMem_Free(dataPtr);
    Py_RETURN_NONE;
}

static PyObject *PyShaderProgram_set_uniform_vec2(PyShaderProgram *self, PyObject *const *args, Py_ssize_t nArgs)
{
    uint32_t values[2];
    GLint uniformLocation;
    GLenum uniformType;

    if (!ParseUniformVectorArgs(self, 2, args, nArgs, &uniformLocation, &uniformType, values))
        return NULL;

    switch (uniformType)
    {
    case GL_INT:
        glProgramUniform2iv(self->id, uniformLocation, 1, (GLint *)values);
        break;
    case GL_UNSIGNED_INT:
        glProgramUniform2uiv(self->id, uniformLocation, 1, (GLuint *)values);
        break;
    case GL_FLOAT:
        glProgramUniform2fv(self->id, uniformLocation, 1, (GLfloat *)values);
        break;
    case GL_DOUBLE:
        glProgramUniform2dv(self->id, uniformLocation, 1, (GLdouble *)values);
        break;
    }

    Py_RETURN_NONE;
}

static PyObject *PyShaderProgram_set_uniform_vec3(PyShaderProgram *self, PyObject *const *args, Py_ssize_t nArgs)
{
    uint32_t values[3];
    GLint uniformLocation;
    GLenum uniformType;

    if (!ParseUniformVectorArgs(self, 3, args, nArgs, &uniformLocation, &uniformType, values))
        return NULL;

    switch (uniformType)
    {
    case GL_INT:
        glProgramUniform3iv(self->id, uniformLocation, 1, (GLint *)values);
        break;
    case GL_UNSIGNED_INT:
        glProgramUniform3uiv(self->id, uniformLocation, 1, (GLuint *)values);
        break;
    case GL_FLOAT:
        glProgramUniform3fv(self->id, uniformLocation, 1, (GLfloat *)values);
        break;
    case GL_DOUBLE:
        glProgramUniform3dv(self->id, uniformLocation, 1, (GLdouble *)values);
        break;
    }

    Py_RETURN_NONE;
}

static PyObject *PyShaderProgram_set_uniform_vec4(PyShaderProgram *self, PyObject *const *args, Py_ssize_t nArgs)
{
    uint32_t values[4];
    GLint uniformLocation;
    GLenum uniformType;

    if (!ParseUniformVectorArgs(self, 4, args, nArgs, &uniformLocation, &uniformType, values))
        return NULL;

    switch (uniformType)
    {
    case GL_INT:
        glProgramUniform4iv(self->id, uniformLocation, 1, (GLint *)values);
        break;
    case GL_UNSIGNED_INT:
        glProgramUniform4uiv(self->id, uniformLocation, 1, (GLuint *)values);
        break;
    case GL_FLOAT:
        glProgramUniform4fv(self->id, uniformLocation, 1, (GLfloat *)values);
        break;
    case GL_DOUBLE:
        glProgramUniform4dv(self->id, uniformLocation, 1, (GLdouble *)values);
        break;
    }

    Py_RETURN_NONE;
}

static PyObject *PyShaderProgram_set_uniform_mat2(PyShaderProgram *self, PyObject *const *args, Py_ssize_t nArgs)
{
    uint32_t values[2 * 2];
    GLint location;
    GLenum uniformType;
    bool transpose;
    if (!ParseUniformMatrixArgs(self, 2, args, nArgs, &location, &uniformType, &transpose, values))
        return NULL;

    switch (uniformType)
    {
    case GL_FLOAT:
        glProgramUniformMatrix2fv(self->id, location, 1, (GLboolean)transpose, (GLfloat *)values);
        break;
    case GL_DOUBLE:
        glProgramUniformMatrix2dv(self->id, location, 1, (GLboolean)transpose, (GLdouble *)values);
        break;
    default:
        PyErr_Format(PyExc_ValueError, "Invalid uniform type for the function: %d.", uniformType);
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject *PyShaderProgram_set_uniform_mat3(PyShaderProgram *self, PyObject *const *args, Py_ssize_t nArgs)
{
    uint32_t values[3 * 3];
    GLint location;
    GLenum uniformType;
    bool transpose;
    if (!ParseUniformMatrixArgs(self, 3, args, nArgs, &location, &uniformType, &transpose, values))
        return NULL;

    switch (uniformType)
    {
    case GL_FLOAT:
        glProgramUniformMatrix3fv(self->id, location, 1, (GLboolean)transpose, (GLfloat *)values);
        break;
    case GL_DOUBLE:
        glProgramUniformMatrix3dv(self->id, location, 1, (GLboolean)transpose, (GLdouble *)values);
        break;
    default:
        PyErr_Format(PyExc_ValueError, "Invalid uniform type for the function: %d.", uniformType);
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject *PyShaderProgram_set_uniform_mat4(PyShaderProgram *self, PyObject *const *args, Py_ssize_t nArgs)
{
    uint32_t values[4 * 4];
    GLint location;
    GLenum uniformType;
    bool transpose;
    if (!ParseUniformMatrixArgs(self, 4, args, nArgs, &location, &uniformType, &transpose, values))
        return NULL;

    switch (uniformType)
    {
    case GL_FLOAT:
        glProgramUniformMatrix4fv(self->id, location, 1, (GLboolean)transpose, (GLfloat *)values);
        break;
    case GL_DOUBLE:
        glProgramUniformMatrix4dv(self->id, location, 1, (GLboolean)transpose, (GLdouble *)values);
        break;
    default:
        PyErr_Format(PyExc_ValueError, "Invalid uniform type for the function: %d.", uniformType);
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject *PyShaderProgram_set_debug_name(PyShaderProgram *self, PyObject *name)
{
    CHECK_ARG_STRING(name, NULL);

    Py_ssize_t nameLength = 0;
    const char *nameStr = PyUnicode_AsUTF8AndSize(name, &nameLength);

    glObjectLabel(GL_PROGRAM, self->id, nameLength, nameStr);

    Py_RETURN_NONE;
}

PyTypeObject PyShaderProgram_Type = {
    PY_VAR_OBJECT_HEAD_INIT(NULL, 0),
    .tp_name = "spyke.graphics.gl.ShaderProgram",
    .tp_basicsize = sizeof(PyShaderProgram),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)PyShaderProgram_init,
    .tp_dealloc = (destructor)PyShaderProgram_dealloc,
    .tp_members = (PyMemberDef[]){
        {"id", Py_T_UINT, offsetof(PyShaderProgram, id), Py_READONLY, NULL},
        {"uniforms", Py_T_OBJECT_EX, offsetof(PyShaderProgram, uniforms), Py_READONLY, NULL},
        {"attributes", Py_T_OBJECT_EX, offsetof(PyShaderProgram, attributes), Py_READONLY, NULL},
        {0},
    },
    .tp_methods = (PyMethodDef[]){
        {"from_binary", (PyCFunction)PyShaderProgram_from_binary, METH_VARARGS | METH_CLASS, NULL},
        {"delete", (PyCFunction)PyShaderProgram_delete, METH_NOARGS, NULL},
        {"use", (PyCFunction)PyShaderProgram_use, METH_NOARGS, NULL},
        {"validate", (PyCFunction)PyShaderProgram_validate, METH_NOARGS, NULL},
        {"get_binary", (PyCFunction)PyShaderProgram_get_binary, METH_NOARGS, NULL},
        {"set_uniform_block_binding", (PyCFunction)PyShaderProgram_set_uniform_block_binding, METH_FASTCALL, NULL},
        {"set_uniform", (PyCFunction)PyShaderProgram_set_uniform, METH_FASTCALL, NULL},
        {"set_uniform_array", (PyCFunction)PyShaderProgram_set_uniform_array, METH_FASTCALL, NULL},
        // TODO Implement and ShaderProgram.set_uniform_mat*
        {"set_uniform_vec2", (PyCFunction)PyShaderProgram_set_uniform_vec2, METH_FASTCALL, NULL},
        {"set_uniform_vec3", (PyCFunction)PyShaderProgram_set_uniform_vec3, METH_FASTCALL, NULL},
        {"set_uniform_vec4", (PyCFunction)PyShaderProgram_set_uniform_vec4, METH_FASTCALL, NULL},
        {"set_uniform_mat2", (PyCFunction)PyShaderProgram_set_uniform_mat2, METH_FASTCALL | METH_KEYWORDS, NULL},
        {"set_uniform_mat3", (PyCFunction)PyShaderProgram_set_uniform_mat3, METH_FASTCALL, NULL},
        {"set_uniform_mat4", (PyCFunction)PyShaderProgram_set_uniform_mat4, METH_FASTCALL, NULL},
        {"set_debug_name", (PyCFunction)PyShaderProgram_set_debug_name, METH_O, NULL},
        {0},
    },
};
