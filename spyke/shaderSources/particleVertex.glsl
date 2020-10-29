#version 450 core

layout(location = 0) in vec3 aPosition;
layout(location = 1) in vec4 aColor;
layout(location = 2) in vec2 aTexCoord;
layout(location = 3) in float aTexIdx;

out vec4 vColor;
out vec2 vTexCoord;
out float vTexIdx;

uniform mat4 uViewProjection;

void main()
{
    vColor = aColor;
    vTexCoord = aTexCoord;
    vTexIdx = aTexIdx;

    gl_Position = uViewProjection * vec4(aPosition, 1.0f);
}