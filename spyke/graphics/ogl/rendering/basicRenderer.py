from ..shader import Shader
from ..vertexArray import VertexArray, VertexArrayLayout
from ..buffers import DynamicVertexBuffer, StaticIndexBuffer
from ....enums import VertexAttribType, GLType
from ....transform import QuadVertices
from ....debug import Log, LogLevel
from ....utils import GetQuadIndexData, GetGLTypeSize, GL_FLOAT_SIZE

from OpenGL import GL
import glm

class BasicRenderer:
	MaxQuadCount = 100
	MaxVertexCount = MaxQuadCount * 4

	__VertexSize = (3 + 4 + 2 + 1 + 2) * GL_FLOAT_SIZE

	def __init__(self, shader: Shader):
		self.shader = shader
		self.vao = VertexArray(BasicRenderer.__VertexSize)
		self.vbo = DynamicVertexBuffer(BasicRenderer.MaxVertexCount * BasicRenderer.__VertexSize)
		self.ibo = StaticIndexBuffer(GetQuadIndexData(BasicRenderer.MaxQuadCount))

		self.vbo.Bind()
		self.vao.Bind()
		self.vao.AddLayouts(
			[VertexArrayLayout(self.shader.GetAttribLocation("aPosition"), 		3, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aColor"), 			4, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTexCoord"), 		2, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTexIdx"), 		1, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTilingFactor"), 	2, VertexAttribType.Float, False)])

		self.__vertexData = []
		self.__vertexCount = 0
		self.__indexCount = 0

		self.__viewProjection = glm.mat4(1.0)

		self.drawsCount = 0

		Log("2D renderer initialized", LogLevel.Info)
	
	def BeginScene(self, viewProjection: glm.mat4, uniformName: str):
		self.__viewProjection = viewProjection
		self.__viewProjectionName = uniformName

		self.drawsCount = 0
	
	def EndScene(self):
		if len(self.__vertexData) != 0:
			self.__Flush()

	def __Flush(self):
		self.shader.Use()

		self.shader.SetUniformMat4(self.__viewProjectionName, self.__viewProjection, False)

		self.vbo.Bind()
		self.vbo.AddData(self.__vertexData, len(self.__vertexData) * GL_FLOAT_SIZE)

		self.vao.Bind()

		self.ibo.Bind()

		GL.glDrawElements(GL.GL_TRIANGLES, self.__indexCount, GLType.UnsignedInt, None)

		self.__vertexData.clear()

		self.__vertexCount = 0
		self.__indexCount = 0

		self.drawsCount += 1
	
	def Render(self, item):
		if self.__vertexCount + 4 > BasicRenderer.MaxVertexCount:
			self.__Flush()
		
		translatedVerts = [
			item.Transform * QuadVertices[0],
			item.Transform * QuadVertices[1],
			item.Transform * QuadVertices[2],
			item.Transform * QuadVertices[3]]
		
		data = [
			translatedVerts[0].x, translatedVerts[0].y, translatedVerts[0].z, item.Color[0], item.Color[1], item.Color[2], item.Color[3], 0, item.TexCoord[1], 					item.TexId, item.TilingFactor[0], item.TilingFactor[1],
			translatedVerts[1].x, translatedVerts[1].y, translatedVerts[1].z, item.Color[0], item.Color[1], item.Color[2], item.Color[3], 0, 0, 								item.TexId, item.TilingFactor[0], item.TilingFactor[1],
			translatedVerts[2].x, translatedVerts[2].y, translatedVerts[2].z, item.Color[0], item.Color[1], item.Color[2], item.Color[3], item.TexCoord[0], 0, 					item.TexId, item.TilingFactor[0], item.TilingFactor[1],
			translatedVerts[3].x, translatedVerts[3].y, translatedVerts[3].z, item.Color[0], item.Color[1], item.Color[2], item.Color[3], item.TexCoord[0], item.TexCoord[1], 	item.TexId, item.TilingFactor[0], item.TilingFactor[1]]
		
		self.__vertexData.extend(data)
		
		self.__vertexCount += 4
		self.__indexCount += 6