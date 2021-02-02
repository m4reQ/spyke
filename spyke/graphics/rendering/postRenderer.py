#region Import
from .renderStats import RenderStats
from ..shader import Shader
from ..buffers import VertexBuffer, Framebuffer
from ..vertexArray import VertexArray
from ...utils import GL_FLOAT_SIZE, Timer
from ...transform import Matrix4, CreateTransform3D, QuadVertices
from ...enums import VertexAttribType, ShaderType

from OpenGL import GL
import glm
#endregion

VERTEX_SIZE = (3 + 4 + 2) * GL_FLOAT_SIZE
VERTEX_DATA_VERTEX_SIZE = (3 + 2) * GL_FLOAT_SIZE
INSTANCE_DATA_VERTEX_SIZE = 4 * GL_FLOAT_SIZE

class PostRenderer(object):
	__VertexCount = 6

	def __init__(self):
		self.shader = Shader()
		self.shader.AddStage(GL.GL_VERTEX_SHADER, "spyke/graphics/shaderSources/post.vert")
		self.shader.AddStage(GL.GL_FRAGMENT_SHADER, "spyke/graphics/shaderSources/post.frag")
		self.shader.Compile()

		self.vertexDataVbo = VertexBuffer(VERTEX_DATA_VERTEX_SIZE * PostRenderer.__VertexCount)
		self.instanceDataVbo = VertexBuffer(INSTANCE_DATA_VERTEX_SIZE)

		self.vao = VertexArray()
		self.vao.Bind()

		self.vao.SetVertexSize(VERTEX_DATA_VERTEX_SIZE)
		self.vao.ClearVertexOffset()
		self.vertexDataVbo.Bind()
		self.vao.AddLayout(self.shader.GetAttribLocation("aPosition"), 3, GL.GL_FLOAT, False)
		self.vao.AddLayout(self.shader.GetAttribLocation("aTexCoord"), 2, GL.GL_FLOAT, False)

		self.vao.SetVertexSize(INSTANCE_DATA_VERTEX_SIZE)
		self.vao.ClearVertexOffset()
		self.instanceDataVbo.Bind()
		self.vao.AddLayout(self.shader.GetAttribLocation("aColor"), 4, GL.GL_FLOAT, False)

		self.vao.AddDivisor(self.shader.GetAttribLocation("aColor"), 1)

	def Render(self, pos: glm.vec3, size: glm.vec3, rotation: glm.vec3, framebuffer: Framebuffer, passIdx = 0) -> None:
		transform = CreateTransform3D(pos, size, rotation)
		
		translatedVerts = [
			transform * QuadVertices[0],
			transform * QuadVertices[1],
			transform * QuadVertices[2],
			transform * QuadVertices[3]]

		vertexData = [
			translatedVerts[0].x, translatedVerts[0].y, translatedVerts[0].z, 0.0, 0.0,
			translatedVerts[1].x, translatedVerts[1].y, translatedVerts[1].z, 0.0, 1.0,
			translatedVerts[2].x, translatedVerts[2].y, translatedVerts[2].z, 1.0, 1.0,
			translatedVerts[2].x, translatedVerts[2].y, translatedVerts[2].z, 1.0, 1.0,
			translatedVerts[3].x, translatedVerts[3].y, translatedVerts[3].z, 1.0, 0.0,
			translatedVerts[0].x, translatedVerts[0].y, translatedVerts[0].z, 0.0, 0.0]
		
		instanceData = [framebuffer.spec.color.x, framebuffer.spec.color.y, framebuffer.spec.color.z, framebuffer.spec.color.w]

		self.shader.Use()

		samples = framebuffer.spec.attachmentsSpecs[passIdx].samples
		attachment = framebuffer.GetColorAttachment(passIdx)

		self.shader.SetUniform1i("uSamples", samples)

		if samples > 1:
			GL.glBindTextureUnit(1, attachment)
			GL.glBindTexture(GL.GL_TEXTURE_2D_MULTISAMPLE, attachment)
		else:
			GL.glBindTextureUnit(0, attachment)
			GL.glBindTexture(GL.GL_TEXTURE_2D, attachment)

		self.vao.Bind()
		
		self.vertexDataVbo.AddDataDirect(vertexData, len(vertexData) * GL_FLOAT_SIZE)
		self.instanceDataVbo.AddDataDirect(instanceData, len(instanceData) * GL_FLOAT_SIZE)

		GL.glDrawArraysInstanced(GL.GL_TRIANGLES, 0, 6, 1)

		RenderStats.DrawsCount += 1
		RenderStats.QuadsCount += 1