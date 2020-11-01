#version 450 core

layout(location = 0) in vec2 aPosition;
layout(location = 1) in vec2 aSize;
layout(location = 2) in float aRotation;
layout(location = 3) in vec4 aColor;
layout(location = 4) in vec2 aTexCoord;
layout(location = 5) in float aTexIdx;

layout(location = 10) out vec4 vColor;
layout(location = 11) out float vTexIdx;

out VS_OUT
{
	vec2 pos;
	vec2 size;
	float rot;
	vec2 texCoord;
} vsOut;

void main()
{
	vsOut.pos = aPosition;
	vsOut.size = aSize;
	vsOut.rot = aRotation;
	vsOut.texCoord = aTexCoord;

	vTexIdx = aTexIdx;
	vColor = aColor;
}