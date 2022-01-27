#version 450 core

in FsIn
{
    vec4 color;
    vec2 texCoords;
    flat float texIndex;
    flat float entityId;
} fsIn;

layout(location = 0) out vec4 color;
layout(location = 1) out int entityId;

uniform sampler2D uTextures[15];

void main()
{
    vec4 texColor = fsIn.color;

    switch(int(fsIn.texIndex))
    {
        case 0: texColor *= texture(uTextures[0], fsIn.texCoords); break;
        case 1: texColor *= texture(uTextures[1], fsIn.texCoords); break;
        case 2: texColor *= texture(uTextures[2], fsIn.texCoords); break;
        case 3: texColor *= texture(uTextures[3], fsIn.texCoords); break;
        case 4: texColor *= texture(uTextures[4], fsIn.texCoords); break;
        case 5: texColor *= texture(uTextures[5], fsIn.texCoords); break;
        case 6: texColor *= texture(uTextures[6], fsIn.texCoords); break;
        case 7: texColor *= texture(uTextures[7], fsIn.texCoords); break;
        case 8: texColor *= texture(uTextures[8], fsIn.texCoords); break;
        case 9: texColor *= texture(uTextures[9], fsIn.texCoords); break;
        case 10: texColor *= texture(uTextures[10], fsIn.texCoords); break;
        case 11: texColor *= texture(uTextures[11], fsIn.texCoords); break;
        case 12: texColor *= texture(uTextures[12], fsIn.texCoords); break;
        case 13: texColor *= texture(uTextures[13], fsIn.texCoords); break;
        case 14: texColor *= texture(uTextures[14], fsIn.texCoords); break;
    }
    
    color = texColor;
    entityId = int(fsIn.entityId);
}