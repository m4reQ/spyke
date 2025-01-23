#version 450

// model data
layout(location=0) in vec3 aPosition;
layout(location=1) in vec2 aTexCoord;
layout(location=2) in vec3 aNormal;
// instance data
layout(location=3) in vec4 aColor;
layout(location=4) in float aTextureIndex;
layout(location=5) in mat4 aTransform;

out VSOut {
    vec2 texCoord;
    vec3 normal;
    vec3 worldPos;
    vec4 color;
    flat float textureIndex;
} vsOut;

layout(std140) uniform uCameraMatrices
{
    mat4 view;
    mat4 projection;
};

void main()
{
    vsOut.texCoord = aTexCoord;
    vsOut.normal = (aTransform * vec4(aNormal, 1.0)).xyz;
    vsOut.worldPos = (aTransform * vec4(aPosition, 1.0)).xyz;
    vsOut.color = aColor;
    vsOut.textureIndex = aTextureIndex;

    gl_Position = aTransform * view * projection * vec4(aPosition, 1.0);
}
