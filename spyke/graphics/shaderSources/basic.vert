#version 450 core

// per-vertex data:
layout(location=0) in vec3 aPosition;

// per-instance data:
layout(location=1) in vec4 aColor;
layout(location=2) in vec2 aTiling;
layout(location=3) in float aTexIndex;
layout(location=4) in float aEntityId;
layout(location=5) in mat4 aTransform;

out FsIn
{
    vec4 color;
    vec2 texCoords;
    flat float texIndex;
    flat float entityId;
} vsOut;

layout(std140) uniform uMatrices
{
    mat4 viewProjection;
};

uniform int uVerticesPerInstance;
uniform samplerBuffer uTextureCoordsBuffer; // per-vertex data, texture coordinates

void main()
{
    vsOut.color = aColor;
    vsOut.texIndex = aTexIndex;
    vsOut.entityId = aEntityId;

    int bufferOffset = (gl_InstanceID * uVerticesPerInstance) + gl_VertexID;
    vsOut.texCoords = texelFetch(uTextureCoordsBuffer, bufferOffset).rg * aTiling;

    gl_Position = aTransform * viewProjection * vec4(aPosition, 1.0f);
}