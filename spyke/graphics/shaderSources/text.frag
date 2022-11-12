#version 450 core

in FsIn
{
    vec4 color;
    vec2 texCoord;
    flat float texIdx;
    flat float entId;
} fsIn;

layout(location=0) out vec4 outColor;
layout(location=1) out int outEntId;

uniform sampler2D uTextures[15];

void main()
{
    vec4 texColor = fsIn.color;

    switch(int(fsIn.texIdx))
    {
        case 0: texColor *= vec4(1.0f, 1.0f, 1.0f, texture(uTextures[0], fsIn.texCoord).r); break;
        case 1: texColor *= vec4(1.0f, 1.0f, 1.0f, texture(uTextures[1], fsIn.texCoord).r); break;
        case 2: texColor *= vec4(1.0f, 1.0f, 1.0f, texture(uTextures[2], fsIn.texCoord).r); break;
        case 3: texColor *= vec4(1.0f, 1.0f, 1.0f, texture(uTextures[3], fsIn.texCoord).r); break;
        case 4: texColor *= vec4(1.0f, 1.0f, 1.0f, texture(uTextures[4], fsIn.texCoord).r); break;
        case 5: texColor *= vec4(1.0f, 1.0f, 1.0f, texture(uTextures[5], fsIn.texCoord).r); break;
        case 6: texColor *= vec4(1.0f, 1.0f, 1.0f, texture(uTextures[6], fsIn.texCoord).r); break;
        case 7: texColor *= vec4(1.0f, 1.0f, 1.0f, texture(uTextures[7], fsIn.texCoord).r); break;
        case 8: texColor *= vec4(1.0f, 1.0f, 1.0f, texture(uTextures[8], fsIn.texCoord).r); break;
        case 9: texColor *= vec4(1.0f, 1.0f, 1.0f, texture(uTextures[9], fsIn.texCoord).r); break;
        case 10: texColor *= vec4(1.0f, 1.0f, 1.0f, texture(uTextures[10], fsIn.texCoord).r); break;
        case 11: texColor *= vec4(1.0f, 1.0f, 1.0f, texture(uTextures[11], fsIn.texCoord).r); break;
        case 12: texColor *= vec4(1.0f, 1.0f, 1.0f, texture(uTextures[12], fsIn.texCoord).r); break;
        case 13: texColor *= vec4(1.0f, 1.0f, 1.0f, texture(uTextures[13], fsIn.texCoord).r); break;
        case 14: texColor *= vec4(1.0f, 1.0f, 1.0f, texture(uTextures[14], fsIn.texCoord).r); break;
    }

    outColor = texColor;
    outEntId = int(fsIn.entId);
}
