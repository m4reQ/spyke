#version 450 core
const int VERTICES_PER_INSTANCE = 4;

layout(location = 0) in vec3 aPosition;

layout(location = 1) in vec4 aColor;

out vec4 vColor;
out vec2 vTexCoord;

layout (std140) uniform uMatrices
{
    mat4 viewProjection;
};

uniform samplerBuffer uTexCoordsBuffer;

void main()
{
    vColor = aColor;
    vTexCoord = texelFetch(uTexCoordsBuffer, gl_InstanceID * VERTICES_PER_INSTANCE + gl_VertexID).rg;

    gl_Position = viewProjection * vec4(aPosition, 1.0f);
}