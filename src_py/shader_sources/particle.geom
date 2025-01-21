#version 450 core

layout(points) in;
layout(triangle_strip, max_vertices = 4) out;

layout (std140) uniform uMatrices
{
    mat4 viewProjection;
};

const vec2 QuadVertices[4] = vec2[4](
	vec2(1.0f, 1.0f), //up-right
	vec2(1.0f, 0.0f),
	vec2(0.0f, 1.0f),
	vec2(0.0f, 0.0f));

in VS_OUT
{
	vec2 pos;
	vec2 size;
	float rot;
	vec4 color;
	vec2 texCoord;
	float texIdx;
} gsIn[];

out vec2 vTexCoord;
out vec4 vColor;
out float vTexIdx;

mat2 createRotation(float rotation)
{
	float s = sin(rotation);
	float c = cos(rotation);

	return mat2(c, -s, s, c);
}

vec2 translate(vec2 baseVector, vec2 pos)
{
	return baseVector + pos;
}

mat2 createScale(vec2 scale)
{
	return mat2(scale.x, 0.0f, 0.0f, scale.y);
}

void EmitVertices(mat2 rotScale)
{
	gl_Position = viewProjection * vec4(translate(QuadVertices[0], gsIn[0].pos) * rotScale, 0.0f, 1.0f);
	vColor = gsIn[0].color;
	vTexCoord = gsIn[0].texCoord;
	vTexIdx = gsIn[0].texIdx;
	EmitVertex();

	gl_Position = viewProjection * vec4(translate(QuadVertices[1], gsIn[0].pos) * rotScale, 0.0f, 1.0f);
	vColor = gsIn[0].color;
	vTexCoord = vec2(gsIn[0].texCoord.x, 0.0f);
	vTexIdx = gsIn[0].texIdx;
	EmitVertex();

	gl_Position = viewProjection * vec4(translate(QuadVertices[2], gsIn[0].pos) * rotScale, 0.0f, 1.0f);
	vColor = gsIn[0].color;
	vTexCoord = vec2(0.0f, gsIn[0].texCoord.y);
	vTexIdx = gsIn[0].texIdx;
	EmitVertex();

	gl_Position = viewProjection * vec4(translate(QuadVertices[3], gsIn[0].pos) * rotScale, 0.0f, 1.0f);
	vColor = gsIn[0].color;
	vTexCoord = vec2(0.0f);
	vTexIdx = gsIn[0].texIdx;
	EmitVertex();
}

void main()
{
	mat2 rotScale = createRotation(gsIn[0].rot) * createScale(gsIn[0].size);

	EmitVertices(rotScale);
	EndPrimitive();
}