#region Import
from .renderStats import RenderStats
from ..shader import Shader
from ..buffers import DynamicVertexBuffer, Framebuffer
from ..vertexArray import VertexArray, VertexArrayLayout
from ...utils.memory import GL_FLOAT_SIZE
from ...transform import Matrix4, TransformQuadVertices
from ...enums import VertexAttribType, ShaderType
from ...debug import Timer

from OpenGL import GL
#endregion

class PostRenderer(object):
	__VertexSize = 3 * GL_FLOAT_SIZE

	def __init__(self):
		self.shader = Shader()
		self.shader.AddStage(ShaderType.VertexShader, "spyke/graphics/shaderSources/post.vert")
		self.shader.AddStage(ShaderType.FragmentShader, "spyke/graphics/shaderSources/post.frag")
		self.shader.Compile()

		self.__vbo = DynamicVertexBuffer(6 * PostRenderer.__VertexSize)
		self.__vao = VertexArray(PostRenderer.__VertexSize)
		self.__vbo.Bind()
		self.__vao.Bind()
		self.__vao.AddLayout(VertexArrayLayout(self.shader.GetAttribLocation("aPosition"), 3, VertexAttribType.Float, False))

		self.__renderStats = RenderStats()

		self.__viewProjection = Matrix4(1.0)
	
	def BeginScene(self, viewProjection: Matrix4) -> None:
		self.__viewProjection = viewProjection

		self.__renderStats.Clear()

	def EndScene(self) -> None:
		pass
	
	def Render(self, transform: Matrix4, framebuffer: Framebuffer, viewProjection: Matrix4) -> None:
		Timer.Start()

		translatedVerts = TransformQuadVertices(transform.to_tuple())

		data = [
			translatedVerts[0].x, translatedVerts[0].y, translatedVerts[0].z, 0.0, 1.0,
			translatedVerts[1].x, translatedVerts[1].y, translatedVerts[1].z, 0.0, 0.0,
			translatedVerts[2].x, translatedVerts[2].y, translatedVerts[2].z, 1.0, 0.0,
			translatedVerts[2].x, translatedVerts[2].y, translatedVerts[2].z, 1.0, 0.0,
			translatedVerts[3].x, translatedVerts[3].y, translatedVerts[3].z, 1.0, 1.0,
			translatedVerts[0].x, translatedVerts[0].y, translatedVerts[0].z, 0.0, 1.0]
		
		self.__shader.Use()
		self.__shader.SetUniformMat4("uViewProjection", self.__viewProjection, False)

		self.__vbo.Bind()
		self.__vbo.AddData(data, len(data) * GL_FLOAT_SIZE)
		GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)

		self.__renderStats.VertexCount += 6
		self.__renderStats.DrawTime = Timer.Stop()
	
	def GetStats(self) -> RenderStats:
		return self.__renderStats