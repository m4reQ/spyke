#version 450 core

in vec2 vTexCoord;
in vec4 vColor;
in float vTexIdx;

layout(location = 0) out vec4 Color;

uniform sampler2DArray uTexture;

void main()
{
	Color = texture(uTexture, vec3(vTexCoord, vTexIdx)) * vColor;
}