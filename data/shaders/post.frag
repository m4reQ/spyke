#version 450 core
in vec2 vTexCoord;

out vec4 Color;

uniform sampler2D uTexture;
uniform sampler2DMS uTextureMS;
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
    if (uSamples > 1)
        Color = textureMultisample(uTextureMS, vTexCoord, uSamples);
    else
        Color = texture(uTexture, vTexCoord);
}