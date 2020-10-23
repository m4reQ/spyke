from .renderStats import RenderStats
from .rendererComponent import RendererComponent
from .renderBatch import RenderBatch
from ..shader import Shader
from ..vertexArray import VertexArray, VertexArrayLayout
from ..buffers import DynamicVertexBuffer
from ...utils import GL_FLOAT_SIZE
from ...enums import GLType, VertexAttribType
from ...debug import Log, LogLevel, Timer

import glm
from OpenGL import GL

class LineRenderer(RendererComponent):
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

		self.__batches = []

		self.__viewProjection = glm.mat4(1.0)

		self.renderStats = RenderStats()

		Log("Line renderer initialized", LogLevel.Info)

	def BeginScene(self, viewProjection: glm.mat4, uniformName: str):
		self.__viewProjection = viewProjection
		self.__viewProjectionName = uniformName

		self.renderStats.Clear()
	
	def EndScene(self):
		needsDraw = False
		for batch in self.__batches:
			needsDraw |= batch.dataSize != 0
			if needsDraw:
				self.__Flush()
				return
	
	def __Flush(self):
		Timer.Start()

		self.shader.Use()
		self.shader.SetUniformMat4(self.__viewProjectionName, self.__viewProjection, False)

		self.vbo.Bind()
		self.vao.Bind()

		for batch in self.__batches:
			self.vbo.AddData(batch.data, batch.dataSize)

			GL.glDrawArrays(GL.GL_LINES, 0, self.renderStats.VertexCount)
			self.renderStats.DrawsCount += 1

			batch.Clear()
		

		self.renderStats.DrawTime = Timer.Stop()
	
	def Render(self, startPos: glm.vec3, endPos: glm.vec3, color: tuple):
		data = [
			startPos.x, startPos.y, startPos.z, color[0], color[1], color[2], color[3],
			endPos.x, endPos.y, endPos.z, color[0], color[1], color[2], color[3]]

		try:
			batch = next(x for x in self.__batches if x.WouldAccept(len(data) * GL_FLOAT_SIZE))
		except StopIteration:
			batch = RenderBatch(LineRenderer.MaxVertexCount * LineRenderer.__VertexSize)
			self.__batches.append(batch)

		batch.AddData(data)
		
		self.renderStats.VertexCount += 2
