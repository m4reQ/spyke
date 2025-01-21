#pragma once
#include <stdint.h>
#include <stdbool.h>

typedef void (*PyInputAppendTextCharFn)(wchar_t);
typedef void (*PyInputUpdateModifiersFn)(uint8_t);
typedef void (*PyInputUpdateMousePosFn)(uint16_t, uint16_t);
typedef void (*PyInputUpdateKeyStateFn)(uint8_t, bool);
typedef void (*PyInputUpdateButtonStateFn)(uint8_t, bool);

typedef enum
{
    BUTTON_X1 = 1,
    BUTTON_X2 = 2,
    BUTTON_LEFT = 3,
    BUTTON_RIGHT = 4,
    BUTTON_MIDDLE = 5,
} Button;

typedef struct
{
    PyInputAppendTextCharFn AppendTextChar;
    PyInputUpdateModifiersFn UpdateModifiers;
    PyInputUpdateMousePosFn UpdateMousePos;
    PyInputUpdateKeyStateFn UpdateKeyState;
    PyInputUpdateButtonStateFn UpdateButtonState;
} PyInput_API;
