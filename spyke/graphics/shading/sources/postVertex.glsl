#version 450 core
layout(location = 0) in vec3 aPosition;
layout(location = 1) in vec4 aColor;
layout(location = 2) in vec2 aTexCoord;
layout(location = 3) in vec2 aTilingFactor;

out vec4 vColor;
out vec2 vTexCoord;
out vec2 vTilingFactor;

void main()
{
    vColor = aColor;
    vTexCoord = aTexCoord;
    vTilingFactor = aTilingFactor;

    gl_Position = vec4(aPosition, 1.0f);
}