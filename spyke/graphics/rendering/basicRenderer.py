#region Import
from .renderBatch import RenderBatch
from .renderStats import RenderStats
from .rendererComponent import RendererComponent
from .rendererSettings import RendererSettings
from ..shader import Shader
from ..vertexArray import VertexArray, VertexArrayLayout
from ..buffers import VertexBuffer, IndexBuffer
from ..texturing.textureUtils import TextureHandle
from ...managers import TextureManager
from ...transform import CreateQuadIndices, Matrix4, QuadVerticsFloat
from ...debug import Log, LogLevel
from ...utils import GL_FLOAT_SIZE

from OpenGL import GL
import glm
#endregion

VERTEX_SIZE = (3 + 4 + 2 + 1 + 2 + 16) * GL_FLOAT_SIZE
TRANSFORM_VERTEX_SIZE = 16 * GL_FLOAT_SIZE
POS_VERTEX_SIZE = 3 * GL_FLOAT_SIZE
DATA_VERTEX_SIZE = (4 + 2 + 1 + 2) * GL_FLOAT_SIZE

class BasicRenderer(RendererComponent):
	def __init__(self):
		self.shader = Shader()
		self.shader.AddStage(GL.GL_VERTEX_SHADER, "spyke/graphics/shaderSources/basicInstanced.vert")
		self.shader.AddStage(GL.GL_FRAGMENT_SHADER, "spyke/graphics/shaderSources/basicInstanced.frag")
		self.shader.Compile()
		
		self.posVbo = VertexBuffer(POS_VERTEX_SIZE * 4, GL.GL_STATIC_DRAW)
		self.vertexDataVbo = VertexBuffer(DATA_VERTEX_SIZE * RendererSettings.MaxQuadsCount * 4)
		self.transformVbo = VertexBuffer(TRANSFORM_VERTEX_SIZE * RendererSettings.MaxQuadsCount)

		self.vao = VertexArray()
		self.ibo = IndexBuffer(CreateQuadIndices(RendererSettings.MaxQuadsCount))

		self.vao.Bind()

		self.posVbo.Bind()
		self.vao.SetVertexSize(POS_VERTEX_SIZE)
		self.vao.ClearVertexOffset()
		self.posVbo.AddData(QuadVerticsFloat, len(QuadVerticsFloat) * GL_FLOAT_SIZE)
		self.vao.AddLayout(VertexArrayLayout(self.shader.GetAttribLocation("aPosition"), 3, GL.GL_FLOAT, False))

		self.vertexDataVbo.Bind()
		self.vao.SetVertexSize(DATA_VERTEX_SIZE)
		self.vao.ClearVertexOffset()
		self.vao.AddLayouts([
			VertexArrayLayout(self.shader.GetAttribLocation("aColor"), 			4, GL.GL_FLOAT, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTexCoord"), 		2, GL.GL_FLOAT, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTexIdx"), 		1, GL.GL_FLOAT, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTilingFactor"), 	2, GL.GL_FLOAT, False)])

		self.transformVbo.Bind()
		self.vao.SetVertexSize(TRANSFORM_VERTEX_SIZE)
		self.vao.ClearVertexOffset()

		idx = self.shader.GetAttribLocation(f"aTransform")
		for i in range(4):
			self.vao.AddLayout(VertexArrayLayout(idx + i, 4, GL.GL_FLOAT, False))
			self.vao.AddDivisor(idx + i, 1)

		self.__batches = []

		Log("2D renderer initialized", LogLevel.Info)
	
	def EndScene(self) -> None:
		needsDraw = False
		for batch in self.__batches:
			needsDraw |= len(batch.data) != 0
			if needsDraw:
				self.__Flush()
				break

	def __Flush(self) -> None:
		self.shader.Use()

		self.vao.Bind()
		self.ibo.Bind()

		for batch in self.__batches:
			TextureManager.GetArray(batch.texarrayID).Bind()

			self.vertexDataVbo.Bind()
			self.vertexDataVbo.AddData(batch.data, len(batch.data) * GL_FLOAT_SIZE)

			self.transformVbo.Bind()
			self.transformVbo.AddData(batch.transformData, len(batch.transformData) * GL_FLOAT_SIZE)

			GL.glDrawElementsInstanced(GL.GL_TRIANGLES, batch.indexCount, GL.GL_UNSIGNED_INT, None, batch.indexCount // 6)

			RenderStats.DrawsCount += 1

			batch.Clear()
		
	def RenderQuad(self, transform: Matrix4, color: glm.vec4, texHandle: TextureHandle, tilingFactor: glm.vec2):
		data = [
			color.x, color.y, color.z, color.w, 0.0, texHandle.V, 				texHandle.Index, tilingFactor.x, tilingFactor.y,
			color.x, color.y, color.z, color.w, 0.0, 0.0, 						texHandle.Index, tilingFactor.x, tilingFactor.y,
			color.x, color.y, color.z, color.w, texHandle.U, 0.0, 				texHandle.Index, tilingFactor.x, tilingFactor.y,
			color.x, color.y, color.z, color.w, texHandle.U, texHandle.V,		texHandle.Index, tilingFactor.x, tilingFactor.y]

		try:
			batch = next(x for x in self.__batches if x.texarrayID == texHandle.TexarrayID and x.WouldAccept(len(data) * GL_FLOAT_SIZE))
		except StopIteration:
			batch = RenderBatch(RendererSettings.MaxQuadsCount * 4 * VERTEX_SIZE)
			batch.texarrayID = texHandle.TexarrayID
			self.__batches.append(batch)
	
		batch.AddData(data)
		floatData = list(transform[0]) + list(transform[1]) + list(transform[2]) + list(transform[3])
		batch.AddTransformData(floatData)
		
		RenderStats.QuadsCount += 1
		batch.indexCount += 6