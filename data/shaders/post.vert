#version 450 core

const vec2 c_Positions[] = {
    vec2(0.0, 0.0),
    vec2(0.0, 1.0),
    vec2(1.0, 1.0),
    vec2(1.0, 1.0),
    vec2(1.0, 0.0),
    vec2(0.0, 0.0)};
const vec2 c_TexCoords[] = {
    vec2(0.0, 1.0),
    vec2(0.0, 0.0),
    vec2(1.0, 0.0),
    vec2(1.0, 0.0),
    vec2(1.0, 1.0),
    vec2(0.0, 1.0)};

out vec2 vsTexCoord;

void main()
{
    vsTexCoord = c_TexCoords[gl_VertexID];
    gl_Position = vec4(c_Positions[gl_VertexID], 0.0, 1.0);
}
