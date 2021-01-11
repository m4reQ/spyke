#region Import
from .renderStats import RenderStats
from .renderTarget import RenderTarget
from ..shader import Shader
from ..buffers import VertexBuffer, Framebuffer
from ..vertexArray import VertexArray, VertexArrayLayout
from ...utils import GL_FLOAT_SIZE, Timer
from ...transform import Matrix4, CreateTransform3D
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
		self.__vao.SetVertexSize(VERTEX_SIZE)
		self.__vbo = VertexBuffer(6 * VERTEX_SIZE)
		
		self.__vao.Bind()
		self.__vbo.Bind()
		self.__vao.ClearVertexOffset()
		self.__vao.AddLayout(VertexArrayLayout(self.shader.GetAttribLocation("aPosition"), 3, VertexAttribType.Float, False))
		self.__vao.AddLayout(VertexArrayLayout(self.shader.GetAttribLocation("aColor"), 4, VertexAttribType.Float, False))
		self.__vao.AddLayout(VertexArrayLayout(self.shader.GetAttribLocation("aTexCoord"), 2, VertexAttribType.Float, False))
	
	def Render(self, pos: glm.vec3, size: glm.vec3, rotation: glm.vec3, framebuffer: Framebuffer) -> None:
		transform = CreateTransform3D(pos, size, rotation)
		translatedVerts = TransformQuadVertices(transform.to_tuple())

		color = framebuffer.Spec.Color

		data = [
			translatedVerts[0].x, translatedVerts[0].y, translatedVerts[0].z, color.x, color.y, color.z, color.w, 0.0, 0.0,
			translatedVerts[1].x, translatedVerts[1].y, translatedVerts[1].z, color.x, color.y, color.z, color.w, 0.0, 1.0,
			translatedVerts[2].x, translatedVerts[2].y, translatedVerts[2].z, color.x, color.y, color.z, color.w, 1.0, 1.0,
			translatedVerts[2].x, translatedVerts[2].y, translatedVerts[2].z, color.x, color.y, color.z, color.w, 1.0, 1.0,
			translatedVerts[3].x, translatedVerts[3].y, translatedVerts[3].z, color.x, color.y, color.z, color.w, 1.0, 0.0,
			translatedVerts[0].x, translatedVerts[0].y, translatedVerts[0].z, color.x, color.y, color.z, color.w, 0.0, 0.0]
		
		self.shader.Use()
		self.shader.SetUniform1i("uSamples", framebuffer.Spec.Samples)

		if framebuffer.Spec.Samples > 1:
			GL.glBindTextureUnit(1, framebuffer.ColorAttachment)
			GL.glBindTexture(GL.GL_TEXTURE_2D_MULTISAMPLE, framebuffer.ColorAttachment)
		else:
			GL.glBindTextureUnit(0, framebuffer.ColorAttachment)
			GL.glBindTexture(GL.GL_TEXTURE_2D, framebuffer.ColorAttachment)

		self.__vbo.Bind()
		self.__vao.Bind()

		self.__vbo.AddData(data, len(data) * GL_FLOAT_SIZE)

		#GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, 0)
		#GL.glDisable(GL.GL_DEPTH_TEST)
		GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)
		#GL.glEnable(GL.GL_DEPTH_TEST)

		RenderStats.QuadsCount += 1