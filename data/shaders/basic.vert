#version 450 core

// per-vertex data:
layout(location=0) in vec3 aPosition;
layout(location=1) in vec2 aTexCoord;

// per-instance data:
layout(location=2) in vec4 aColor;
layout(location=3) in float aTexIdx;
layout(location=4) in float aEntId;
layout(location=5) in mat4 aTransform;

out FsIn
{
    vec4 color;
    vec2 texCoord;
    flat float texIdx;
    flat float entId;
} vsOut;

layout(std140) uniform uMatrices
{
    mat4 view;
    mat4 projection;
};

void main()
{
    vsOut.color = aColor;
    vsOut.texCoord = aTexCoord;
    vsOut.texIdx = aTexIdx;
    vsOut.entId = aEntId;

    gl_Position = aTransform * view * projection * vec4(aPosition, 1.0f);
}
