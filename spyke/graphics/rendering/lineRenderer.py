from ..shader import Shader
from ..vertexArray import VertexArray, VertexArrayLayout
from ..buffers import DynamicVertexBuffer
from ...utils import GL_FLOAT_SIZE
from ...enums import GLType, VertexAttribType
from ...debug import Log, LogLevel

import glm
from OpenGL import GL

class LineRenderer(object):
	MaxLinesCount = 500
	MaxVertexCount = MaxLinesCount * 2

	__VertexSize = (3 + 4) * GL_FLOAT_SIZE

	def __init__(self, shader: Shader):
		self.shader = shader
		self.vao = VertexArray(LineRenderer.__VertexSize)
		self.vbo = DynamicVertexBuffer(LineRenderer.MaxVertexCount * LineRenderer.__VertexSize)

		self.vbo.Bind()
		self.vao.Bind()
		self.vao.AddLayouts(
			[VertexArrayLayout(self.shader.GetAttribLocation("aPosition"), 	3, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aColor"), 		4, VertexAttribType.Float, False)])

		self.__vertexCount = 0
		self.__vertexData = []

		self.__viewProjection = glm.mat4(1.0)

		self.drawsCount = 0

		Log("Line renderer initialized", LogLevel.Info)

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

		GL.glDrawArrays(GL.GL_LINES, 0, self.__vertexCount)

		self.__vertexData.clear()

		self.__vertexCount = 0

		self.drawsCount += 1
	
	def Render(self, item):
		if self.__vertexCount + 2 > LineRenderer.MaxVertexCount:
			self.__Flush()
		
		data = [
			item.StartPosition[0], item.StartPosition[1], item.StartPosition[2], item.Color[0], item.Color[1], item.Color[2], item.Color[3],
			item.EndPosition[0], item.EndPosition[1], item.EndPosition[2], item.Color[0], item.Color[1], item.Color[2], item.Color[3]]

		self.__vertexData.extend(data)
		
		self.__vertexCount += 2
