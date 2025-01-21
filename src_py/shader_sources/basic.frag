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

uniform sampler2D uTextures[16];

void main()
{
    // vec4 texColor = fsIn.color;

    // switch(int(fsIn.texIdx))
    // {
    //     case 0: texColor *= texture(uTextures[0], fsIn.texCoord); break;
    //     case 1: texColor *= texture(uTextures[1], fsIn.texCoord); break;
    //     case 2: texColor *= texture(uTextures[2], fsIn.texCoord); break;
    //     case 3: texColor *= texture(uTextures[3], fsIn.texCoord); break;
    //     case 4: texColor *= texture(uTextures[4], fsIn.texCoord); break;
    //     case 5: texColor *= texture(uTextures[5], fsIn.texCoord); break;
    //     case 6: texColor *= texture(uTextures[6], fsIn.texCoord); break;
    //     case 7: texColor *= texture(uTextures[7], fsIn.texCoord); break;
    //     case 8: texColor *= texture(uTextures[8], fsIn.texCoord); break;
    //     case 9: texColor *= texture(uTextures[9], fsIn.texCoord); break;
    //     case 10: texColor *= texture(uTextures[10], fsIn.texCoord); break;
    //     case 11: texColor *= texture(uTextures[11], fsIn.texCoord); break;
    //     case 12: texColor *= texture(uTextures[12], fsIn.texCoord); break;
    //     case 13: texColor *= texture(uTextures[13], fsIn.texCoord); break;
    //     case 14: texColor *= texture(uTextures[14], fsIn.texCoord); break;
    //     case 15: texColor *= texture(uTextures[15], fsIn.texCoord); break;
    // }

    outColor = texture(uTextures[int(fsIn.texIdx)], fsIn.texCoord) * fsIn.color;
    outEntId = int(fsIn.entId);
}
