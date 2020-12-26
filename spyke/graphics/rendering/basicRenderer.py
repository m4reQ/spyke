#region Import
from .renderBatch import RenderBatch
from .renderStats import RenderStats
from .rendererComponent import RendererComponent
from ..shader import Shader
from ..vertexArray import VertexArray, VertexArrayLayout
from ..buffers import VertexBuffer, IndexBuffer, UniformBuffer
from ..texturing.textureUtils import TextureHandle
from ...managers import TextureManager
from ...transform import CreateQuadIndices, Matrix4, QuadVerticsFloat
from ...debug import Log, LogLevel
from ...utils import GL_FLOAT_SIZE

from OpenGL import GL
#endregion

class BasicRenderer(RendererComponent):
	MaxQuadCount = 200
	MaxVertexCount = MaxQuadCount * 4

	__VertexSize = (3 + 4 + 2 + 1 + 2) * GL_FLOAT_SIZE

	def __init__(self):
		self.shader = Shader()
		self.shader.AddStage(GL.GL_VERTEX_SHADER, "spyke/graphics/shaderSources/basic.vert")
		self.shader.AddStage(GL.GL_FRAGMENT_SHADER, "spyke/graphics/shaderSources/basic.frag")
		self.shader.Compile()
		
		self.posVbo = VertexBuffer(4 * 3 * GL_FLOAT_SIZE)
		self.vertexDataVbo = VertexBuffer((BasicRenderer.__VertexSize - (3 * GL_FLOAT_SIZE)) * BasicRenderer.MaxVertexCount)

		self.vao = VertexArray(BasicRenderer.__VertexSize)
		self.ibo = IndexBuffer(CreateQuadIndices(BasicRenderer.MaxQuadCount))

		self.vao.Bind()

		self.posVbo.Bind()
		self.posVbo.AddData(QuadVerticsFloat, len(QuadVerticsFloat) * GL_FLOAT_SIZE)
		self.vao.AddLayout(VertexArrayLayout(self.shader.GetAttribLocation("aPosition"), 3, GL.GL_FLOAT, False))

		self.vertexDataVbo.Bind()
		self.vao.AddLayouts([
			VertexArrayLayout(self.shader.GetAttribLocation("aColor"), 			4, GL.GL_FLOAT, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTexCoord"), 		2, GL.GL_FLOAT, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTexIdx"), 		1, GL.GL_FLOAT, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTilingFactor"), 	2, GL.GL_FLOAT, False)])

		self.ubo = UniformBuffer(BasicRenderer.MaxQuadCount * 16 * GL_FLOAT_SIZE)
		self.ubo.Bind()
		self.ubo.BindToUniform(self.shader.GetUniformLocation("uTransform"))

		self.__batches = []
		self.__viewProjection = Matrix4(1.0)

		Log("2D renderer initialized", LogLevel.Info)
	
	def BeginScene(self, viewProjection: Matrix4) -> None:
		self.__viewProjection = viewProjection
	
	def EndScene(self) -> None:
		needsDraw = False
		for batch in self.__batches:
			needsDraw |= batch.dataSize != 0
			if needsDraw:
				self.__Flush()
				break

	def __Flush(self) -> None:
		self.shader.Use()
		self.shader.SetUniformMat4("uViewProjection", self.__viewProjection, False)

		self.vao.Bind()
		self.ibo.Bind()
		self.ubo.Bind()

		for batch in self.__batches:
			TextureManager.GetArray(batch.texarrayID).Bind()

			self.vertexDataVbo.AddData(batch.data, batch.dataSize)

			GL.glDrawElements(GL.GL_TRIANGLES, batch.indexCount, GL.GL_UNSIGNED_INT, None)

			RenderStats.DrawsCount += 1

			batch.Clear()
		
	def RenderQuad(self, transform: Matrix4, color: tuple, texHandle: TextureHandle, tilingFactor: tuple):
		data = [
			color[0], color[1], color[2], color[3], 0.0, texHandle.V, 				texHandle.Index, tilingFactor[0], tilingFactor[1],
			color[0], color[1], color[2], color[3], 0.0, 0.0, 						texHandle.Index, tilingFactor[0], tilingFactor[1],
			color[0], color[1], color[2], color[3], texHandle.U, 0.0, 				texHandle.Index, tilingFactor[0], tilingFactor[1],
			color[0], color[1], color[2], color[3], texHandle.U, texHandle.V,		texHandle.Index, tilingFactor[0], tilingFactor[1]]

		try:
			batch = next(x for x in self.__batches if x.texarrayID == texHandle.TexarrayID and x.WouldAccept(len(data) * GL_FLOAT_SIZE))
		except StopIteration:
			batch = RenderBatch(BasicRenderer.MaxVertexCount * BasicRenderer.__VertexSize)
			batch.texarrayID = texHandle.TexarrayID
			self.__batches.append(batch)
	
		batch.AddData(data)
		batch.AddTransformData(list(transform))
		
		RenderStats.QuadsCount += 1
		batch.indexCount += 6