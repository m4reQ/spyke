#version 450 core

layout(points) in;
layout(triangle_strip, max_vertices = 4) out;

uniform mat4 uViewProjection;

const vec2 QuadVertices[4] = vec2[4](
	vec2(0.0f, 0.0f),
	vec2(1.0f, 0.0f),
	vec2(1.0f, 1.0f),
	vec2(0.0f, 1.0f));

out VS_OUT
{
	vec2 pos;
	vec2 size;
	float rot;
	vec2 texCoord;
} gsIn[];

out vec2 vTexCoord;

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
	gl_Position = uViewProjection * vec4(translate(QuadVertices[0], gsIn[0].pos) * rotScale, 0.0f, 1.0f);
	//vColor = color;
	vTexCoord = vec2(0.0f, gsIn[0].texCoord.y);
	EmitVertex();

	gl_Position = uViewProjection * vec4(translate(QuadVertices[1], gsIn[0].pos) * rotScale, 0.0f, 1.0f);
	//vColor = color;
	vTexCoord = gsIn[0].texCoord;
	EmitVertex();

	gl_Position = uViewProjection * vec4(translate(QuadVertices[2], gsIn[0].pos) * rotScale, 0.0f, 1.0f);
	//vColor = color;
	vTexCoord = vec2(gsIn[0].texCoord.x, 0.0f);
	EmitVertex();

	gl_Position = uViewProjection * vec4(translate(QuadVertices[3], gsIn[0].pos) * rotScale, 0.0f, 1.0f);
	//vColor = color;
	vTexCoord = vec2(0.0f);
	EmitVertex();
}

void main()
{
	mat2 rotScale = createRotation(gsIn[0].rot) * createScale(gsIn[0].size);

	EmitVertices(rotScale);
	EndPrimitive();
}