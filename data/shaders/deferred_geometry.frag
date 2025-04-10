#version 450

in VSOut {
    vec2 texCoord;
    vec3 normal;
    vec3 worldPos;
    vec4 color;
    flat float albedoTextureIndex;
    flat float specularTextureIndex;
} vsOut;

layout(location=1) out vec4 outAlbedoSpecular;
layout(location=2) out vec3 outNormal;
layout(location=3) out vec3 outWorldPos;

uniform sampler2D uTextures[16];

void main()
{
    outWorldPos = vsOut.worldPos;
    outNormal = vsOut.normal;
    outAlbedoSpecular.rgb = vsOut.color.rgb * texture(uTextures[uint(vsOut.albedoTextureIndex)], vsOut.texCoord).rgb;
    outAlbedoSpecular.a = texture(uTextures[uint(vsOut.specularTextureIndex)], vsOut.texCoord).r;
}
