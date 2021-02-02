#region Import
from .renderStats import RenderStats
from .rendererComponent import RendererComponent
from .renderBatch import RenderBatch
from ..shader import Shader
from ..vertexArray import VertexArray
from ..buffers import VertexBuffer
from ...utils import GL_FLOAT_SIZE, Timer
from ...enums import VertexAttribType, ShaderType
from ...debugging import Log, LogLevel
from ...transform import Matrix4, Vector3

from OpenGL import GL
import glm
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
		self.vao.AddLayout(self.shader.GetAttribLocation("aPosition"), 3, GL.GL_FLOAT, False)
		self.vao.AddLayout(self.shader.GetAttribLocation("aColor"), 4, GL.GL_FLOAT, False)

		self.__batches = []

		Log("Line renderer initialized", LogLevel.Info)
	
	def EndScene(self):
		needsDraw = False
		for batch in self.__batches:
			needsDraw |= batch.dataSize != 0
			if needsDraw:
				self.__Flush(viewProjectionMatrix)
				return
	
	def __Flush(self):
		self.shader.Use()
		
		self.vbo.Bind()
		self.vao.Bind()

		for batch in self.__batches:
			self.vbo.AddData(batch.data, batch.dataSize)

			GL.glDrawArrays(GL.GL_LINES, 0, RenderStats.VertexCount)
			RenderStats.DrawsCount += 1

			batch.Clear()
	
	def Render(self, startPos: glm.vec3, endPos: glm.vec3, color: glm.vec4):
		data = [
			startPos.x, startPos.y, startPos.z, color.x, color.y, color.z, color.w,
			endPos.x, endPos.y, endPos.z, 		color.x, color.y, color.z, color.w]

		try:
			batch = next(x for x in self.__batches if x.WouldAccept(len(data) * GL_FLOAT_SIZE))
		except StopIteration:
			batch = RenderBatch(LineRenderer.MaxVertexCount * VERTEX_SIZE)
			self.__batches.append(batch)

		batch.AddData(data)
		
		RenderStats.QuadsCount += 1