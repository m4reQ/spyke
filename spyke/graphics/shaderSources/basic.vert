#version 450 core
const int VERTICES_PER_INSTANCE = 4;

layout(location=0) in vec3 aPosition;

layout(location=1) in vec4 aColor;
layout(location=2) in vec2 aTilingFactor;
layout(location=3) in float aTexIdx;
layout(location=4) in float aEntId;
layout(location=5) in mat4 aTransform;

out vec4 vColor;
out vec2 vTexCoord;
out float vTexIdx;
out float vEntId;

layout(std140) uniform uMatrices
{
    mat4 viewProjection;
};

uniform samplerBuffer uTexCoordsBuffer;

void main()
{
    vTexCoord = texelFetch(uTexCoordsBuffer, gl_InstanceID * VERTICES_PER_INSTANCE + gl_VertexID).rg * aTilingFactor;

    vColor = aColor;
    vTexIdx = aTexIdx;
    vEntId = aEntId;
    
    gl_Position = aTransform * viewProjection * vec4(aPosition, 1.0f);
}