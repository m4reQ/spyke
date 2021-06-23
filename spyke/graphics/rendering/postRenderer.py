from .renderStats import RenderStats
from ..shader import Shader
from ..buffers import VertexBuffer, Framebuffer, IndexBuffer
from ..vertexArray import VertexArray
from ...constants import _GL_FLOAT_SIZE
from ...debugging import Debug, LogLevel

from OpenGL import GL
import glm

VERTEX_SIZE = (3 + 4 + 2) * _GL_FLOAT_SIZE

VERTICES_PER_QUAD = 4

VERTEX_DATA_BUFFER_BINDING = 0

class PostRenderer(object):
	__VertexCount = 4

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

		self.vbo = VertexBuffer(VERTEX_SIZE * PostRenderer.__VertexCount)
		self.ibo = IndexBuffer(IndexBuffer.CreateQuadIndices(1), GL.GL_UNSIGNED_BYTE)

		self.vao = VertexArray()
		self.vao.BindVertexBuffer(VERTEX_DATA_BUFFER_BINDING, self.vbo.ID, 0, VERTEX_SIZE)
		self.vao.BindElementBuffer(self.ibo.ID)

		self.vao.AddLayout(self.shader.GetAttribLocation("aPosition"), VERTEX_DATA_BUFFER_BINDING, 3, GL.GL_FLOAT, False)
		self.vao.AddLayout(self.shader.GetAttribLocation("aColor"), VERTEX_DATA_BUFFER_BINDING, 4, GL.GL_FLOAT, False)
		self.vao.AddLayout(self.shader.GetAttribLocation("aTexCoord"), VERTEX_DATA_BUFFER_BINDING, 2, GL.GL_FLOAT, False)

		self._vertexData = []
		self._samplesToRender = 0
		self._attachmentIdToRender = 0

		self.shader.Validate()
		Debug.GetGLError()
		Debug.Log("Post processing renderer initialized succesfully.", LogLevel.Info)

	def RenderFullscreen(self, framebuffer: Framebuffer, passIdx=0) -> None:
		self._vertexData = [
			0.0, 0.0, 0.0, 0.0, 0.0, framebuffer.spec.color.x, framebuffer.spec.color.y, framebuffer.spec.color.z, framebuffer.spec.color.w,
			0.0, 1.0, 0.0, 0.0, 1.0, framebuffer.spec.color.x, framebuffer.spec.color.y, framebuffer.spec.color.z, framebuffer.spec.color.w,
			1.0, 1.0, 0.0, 1.0, 1.0, framebuffer.spec.color.x, framebuffer.spec.color.y, framebuffer.spec.color.z, framebuffer.spec.color.w,
			1.0, 0.0, 0.0, 1.0, 0.0, framebuffer.spec.color.x, framebuffer.spec.color.y, framebuffer.spec.color.z, framebuffer.spec.color.w]
		
		self._samplesToRender = framebuffer.spec.attachmentsSpecs[passIdx].samples
		self._attachmentIdToRender = framebuffer.GetColorAttachment(passIdx)

		self.__Flush()

	def Render(self, pos: glm.vec3, size: glm.vec3, rotation: glm.vec3, framebuffer: Framebuffer, passIdx = 0) -> None:
		transform = glm.translate(glm.mat4(1.0), pos)
		transform = glm.rotate(transform, rotation.x, glm.vec3(1.0, 0.0, 0.0))
		transform = glm.rotate(transform, rotation.y, glm.vec3(0.0, 1.0, 0.0))
		transform = glm.rotate(transform, rotation.z, glm.vec3(0.0, 0.0, 1.0))
		transform = glm.scale(transform, size)
		
		translatedVerts = [
			transform * PostRenderer.QuadVertices[0],
			transform * PostRenderer.QuadVertices[1],
			transform * PostRenderer.QuadVertices[2],
			transform * PostRenderer.QuadVertices[3]]

		self._vertexData = [
			translatedVerts[0].x, translatedVerts[0].y, translatedVerts[0].z, 0.0, 0.0, framebuffer.spec.color.x, framebuffer.spec.color.y, framebuffer.spec.color.z, framebuffer.spec.color.w,
			translatedVerts[1].x, translatedVerts[1].y, translatedVerts[1].z, 0.0, 1.0, framebuffer.spec.color.x, framebuffer.spec.color.y, framebuffer.spec.color.z, framebuffer.spec.color.w,
			translatedVerts[2].x, translatedVerts[2].y, translatedVerts[2].z, 1.0, 1.0, framebuffer.spec.color.x, framebuffer.spec.color.y, framebuffer.spec.color.z, framebuffer.spec.color.w,
			translatedVerts[3].x, translatedVerts[3].y, translatedVerts[3].z, 1.0, 0.0, framebuffer.spec.color.x, framebuffer.spec.color.y, framebuffer.spec.color.z, framebuffer.spec.color.w]
		
		self._samplesToRender = framebuffer.spec.attachmentsSpecs[passIdx].samples
		self._attachmentIdToRender = framebuffer.GetColorAttachment(passIdx)

		self.__Flush()

	def __Flush(self):
		self.shader.Use()

		self.shader.SetUniform1i("uSamples", self._samplesToRender)

		if self._samplesToRender > 1:
			GL.glBindTextureUnit(1, self._attachmentIdToRender)
			GL.glBindTexture(GL.GL_TEXTURE_2D_MULTISAMPLE, self._attachmentIdToRender)
		else:
			GL.glBindTextureUnit(0, self._attachmentIdToRender)
			GL.glBindTexture(GL.GL_TEXTURE_2D, self._attachmentIdToRender)

		self.vbo.AddData(self._vertexData, len(self._vertexData) * _GL_FLOAT_SIZE)
		
		self.vao.Bind()
		
		GL.glDrawElements(GL.GL_TRIANGLES, VERTICES_PER_QUAD, self.ibo.Type, None)

		RenderStats.drawsCount += 1
		RenderStats.quadsCount += 1
		RenderStats.vertexCount += VERTICES_PER_QUAD