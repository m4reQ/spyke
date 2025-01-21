#version 450

in VSOut {
    vec2 texCoord;
    vec3 normal;
    vec3 worldPos;
    vec4 color;
    uint textureIndex;
} vsOut;

layout(location=0) out vec4 outDiffuse;
layout(location=1) out vec3 outWorldPos;
layout(location=2) out vec3 outNormal;
layout(location=3) out vec2 outTexCoord;

uniform sampler2D uTextures[16];

void main()
{
    outDiffuse = vsOut.color * texture(uTextures[vsOut.textureIndex], vsOut.texCoord);
    outWorldPos = vsOut.worldPos;
    outNormal = normalize(vsOut.normal);
    outTexCoord = vsOut.texCoord;
}
