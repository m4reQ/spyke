BASIC_VERTEX = """
#version 450 core
layout(location = 0) in vec3 aPosition;
layout(location = 1) in vec4 aColor;
layout(location = 2) in vec2 aTexCoord;
layout(location = 3) in float aTexIdx;
layout(location = 4) in vec2 aTilingFactor;
out vec4 vColor;
out vec2 vTexCoord;
out float vTexIdx;
out vec2 vTilingFactor;
uniform mat4 uViewProjection;
void main(){
    vColor = aColor;
    vTexCoord = aTexCoord;
    vTexIdx = aTexIdx;
    vTilingFactor = aTilingFactor;
    gl_Position = uViewProjection * vec4(aPosition, 1.0f);}
"""

BASIC_FRAGMENT = """
#version 450 core
in vec4 vColor;
in vec2 vTexCoord;
in float vTexIdx;
in vec2 vTilingFactor;
uniform sampler2DArray uTextureArray;
out vec4 Color;
void main(){
    Color = texture(uTextureArray, vec3(vTexCoord.xy * vTilingFactor, vTexIdx)) * vColor;}
"""

TEXT_VERTEX = """
#version 450 core
layout(location = 0) in vec3 aPosition;
layout(location = 1) in vec4 aColor;
layout(location = 2) in vec2 aTexCoord;
layout(location = 3) in float aTexIdx;
uniform mat4 uViewProjection;
out vec4 vColor;
out vec2 vTexCoord;
out float vTexIdx;
void main(){
    vColor = aColor;
    vTexCoord = aTexCoord;
    vTexIdx = aTexIdx;
    gl_Position = uViewProjection * vec4(aPosition, 1.0f);    }
"""

TEXT_FRAGMENT = """
#version 450 core
in vec4 vColor;
in vec2 vTexCoord;
in float vTexIdx;
uniform sampler2DArray uTextures;
out vec4 Color;
void main(){
    Color = texture(uTextures, vec3(vTexCoord, vTexIdx)) * vColor;}
"""

LINE_VERTEX = """
#version 450 core
layout(location = 0) in vec3 aPosition;
layout(location = 1) in vec4 aColor;
out vec4 vColor;
uniform mat4 uViewProjection;
void main(){
    vColor = aColor;
    gl_Position = uViewProjection * vec4(aPosition, 1.0f);}
"""

LINE_FRAGMENT = """
#version 450 core
in vec4 vColor;
out vec4 Color;
void main(){
    Color = vColor;}
"""

POST_VERTEX = """
#version 450 core
layout(location = 0) in vec3 aPosition;
layout(location = 1) in vec4 aColor;
layout(location = 2) in vec2 aTexCoord;
layout(location = 3) in vec2 aTilingFactor;
out vec4 vColor;
out vec2 vTexCoord;
out vec2 vTilingFactor;
void main(){
    vColor = aColor;
    vTexCoord = aTexCoord;
    vTilingFactor = aTilingFactor;

    gl_Position = vec4(aPosition, 1.0f);}
"""

POST_FRAGMENT = """
#version 450 core
in vec4 vColor;
in vec2 vTexCoord;
in vec2 vTilingFactor;
layout(binding = 0) uniform sampler2D uTexture;
layout(binding = 1) uniform sampler2DMS uTextureMS;
uniform int uSamples;
out vec4 Color;
vec4 textureMultisample(sampler2DMS texSampler, vec2 coord, int samples){
    vec4 color;
    ivec2 texSize = textureSize(texSampler);
    ivec2 texCoord = ivec2(coord * texSize);
    for (int i = 0; i < samples; i++)
        color += texelFetch(texSampler, texCoord, i);
    color /= float(samples);
    return color;}
void main(){
    vec4 texColor;
    if (uSamples > 1)
        texColor = textureMultisample(uTextureMS, vTexCoord * vTilingFactor, uSamples);
    else
        texColor = texture(uTexture, vTexCoord * vTilingFactor);
    Color = texColor * vColor;}
"""