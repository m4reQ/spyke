from .renderStats import RenderStats
from ..shader import Shader
from ..buffers import VertexBuffer, Framebuffer
from ..vertexArray import VertexArray
from ...constants import _GL_FLOAT_SIZE
from ...debugging import Debug, LogLevel

from OpenGL import GL
import glm

VERTEX_SIZE = (3 + 4 + 2) * _GL_FLOAT_SIZE
VERTEX_DATA_VERTEX_SIZE = (3 + 2) * _GL_FLOAT_SIZE
INSTANCE_DATA_VERTEX_SIZE = 4 * _GL_FLOAT_SIZE

class PostRenderer(object):
	__VertexCount = 6

	QuadVertices = [
		glm.vec4(0.0, 0.0, 0.0, 1.0),
		glm.vec4(0.0, 1.0, 0.0, 1.0),
		glm.vec4(1.0, 1.0, 0.0, 1.0),
		glm.vec4(1.0, 0.0, 0.0, 1.0)]

	def __init__(self):
		self.shader = Shader()
		self.shader.AddStage(GL.GL_VERTEX_SHADER, "spyke/graphics/shaderSources/post.vert")
		self.shader.AddStage(GL.GL_FRAGMENT_SHADER, "spyke/graphics/shaderSources/post.frag")
		self.shader.Compile()

		self.vertexDataVbo = VertexBuffer(VERTEX_DATA_VERTEX_SIZE * PostRenderer.__VertexCount)
		self.instanceDataVbo = VertexBuffer(INSTANCE_DATA_VERTEX_SIZE)

		self.vao = VertexArray()
		self.vao.Bind()

		self.vertexDataVbo.Bind()
		self.vao.SetVertexSize(VERTEX_DATA_VERTEX_SIZE)
		self.vao.ClearVertexOffset()
		self.vao.AddLayout(self.shader.GetAttribLocation("aPosition"), 3, GL.GL_FLOAT, False)
		self.vao.AddLayout(self.shader.GetAttribLocation("aTexCoord"), 2, GL.GL_FLOAT, False)

		self.instanceDataVbo.Bind()
		self.vao.SetVertexSize(INSTANCE_DATA_VERTEX_SIZE)
		self.vao.ClearVertexOffset()
		self.vao.AddLayout(self.shader.GetAttribLocation("aColor"), 4, GL.GL_FLOAT, False, 1)
		
		self.shader.Validate()
		Debug.GetGLError()
		Debug.Log("Post processing renderer initialized succesfully.", LogLevel.Info)


	def Render(self, pos: glm.vec3, size: glm.vec3, rotation: glm.vec3, framebuffer: Framebuffer, passIdx = 0) -> None:
		transform = glm.translate(glm.mat4(1.0), pos)
		transform = glm.scale(transform, size)
		transform = glm.rotate(transform, rotation.x, glm.vec3(1.0, 0.0, 0.0))
		transform = glm.rotate(transform, rotation.y, glm.vec3(0.0, 1.0, 0.0))
		transform = glm.rotate(transform, rotation.z, glm.vec3(0.0, 0.0, 1.0))
		
		translatedVerts = [
			transform * PostRenderer.QuadVertices[0],
			transform * PostRenderer.QuadVertices[1],
			transform * PostRenderer.QuadVertices[2],
			transform * PostRenderer.QuadVertices[3]]

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
		
		self.vertexDataVbo.AddData(vertexData, len(vertexData) * _GL_FLOAT_SIZE)
		self.instanceDataVbo.AddData(instanceData, len(instanceData) * _GL_FLOAT_SIZE)

		GL.glDrawArraysInstanced(GL.GL_TRIANGLES, 0, 6, 1)

		RenderStats.drawsCount += 1
		RenderStats.quadsCount += 1