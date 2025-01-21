#version 450 core
const int VERTICES_PER_INSTANCE = 4;

layout(location = 0) in vec3 aPosition;
layout(location = 1) in vec2 aTexCoord;

out vec2 vTexCoord;

layout (std140) uniform uMatrices
{
    mat4 viewProjection;
};

void main()
{
    vTexCoord = aTexCoord;

    gl_Position = viewProjection * vec4(aPosition, 1.0f);
}