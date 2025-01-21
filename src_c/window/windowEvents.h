#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "../utils.h"

typedef struct
{
    PY_OBJECT_HEAD;
    uint16_t width;
    uint16_t height;
} PyResizeEventData;

typedef struct
{
    PY_OBJECT_HEAD;
    uint16_t x;
    uint16_t y;
} PyMoveEventData;

typedef struct
{
    PY_OBJECT_HEAD;
    double time;
} PyCloseEventData;

typedef struct
{
    PY_OBJECT_HEAD;
    uint16_t x;
    uint16_t y;
    uint16_t modifiers;
} PyMouseMoveEventData;

typedef struct
{
    PY_OBJECT_HEAD;
    bool isVisible;
} PyShowEventData;

typedef struct
{
    PY_OBJECT_HEAD;
    uint16_t x;
    uint16_t y;
    int16_t delta;
    uint16_t modifiers;
} PyScrollEventData;

typedef struct
{
    PY_OBJECT_HEAD;
    uint32_t key;
    uint16_t repeatCount;
    uint8_t scanCode;
    bool wasPressed;
} PyKeyDownEventData;

typedef struct
{
    PY_OBJECT_HEAD;
    uint32_t key;
    uint8_t scanCode;
} PyKeyUpEventData;

typedef struct
{
    PY_OBJECT_HEAD;
    uint32_t character;
    uint16_t repeatCount;
    uint8_t scanCode;
    bool wasPressed;
} PyCharEventData;

typedef struct
{
    PY_OBJECT_HEAD;
    uint16_t x;
    uint16_t y;
    uint8_t button;
    uint8_t modifiers;
} PyButtonDownEventData;

typedef struct
{
    PY_OBJECT_HEAD;
    uint16_t x;
    uint16_t y;
    uint8_t button;
    uint8_t modifiers;
} PyButtonUpEventData;

extern PyTypeObject PyResizeEventData_Type;
extern PyTypeObject PyButtonUpEventData_Type;
extern PyTypeObject PyButtonDownEventData_Type;
extern PyTypeObject PyCharEventData_Type;
extern PyTypeObject PyKeyUpEventData_Type;
extern PyTypeObject PyKeyDownEventData_Type;
extern PyTypeObject PyScrollEventData_Type;
extern PyTypeObject PyShowEventData_Type;
extern PyTypeObject PyMouseMoveEventData_Type;
extern PyTypeObject PyCloseEventData_Type;
extern PyTypeObject PyMoveEventData_Type;
