#region Import
from .rendererComponent import RendererComponent
from .renderStats import RenderStats
from .renderBatch import RenderBatch
from ..shading.shader import Shader
from ..buffers import StaticIndexBuffer, DynamicVertexBuffer
from ..vertexArray import VertexArray, VertexArrayLayout
from ..texturing.textureUtils import TextureHandle
from ..texturing.textureManager import TextureManager
from ...transform import Matrix4, GetQuadIndexData, TransformQuadVertices
from ...enums import VertexAttribType, GLType
from ...utils import GL_FLOAT_SIZE
from ...debug import Log, LogLevel, Timer

from OpenGL import GL
#endregion

class ParticleRenderer(RendererComponent):
    MaxParticleCount = 100
    MaxVertexCount = MaxParticleCount * 4
    __VertexSize = (3 + 4 + 2 + 1) * GL_FLOAT_SIZE

    def __init__(self):
        self.shader = Shader.FromFile("spyke/shaderSources/particleVertex.glsl", "spyke/shaderSources/particleFragment.glsl")
        
        self.ibo = StaticIndexBuffer(GetQuadIndexData(ParticleRenderer.MaxParticleCount * 6))
        self.vbo = DynamicVertexBuffer(ParticleRenderer.MaxVertexCount * ParticleRenderer.__VertexSize)
        self.vao = VertexArray(ParticleRenderer.__VertexSize)

        self.vbo.Bind()
        self.vao.Bind()
        self.vao.AddLayouts([
            VertexArrayLayout(self.shader.GetAttribLocation("aPosition"), 3, VertexAttribType.Float, False),
            VertexArrayLayout(self.shader.GetAttribLocation("aColor"), 4, VertexAttribType.Float, False),
            VertexArrayLayout(self.shader.GetAttribLocation("aTexCoord"), 2, VertexAttribType.Float, False),
            VertexArrayLayout(self.shader.GetAttribLocation("aTexIdx"), 1, VertexAttribType.Float, False)])
        
        self.batches = []
        self.__viewProjection = Matrix4(1.0)
        self.renderStats = RenderStats()

        Log("Particle renderer initialized", LogLevel.Info)
    
    def RenderParticle(self, transform: Matrix4, color: tuple, texHandle: TextureHandle):
        transformedVerts = TransformQuadVertices(transform.to_tuple())

        data = [
            transformedVerts[0].x, transformedVerts[0].y, transformedVerts[0].z, color[0], color[1], color[2], color[3], 0.0, texHandle.V,          texHandle.Index,
            transformedVerts[1].x, transformedVerts[1].y, transformedVerts[1].z, color[0], color[1], color[2], color[3], 0.0, 0.0,                  texHandle.Index,
            transformedVerts[2].x, transformedVerts[2].y, transformedVerts[2].z, color[0], color[1], color[2], color[3], texHandle.U, 0.0,          texHandle.Index,
            transformedVerts[3].x, transformedVerts[3].y, transformedVerts[3].z, color[0], color[1], color[2], color[3], texHandle.U, texHandle.V,  texHandle.Index]

        try:
            batch = next(x for x in self.batches if x.texarrayID == texHandle.TexarrayID and x.WouldAccept(len(data) * GL_FLOAT_SIZE))
        except StopIteration:
            batch = RenderBatch(ParticleRenderer.MaxVertexCount * ParticleRenderer.__VertexSize)
            batch.texarrayID = texHandle.TexarrayID
            self.batches.append(batch)
        
        batch.AddData(data)

        self.renderStats.VertexCount += 4
        batch.indexCount += 6

    def BeginScene(self, viewProjection: Matrix4) -> None:
        self.__viewProjection = viewProjection
        self.renderStats.Clear()

    def EndScene(self) -> None:
        needsDraw = False
        for batch in self.batches:
            needsDraw |= batch.dataSize != 0
            if needsDraw:
                self.__Flush()
                return
    
    def __Flush(self):
        Timer.Start()

        self.shader.Use()
        self.shader.SetUniformMat4("uViewProjection", self.__viewProjection, False)

        self.vbo.Bind()
        self.vao.Bind()
        self.ibo.Bind()

        for batch in self.batches:
            if batch.texarrayID != -1:
                GL.glBindTexture(GL.GL_TEXTURE_2D_ARRAY, batch.texarrayID)
            else:
                TextureManager.GetArray(TextureManager.BlankArray).Bind()

            self.vbo.AddData(batch.data, batch.dataSize)

            GL.glDrawElements(GL.GL_TRIANGLES, batch.indexCount, GLType.UnsignedInt, None)
            self.renderStats.DrawsCount += 1

            batch.Clear()
        
        self.renderStats.DrawTime = Timer.Stop()

    def GetStats(self) -> RenderStats:
        return self.renderStats