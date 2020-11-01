#version 450 core

in vec2 vTexCoord;
layout(location = 10) in vec4 color;
layout(location = 11) in float texIdx;

out vec4 Color;

uniform sampler2DArray uTexture;

void main()
{
	Color = texture(uTexture, vec3(vTexCoord, texIdx)) * color;
}