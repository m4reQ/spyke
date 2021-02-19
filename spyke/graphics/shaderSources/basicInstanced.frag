#version 450 core

in vec4 vColor;
in vec2 vTexCoord;
in flat float vTexIdx;

layout(location = 0) out vec4 Color;

uniform sampler2D uTextures[32];

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
        case 15: texCol *= texture(uTextures[15], vTexCoord); break;
        case 16: texCol *= texture(uTextures[16], vTexCoord); break;
        case 17: texCol *= texture(uTextures[17], vTexCoord); break;
        case 18: texCol *= texture(uTextures[18], vTexCoord); break;
        case 19: texCol *= texture(uTextures[19], vTexCoord); break;
        case 20: texCol *= texture(uTextures[20], vTexCoord); break;
        case 21: texCol *= texture(uTextures[21], vTexCoord); break;
        case 22: texCol *= texture(uTextures[22], vTexCoord); break;
        case 23: texCol *= texture(uTextures[23], vTexCoord); break;
        case 24: texCol *= texture(uTextures[24], vTexCoord); break;
        case 25: texCol *= texture(uTextures[25], vTexCoord); break;
        case 26: texCol *= texture(uTextures[26], vTexCoord); break;
        case 27: texCol *= texture(uTextures[27], vTexCoord); break;
        case 28: texCol *= texture(uTextures[28], vTexCoord); break;
        case 29: texCol *= texture(uTextures[29], vTexCoord); break;
        case 30: texCol *= texture(uTextures[30], vTexCoord); break;
        case 31: texCol *= texture(uTextures[31], vTexCoord); break;
    }
    
    Color = texCol;
}