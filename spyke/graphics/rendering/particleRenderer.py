from .rendererComponent import RendererComponent
from ..shading.shader import Shader
from ..buffers import StaticIndexBuffer, DynamicVertexBuffer
from ..vertexArray import VertexArray
from ..texturing.textureUtils import TextureHandle
from ...transform import Matrix4, GetQuadIndexData
from ...utils import GL_FLOAT_SIZE

class ParticleRenderer(RendererComponent):
    MaxParticleCount = 100
    MaxVertexCount = MaxParticleCount * 4
    __VertexSize = (3 + 4 + 2 + 1) * GL_FLOAT_SIZE

    def __init__(self):
        self.shader = Shader.FromFile("spyke/shaderSources/particleVertex.glsl", "spyke/shaderSources/particleFragment.glsl")
        
        self.ibo = StaticIndexBuffer(GetQuadIndexData(ParticleRenderer.MaxParticleCount * 6))
        self.vbo = DynamicVertexBuffer(ParticleRenderer.MaxVertexCount * ParticleRenderer.__VertexSize)
        self.vao = VertexArray(ParticleRenderer.__VertexSize)
    
    def RenderParticle(self, transform: Matrix4, color: tuple, texHandle: TextureHandle):
        pass

    def BeginScene(self):
        pass

    def EndScene(self):
        pass