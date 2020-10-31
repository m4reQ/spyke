#region Import
from .renderBatch import RenderBatch
from .renderStats import RenderStats
from .rendererComponent import RendererComponent
from ..shader import Shader
from ..vertexArray import VertexArray, VertexArrayLayout
from ..buffers import DynamicVertexBuffer, StaticIndexBuffer
from ..texturing.textureUtils import TextureHandle
from ..texturing.textureManager import TextureManager
from ...enums import VertexAttribType, GLType, ShaderType
from ...transform import TransformQuadVertices, GetQuadIndexData
from ...debug import Log, LogLevel, Timer
from ...utils import GL_FLOAT_SIZE

from OpenGL import GL
import glm
#endregion

class BasicRenderer(RendererComponent):
	MaxQuadCount = 100
	MaxVertexCount = MaxQuadCount * 4

	__VertexSize = (3 + 4 + 2 + 1 + 2) * GL_FLOAT_SIZE

	def __init__(self):
		self.shader = Shader()
		self.shader.AddStage(ShaderType.VertexShader, "spyke/graphics/shaderSources/basicVertex.glsl")
		self.shader.AddStage(ShaderType.FragmentShader, "spyke/graphics/shaderSources/basicFragment.glsl")
		self.shader.Compile()
		
		self.vao = VertexArray(BasicRenderer.__VertexSize)
		self.vbo = DynamicVertexBuffer(BasicRenderer.MaxVertexCount * BasicRenderer.__VertexSize)
		self.ibo = StaticIndexBuffer(GetQuadIndexData(BasicRenderer.MaxQuadCount))

		self.vbo.Bind()
		self.vao.Bind()
		self.vao.AddLayouts([
			VertexArrayLayout(self.shader.GetAttribLocation("aPosition"), 		3, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aColor"), 			4, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTexCoord"), 		2, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTexIdx"), 		1, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTilingFactor"), 	2, VertexAttribType.Float, False)])

		self.__batches = []

		self.__viewProjection = glm.mat4(1.0)

		self.renderStats = RenderStats()

		Log("2D renderer initialized", LogLevel.Info)
	
	def BeginScene(self, viewProjection: glm.mat4) -> None:
		self.__viewProjection = viewProjection

		self.renderStats.Clear()
	
	def EndScene(self) -> None:
		needsDraw = False
		for batch in self.__batches:
			needsDraw |= batch.dataSize != 0
			if needsDraw:
				self.__Flush()
				break

	def __Flush(self) -> None:
		Timer.Start()

		self.shader.Use()
		self.shader.SetUniformMat4("uViewProjection", self.__viewProjection, False)

		self.vbo.Bind()
		self.vao.Bind()
		self.ibo.Bind()

		for batch in self.__batches:
			if batch.texarrayID != -1:
				GL.glBindTexture(GL.GL_TEXTURE_2D_ARRAY, batch.texarrayID)
			else:
				TextureManager.GetArray(TextureManager.BlankArray).Bind()
				
			self.vbo.AddData(batch.data, batch.dataSize)

			GL.glDrawElements(GL.GL_TRIANGLES, batch.indexCount, GLType.UnsignedInt, None)
			self.renderStats.DrawsCount += 1

			batch.Clear()
		
		self.renderStats.DrawTime = Timer.Stop()
	
	def RenderQuad(self, transform: glm.mat4, color: tuple, texHandle: TextureHandle, tilingFactor: tuple):
		transformedVerts = TransformQuadVertices(transform.to_tuple())

		
		data = [
			transformedVerts[0].x, transformedVerts[0].y, transformedVerts[0].z, color[0], color[1], color[2], color[3], 0.0, texHandle.V, 			texHandle.Index, tilingFactor[0], tilingFactor[1],
			transformedVerts[1].x, transformedVerts[1].y, transformedVerts[1].z, color[0], color[1], color[2], color[3], 0.0, 0.0, 					texHandle.Index, tilingFactor[0], tilingFactor[1],
			transformedVerts[2].x, transformedVerts[2].y, transformedVerts[2].z, color[0], color[1], color[2], color[3], texHandle.U, 0.0, 			texHandle.Index, tilingFactor[0], tilingFactor[1],
			transformedVerts[3].x, transformedVerts[3].y, transformedVerts[3].z, color[0], color[1], color[2], color[3], texHandle.U, texHandle.V,		texHandle.Index, tilingFactor[0], tilingFactor[1]]

		try:
			batch = next(x for x in self.__batches if x.texarrayID == texHandle.TexarrayID and x.WouldAccept(len(data) * GL_FLOAT_SIZE))
		except StopIteration:
			batch = RenderBatch(BasicRenderer.MaxVertexCount * BasicRenderer.__VertexSize)
			batch.texarrayID = texHandle.TexarrayID
			self.__batches.append(batch)
	
		batch.AddData(data)
		
		self.renderStats.VertexCount += 4
		batch.indexCount += 6
	
	def GetStats(self) -> RenderStats:
		return self.renderStats