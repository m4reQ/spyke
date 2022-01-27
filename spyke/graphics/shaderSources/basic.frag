#version 450 core

in vec4 vColor;
in vec2 vTexCoord;
in flat float vTexIdx;
in flat float vEntId;

layout(location = 0) out vec4 Color;
layout(location = 1) out int EntityId;

uniform sampler2D uTextures[15];

void main()
{
    vec4 texCol = vColor;

    switch(int(vTexIdx))
    {
        case 0: texCol *= texture(uTextures[0], vTexCoord); break;
        case 1: texCol *= texture(uTextures[1], vTexCoord); break;
        case 2: texCol *= texture(uTextures[2], vTexCoord); break;
        case 3: texCol *= texture(uTextures[3], vTexCoord); break;
        case 4: texCol *= texture(uTextures[4], vTexCoord); break;
        case 5: texCol *= texture(uTextures[5], vTexCoord); break;
        case 6: texCol *= texture(uTextures[6], vTexCoord); break;
        case 7: texCol *= texture(uTextures[7], vTexCoord); break;
        case 8: texCol *= texture(uTextures[8], vTexCoord); break;
        case 9: texCol *= texture(uTextures[9], vTexCoord); break;
        case 10: texCol *= texture(uTextures[10], vTexCoord); break;
        case 11: texCol *= texture(uTextures[11], vTexCoord); break;
        case 12: texCol *= texture(uTextures[12], vTexCoord); break;
        case 13: texCol *= texture(uTextures[13], vTexCoord); break;
        case 14: texCol *= texture(uTextures[14], vTexCoord); break;
    }
    
    Color = texCol;
    EntityId = int(vEntId);
}