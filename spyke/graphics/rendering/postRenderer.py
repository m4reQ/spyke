#region Import
from .renderStats import RenderStats
from .renderTarget import RenderTarget
from ..shader import Shader
from ..buffers import VertexBuffer, Framebuffer
from ..vertexArray import VertexArray, VertexArrayLayout
from ...utils import GL_FLOAT_SIZE, Timer
from ...transform import Matrix4, TransformQuadVertices
from ...enums import VertexAttribType, ShaderType

from OpenGL import GL
import glm
#endregion

VERTEX_SIZE = (3 + 4 + 2) * GL_FLOAT_SIZE

class PostRenderer(object):
	def __init__(self):
		self.shader = Shader()
		self.shader.AddStage(ShaderType.VertexShader, "spyke/graphics/shaderSources/post.vert")
		self.shader.AddStage(ShaderType.FragmentShader, "spyke/graphics/shaderSources/post.frag")
		self.shader.Compile()

		self.__vao = VertexArray()
		self.__vbo = VertexBuffer(6 * VERTEX_SIZE)
		
		self.__vao.Bind()
		self.__vbo.Bind()
		self.__vao.AddLayout(VertexArrayLayout(self.shader.GetAttribLocation("aPosition"), 3, VertexAttribType.Float, False))
		self.__vao.AddLayout(VertexArrayLayout(self.shader.GetAttribLocation("aColor"), 4, VertexAttribType.Float, False))
		self.__vao.AddLayout(VertexArrayLayout(self.shader.GetAttribLocation("aTexCoord"), 2, VertexAttribType.Float, False))

		self.BeginScene = lambda *_, **__: None
		self.EndScene = lambda *_, **__: None
	
	def Render(self, transform: Matrix4, renderTarget: RenderTarget) -> None:
		Timer.Start()

		translatedVerts = TransformQuadVertices(transform.to_tuple())

		color = renderTarget.Framebuffer.Spec.Color

		data = [
			translatedVerts[0].x, translatedVerts[0].y, translatedVerts[0].z, color.x, color.y, color.z, color.w, 0.0, 0.0,
			translatedVerts[1].x, translatedVerts[1].y, translatedVerts[1].z, color.x, color.y, color.z, color.w, 0.0, 1.0,
			translatedVerts[2].x, translatedVerts[2].y, translatedVerts[2].z, color.x, color.y, color.z, color.w, 1.0, 1.0,
			translatedVerts[2].x, translatedVerts[2].y, translatedVerts[2].z, color.x, color.y, color.z, color.w, 1.0, 1.0,
			translatedVerts[3].x, translatedVerts[3].y, translatedVerts[3].z, color.x, color.y, color.z, color.w, 1.0, 0.0,
			translatedVerts[0].x, translatedVerts[0].y, translatedVerts[0].z, color.x, color.y, color.z, color.w, 0.0, 0.0]
		
		self.shader.Use()
		self.shader.SetUniform1i("uSamples", renderTarget.Framebuffer.Spec.Samples)

		if renderTarget.Framebuffer.Spec.Samples > 1:
			GL.glBindTextureUnit(1, renderTarget.Framebuffer.ColorAttachment)
			GL.glBindTexture(GL.GL_TEXTURE_2D_MULTISAMPLE, renderTarget.Framebuffer.ColorAttachment)
		else:
			GL.glBindTextureUnit(0, renderTarget.Framebuffer.ColorAttachment)
			GL.glBindTexture(GL.GL_TEXTURE_2D, renderTarget.Framebuffer.ColorAttachment)

		self.__vbo.Bind()
		self.__vao.Bind()

		self.__vbo.AddData(data, len(data) * GL_FLOAT_SIZE)

		#GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, 0)

		#GL.glDisable(GL.GL_DEPTH_TEST)
		GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)
		#GL.glEnable(GL.GL_DEPTH_TEST)

		RenderStats.QuadsCount += 1
		RenderStats.DrawTime = Timer.Stop()
	
	def GetStats(self) -> RenderStats:
		return RenderStats