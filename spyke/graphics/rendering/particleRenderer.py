#region Import
from .rendererComponent import RendererComponent
from .renderStats import RenderStats
from .renderBatch import RenderBatch
from ..shader import Shader
from ..buffers import StaticIndexBuffer, DynamicVertexBuffer
from ..vertexArray import VertexArray, VertexArrayLayout
from ..texturing.textureUtils import TextureHandle
from ..texturing.textureManager import TextureManager
from ...transform import Matrix4, GetQuadIndexData, TransformQuadVertices, Vector2
from ...enums import VertexAttribType, GLType, ShaderType
from ...utils import GL_FLOAT_SIZE
from ...debug import Log, LogLevel, Timer

from OpenGL import GL
#endregion

class ParticleRenderer(RendererComponent):
	MaxParticleCount = 100
	MaxVertexCount = MaxParticleCount * 1
	__VertexSize = (2 + 2 + 1 + 4 + 2 + 1) * GL_FLOAT_SIZE

	def __init__(self):
		self.shader = Shader()
		self.shader.AddStage(ShaderType.VertexShader, "spyke/graphics/shaderSources/particleVertex.glsl")
		self.shader.AddStage(ShaderType.GeometryShader, "spyke/graphics/shaderSources/particleGeometry.glsl")
		self.shader.AddStage(ShaderType.FragmentShader, "spyke/graphics/shaderSources/particleFragment.glsl")
		self.shader.Compile()
		
		self.ibo = StaticIndexBuffer(GetQuadIndexData(ParticleRenderer.MaxParticleCount * 6))
		self.vbo = DynamicVertexBuffer(ParticleRenderer.MaxVertexCount * ParticleRenderer.__VertexSize)
		self.vao = VertexArray(ParticleRenderer.__VertexSize)

		self.vbo.Bind()
		self.vao.Bind()
		self.vao.AddLayouts([
			VertexArrayLayout(self.shader.GetAttribLocation("aPosition"), 2, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aSize"), 2, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aRotation"), 1, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aColor"), 4, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTexCoord"), 2, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTexIdx"), 1, VertexAttribType.Float, False)])
		
		self.batches = []
		self.__viewProjection = Matrix4(1.0)
		self.renderStats = RenderStats()

		Log("Particle renderer initialized", LogLevel.Info)
	
	def RenderParticle(self, pos: Vector2, size: Vector2, rot: float, color: tuple, texHandle: TextureHandle):
		data = [pos.x, pos.y, size.x, size.y, rot, color[0], color[1], color[2], color[3], texHandle.U, texHandle.V, texHandle.Index]

		try:
			batch = next(x for x in self.batches if x.texarrayID == texHandle.TexarrayID and x.WouldAccept(len(data) * GL_FLOAT_SIZE))
		except StopIteration:
			batch = RenderBatch(ParticleRenderer.MaxVertexCount * ParticleRenderer.__VertexSize)
			batch.texarrayID = texHandle.TexarrayID
			self.batches.append(batch)
		
		batch.AddData(data)

		self.renderStats.VertexCount += 1
		batch.indexCount += 1

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

		GL.glDepthMask(False)

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

			GL.glDrawElements(GL.GL_POINTS, batch.indexCount, GLType.UnsignedInt, None)
			self.renderStats.DrawsCount += 1

			batch.Clear()
		
		GL.glDepthMask(True)
		
		self.renderStats.DrawTime = Timer.Stop()

	def GetStats(self) -> RenderStats:
		return self.renderStats