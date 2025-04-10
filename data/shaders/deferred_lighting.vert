#version 450 core

out vec2 vsTexCoords;

const vec4 cVertices[6] = {
    vec4(-1.0, -1.0, 0.0, 1.0),
    vec4(-1.0, 1.0, 1.0, 1.0),
    vec4(1.0, 1.0, 1.0, 0.0),
    vec4(1.0, 1.0, 1.0, 0.0),
    vec4(1.0, -1.0, 0.0, 0.0),
    vec4(-1.0, -1.0, 0.0, 1.0),
};

void main()
{
    vsTexCoords = cVertices[gl_VertexID].zw;
    gl_Position = vec4(cVertices[gl_VertexID].xy, 0.0, 1.0);
}
