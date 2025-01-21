#pragma once
#include <stdbool.h>
#include <stdint.h>
#include <Python.h>
#include "../utils.h"

typedef struct
{
    PyObject *pyCallback;
    int32_t priority;
    bool shouldConsume;
} EventHandler;

typedef struct
{
    PY_OBJECT_HEAD;
    EventHandler *handlers;
} PyEvent;

typedef PyObject *(*PyEventInvokeFn)(PyEvent *, PyObject *);

typedef struct
{
    PyTypeObject *pyEventType;
    PyEventInvokeFn pyEventInvoke;
} EventsAPI;
