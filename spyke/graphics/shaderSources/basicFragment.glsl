#version 450 core

in vec4 vColor;
in vec2 vTexCoord;
in float vTexIdx;
in vec2 vTilingFactor;

out vec4 Color;

uniform sampler2DArray uTextureArray;

void main()
{
    Color = texture(uTextureArray, vec3(vTexCoord.xy * vTilingFactor, vTexIdx)) * vColor;
}