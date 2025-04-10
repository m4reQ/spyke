#version 450 core

in vec2 vsTexCoord;

out vec4 fsColor;

uniform sampler2D uFramebufferTexture;

void main()
{
    fsColor = texture(uFramebufferTexture, vsTexCoord);
}
