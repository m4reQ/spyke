#version 450 core
layout(location = 0) in vec3 aPosition;
layout(location = 1) in vec4 aColor;

out vec4 vColor;

layout (std140) uniform uMatrices
{
    mat4 viewProjection;
};

void main()
{
    vColor = aColor;
    gl_Position = viewProjection * vec4(aPosition, 1.0f);
}