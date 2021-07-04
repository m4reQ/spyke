#version 450 core
in vec4 vColor;
in vec2 vTexCoord;

out vec4 Color;

layout(binding = 0) uniform sampler2D uTexture;
layout(binding = 1) uniform sampler2DMS uTextureMS;
uniform int uSamples;

vec4 textureMultisample(sampler2DMS texSampler, vec2 coord, int samples)
{
    vec4 color;
    ivec2 texCoord = ivec2(coord * textureSize(texSampler));

    for (int i = 0; i < samples; i++)
        color += texelFetch(texSampler, texCoord, i);

    color /= float(samples);
    return color;
}

void main()
{
    vec4 texColor;

    if (uSamples > 1)
        texColor = textureMultisample(uTextureMS, vTexCoord, uSamples);
    else
        texColor = texture(uTexture, vTexCoord);
    
    Color = texColor * vColor;
}