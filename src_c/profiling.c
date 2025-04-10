#pragma once
#include <stdio.h>
#include <stdbool.h>
#include "utils.h"

#ifdef _WIN32
#include <windows.h>
#else
#error "Unsupported platform: profiling.c"
#endif

#define PROFILE_FILE_HEADER "{\"traceEvents\":[{}"
#define PROFILE_FILE_FOOTER "]}"
#define FRAME_FORMAT ",{\"name\":\"%s\",\"ph\":\"X\",\"ts\":%lf,\"dur\":%lf,\"tid\":%d}"
#define EVENT_FORMAT ",{\"name\":\"%s\",\"ph\":\"I\",\"ts\":%lf,\"s\":\"g\"}"
#define COUNTER_FORMAT ",{\"name\":\"%s\",\"ph\":\"C\",\"ts\":%lf,\"args\":{\"\":%lf}}"

static FILE *s_ProfileFile;
static HANDLE s_WriteMutex;
static uint64_t s_ProfileBeginTs;
static uint64_t s_ClockResolution;

static bool IsProfilingEnabled(void)
{
    return s_ProfileFile != NULL;
}

static void AcquireWriteMutex(void)
{
    WaitForSingleObject(s_WriteMutex, INFINITE);
}

static void ReleaseWriteMutex(void)
{
    ReleaseMutex(s_WriteMutex);
}

static void EndSession(void)
{
    AcquireWriteMutex();

    fprintf(s_ProfileFile, PROFILE_FILE_FOOTER);
    fclose(s_ProfileFile);
    s_ProfileFile = NULL;

    ReleaseWriteMutex();
}

static uint64_t GetNow(void)
{
    uint64_t now;
    QueryPerformanceCounter((LARGE_INTEGER *)&now);

    return now;
}

static double DurationToUs(uint64_t begin, uint64_t end)
{
    return ((end - begin) / (double)s_ClockResolution) * 1000000;
}

static PyObject *PyProfiling_BeginFrame(PyObject *self, PyObject *args)
{
    (void)self;
    (void)args;

    return IsProfilingEnabled() ? PyLong_FromUnsignedLongLong(GetNow()) : Py_NewRef(Py_None);
}

static PyObject *PyProfiling_EndFrame(PyObject *self, PyObject *const *args, Py_ssize_t argsCount)
{
    (void)self;

    if (!IsProfilingEnabled())
        Py_RETURN_NONE;

    uint64_t startTimestamp;
    const char *funcName;
    if (!_PyArg_ParseStack(args, argsCount, "Ks", &startTimestamp, &funcName))
        return NULL;

    AcquireWriteMutex();
    fprintf(s_ProfileFile, FRAME_FORMAT, funcName, DurationToUs(s_ProfileBeginTs, startTimestamp), DurationToUs(startTimestamp, GetNow()), GetCurrentThreadId());
    ReleaseWriteMutex();

    Py_RETURN_NONE;
}

static PyObject *PyProfiling_EmitEvent(PyObject *self, PyObject *eventName)
{
    (void)self;

    if (!IsProfilingEnabled())
        Py_RETURN_NONE;

    CHECK_ARG_STRING(eventName, NULL);

    AcquireWriteMutex();
    fprintf(s_ProfileFile, EVENT_FORMAT, PyUnicode_AsUTF8(eventName), DurationToUs(s_ProfileBeginTs, GetNow()));
    ReleaseWriteMutex();

    Py_RETURN_NONE;
}

static PyObject *PyProfiling_UpdateCounter(PyObject *self, PyObject *const *args, Py_ssize_t argsCount)
{
    (void)self;

    if (!IsProfilingEnabled())
        Py_RETURN_NONE;

    double value;
    const char *counterName;
    if (!_PyArg_ParseStack(args, argsCount, "ds", &value, &counterName))
        return NULL;

    AcquireWriteMutex();
    fprintf(s_ProfileFile, COUNTER_FORMAT, counterName, DurationToUs(s_ProfileBeginTs, GetNow()), value);
    ReleaseWriteMutex();

    Py_RETURN_NONE;
}

static PyObject *PyProfiling_EndSession(PyObject *self, PyObject *args)
{
    (void)self;
    (void)args;

    if (IsProfilingEnabled())
        EndSession();

    Py_RETURN_NONE;
}

static PyObject *PyProfiling_BeginSession(PyObject *self, PyObject *filepath)
{
    (void)self;

    CHECK_ARG_STRING(filepath, NULL);

    if (IsProfilingEnabled())
        EndSession();

    const errno_t openResult = fopen_s(&s_ProfileFile, PyUnicode_AsUTF8(filepath), "w+");
    if (openResult)
        return PyErr_SetFromErrno(PyExc_IOError);

    fprintf(s_ProfileFile, PROFILE_FILE_HEADER);

    s_ProfileBeginTs = GetNow();

    Py_RETURN_NONE;
}

static PyObject *PyProfiling_IsProfilingEnabled(PyObject *self, PyObject *args)
{
    (void)self;
    (void)args;

    return PyBool_FromLong(IsProfilingEnabled());
}

static void PyProfiling_Free(PyObject *self)
{
    (void)self;

    CloseHandle(s_WriteMutex);
    if (IsProfilingEnabled())
        EndSession();
}

static PyModuleDef s_ModuleDef = {
    PyModuleDef_HEAD_INIT,
    .m_name = "spyke.debug.profiling",
    .m_free = PyProfiling_Free,
    .m_methods = (PyMethodDef[]){
        {"begin_profiling_session", PyProfiling_BeginSession, METH_O, NULL},
        {"end_profiling_session", PyProfiling_EndSession, METH_NOARGS, NULL},
        {"begin_profiling_frame", PyProfiling_BeginFrame, METH_NOARGS, NULL},
        {"end_profiling_frame", (PyCFunction)PyProfiling_EndFrame, METH_FASTCALL, NULL},
        {"emit_profiling_event", PyProfiling_EmitEvent, METH_O, NULL},
        {"update_profiling_counter", (PyCFunction)PyProfiling_UpdateCounter, METH_FASTCALL, NULL},
        {"is_profiling_enabled", (PyCFunction)PyProfiling_IsProfilingEnabled, METH_NOARGS, NULL},
        {0},
    },
    .m_size = -1,
};

PyMODINIT_FUNC PyInit_profiling()
{
    if (!QueryPerformanceFrequency((LARGE_INTEGER *)&s_ClockResolution))
    {
        PyErr_SetString(PyExc_SystemError, "QueryPerformanceCounter failed to retrieve clock resolution.");
        return NULL;
    }

    s_WriteMutex = CreateMutex(NULL, FALSE, NULL);
    if (!s_WriteMutex)
    {
        PyErr_SetString(PyExc_SystemError, "CreateMutex failed to create mutex.");
        return NULL;
    }

    return PyModule_Create(&s_ModuleDef);
}
