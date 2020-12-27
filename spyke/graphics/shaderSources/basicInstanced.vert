#version 450 core

layout(location=0) in vec3 aPosition;
layout(location=1) in vec4 aColor;
layout(location=2) in vec2 aTexCoord;
layout(location=3) in float aTexIdx;
layout(location=4) in vec2 aTilingFactor;
layout(location=5) in mat4 aTransform;

out vec4 vColor;
out vec2 vTexCoord;
out float vTexIdx;

uniform mat4 uViewProjection;

void main()
{
    vColor = aColor;
    vTexCoord = aTexCoord * aTilingFactor;
    vTexIdx = aTexIdx;
    
    gl_Position = aTransform * uViewProjection * vec4(aPosition, 1.0f);
}