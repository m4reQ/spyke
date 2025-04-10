#version 450 core
#define MAX_LIGHTS_COUNT 32

layout(location=0) out vec4 outColor;

in vec2 vsTexCoords;

layout(binding = 1) uniform sampler2D uPositionTexture;
layout(binding = 2) uniform sampler2D uNormalTexture;
layout(binding = 3) uniform sampler2D uAlbedoSpecularTexture;

uniform vec3 uViewPos;
uniform uint uLightsCount;

struct Light
{
    vec4 color; // `A` component is the light's intensity
    vec3 position;
    // 4 - byte padding here
};

layout (std140, binding=1) uniform uLights
{
    Light lights[MAX_LIGHTS_COUNT];
};

void main()
{
    vec3 fragPos = texture(uPositionTexture, vsTexCoords).rgb;
    vec3 normal = texture(uNormalTexture, vsTexCoords).rgb;
    vec4 albedoSpecular = texture(uAlbedoSpecularTexture, vsTexCoords);
    vec3 albedo = albedoSpecular.rgb;
    float specular = albedoSpecular.a;

    vec3 lighting = albedo * 0.8;
    vec3 viewDir = normalize(uViewPos - fragPos);

    for (uint i = 0; i < uLightsCount; i++)
    {
        Light light = lights[i];

        vec3 lightDir = normalize(light.position - fragPos);
        vec3 diffuse = max(dot(normal, lightDir), 0.0) * albedo * light.color.rgb * light.color.a;

        lighting += diffuse;
    }

    outColor = vec4(lighting, 1.0);
}
