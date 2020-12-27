#region Import
from .renderStats import RenderStats
from .rendererComponent import RendererComponent
from .renderBatch import RenderBatch
from ..shader import Shader
from ..vertexArray import VertexArray, VertexArrayLayout
from ..buffers import VertexBuffer
from ...utils import GL_FLOAT_SIZE, Timer
from ...enums import VertexAttribType, ShaderType
from ...debug import Log, LogLevel
from ...transform import Matrix4, Vector3

from OpenGL import GL
#endregion

VERTEX_SIZE = (3 + 4) * GL_FLOAT_SIZE

class LineRenderer(RendererComponent):
	MaxLinesCount = 500
	MaxVertexCount = MaxLinesCount * 2

	def __init__(self):
		self.shader = Shader()
		self.shader.AddStage(ShaderType.VertexShader, "spyke/graphics/shaderSources/line.vert")
		self.shader.AddStage(ShaderType.FragmentShader, "spyke/graphics/shaderSources/line.frag")
		self.shader.Compile()

		self.vao = VertexArray()
		self.vbo = VertexBuffer(LineRenderer.MaxVertexCount * VERTEX_SIZE)

		self.vao.Bind()
		self.vao.SetVertexSize(VERTEX_SIZE)
		self.vbo.Bind()
		self.vao.AddLayouts(
			[VertexArrayLayout(self.shader.GetAttribLocation("aPosition"), 	3, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aColor"), 		4, VertexAttribType.Float, False)])

		self.__batches = []

		self.__viewProjection = Matrix4(1.0)

		self.renderStats = RenderStats()

		Log("Line renderer initialized", LogLevel.Info)

	def BeginScene(self, viewProjection: Matrix4):
		self.__viewProjection = viewProjection

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
		self.shader.SetUniformMat4("uViewProjection", self.__viewProjection, False)

		self.vbo.Bind()
		self.vao.Bind()

		for batch in self.__batches:
			self.vbo.AddData(batch.data, batch.dataSize)

			GL.glDrawArrays(GL.GL_LINES, 0, self.renderStats.VertexCount)
			self.renderStats.DrawsCount += 1

			batch.Clear()

		self.renderStats.DrawTime = Timer.Stop()
	
	def Render(self, startPos: Vector3, endPos: Vector3, color: tuple):
		data = [
			startPos.x, startPos.y, startPos.z, color[0], color[1], color[2], color[3],
			endPos.x, endPos.y, endPos.z, color[0], color[1], color[2], color[3]]

		try:
			batch = next(x for x in self.__batches if x.WouldAccept(len(data) * GL_FLOAT_SIZE))
		except StopIteration:
			batch = RenderBatch(LineRenderer.MaxVertexCount * VERTEX_SIZE)
			self.__batches.append(batch)

		batch.AddData(data)
		
		self.renderStats.QuadsCount += 1
	
	def GetStats(self) -> RenderStats:
		return self.renderStats
