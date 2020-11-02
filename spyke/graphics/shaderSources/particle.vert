#version 450 core

layout(location = 0) in vec2 aPosition;
layout(location = 1) in vec2 aSize;
layout(location = 2) in float aRotation;
layout(location = 3) in vec4 aColor;
layout(location = 4) in vec2 aTexCoord;
layout(location = 5) in float aTexIdx;

out VS_OUT
{
	vec2 pos;
	vec2 size;
	float rot;
	vec4 color;
	vec2 texCoord;
	float texIdx;
} vsOut;

void main()
{
	vsOut.pos = aPosition;
	vsOut.size = aSize;
	vsOut.rot = aRotation;
	vsOut.texCoord = aTexCoord;
	vsOut.color = aColor;
	vsOut.texIdx = aTexIdx;
}