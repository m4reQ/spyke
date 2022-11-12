#version 450 core

const int VerticesPerInstance = 6;

// per-vertex
layout(location=0) in vec3 aPosition;

// per-instance
layout(location=1) in vec4 aColor;
layout(location=2) in float aTexIdx;
layout(location=3) in float aEntId;
layout(location=4) in mat4 aTransform;

uniform samplerBuffer uTexCoordsBuffer;

out FsIn
{
    vec4 color;
    vec2 texCoord;
    flat float texIdx;
    flat float entId;
} vsOut;

layout(std140) uniform uMatrices
{
    mat4 viewProjection;
};

void main()
{
    vsOut.color = aColor;
    vsOut.texIdx = aTexIdx;
    vsOut.entId = aEntId;

    int bufferOffset = (gl_InstanceID * VerticesPerInstance) + gl_VertexID;
    vsOut.texCoord = texelFetch(uTexCoordsBuffer, bufferOffset).rg;

    gl_Position = aTransform * viewProjection * vec4(aPosition, 1.0f);
}
