from .renderStats import RenderStats
from ..shader import Shader
from ..buffers import VertexBuffer, Framebuffer, IndexBuffer
from ..vertexArray import VertexArray
from ...constants import _GL_FLOAT_SIZE, _NP_FLOAT
from ...debugging import Debug, LogLevel

from OpenGL import GL
import numpy as np
import glm

VERTEX_SIZE = (3 + 4 + 2) * _GL_FLOAT_SIZE
VERTEX_VERTEX_VALUES_COUNT = 3 + 4 + 2

VERTICES_PER_QUAD = 4

VERTEX_DATA_BUFFER_BINDING = 0

NORMAL_TEXTURE_SAMPLER_INDEX = 0
MULTISAMPLE_TEXTURE_SAMPLER_INDEX = 1

class PostRenderer(object):
	def __init__(self):
		self._vertexData = np.empty(VERTEX_VERTEX_VALUES_COUNT * VERTICES_PER_QUAD, dtype=_NP_FLOAT)

		self.shader = Shader()
		self.shader.AddStage(GL.GL_VERTEX_SHADER, "spyke/graphics/shaderSources/post.vert")
		self.shader.AddStage(GL.GL_FRAGMENT_SHADER, "spyke/graphics/shaderSources/post.frag")
		self.shader.Compile()

		self.vbo = VertexBuffer(VERTEX_SIZE * VERTICES_PER_QUAD * 1, memoryview(self._vertexData))
		self.ibo = IndexBuffer(IndexBuffer.CreateQuadIndices(1), GL.GL_UNSIGNED_BYTE)

		self.vao = VertexArray()
		self.vao.BindVertexBuffer(VERTEX_DATA_BUFFER_BINDING, self.vbo.ID, 0, VERTEX_SIZE)
		self.vao.BindElementBuffer(self.ibo.ID)

		self.vao.AddLayout(self.shader.GetAttribLocation("aPosition"), VERTEX_DATA_BUFFER_BINDING, 3, GL.GL_FLOAT, False)
		self.vao.AddLayout(self.shader.GetAttribLocation("aColor"), VERTEX_DATA_BUFFER_BINDING, 4, GL.GL_FLOAT, False)
		self.vao.AddLayout(self.shader.GetAttribLocation("aTexCoord"), VERTEX_DATA_BUFFER_BINDING, 2, GL.GL_FLOAT, False)

		
		self._samplesToRender = 0
		self._textureIdToRender = 0

		self.shader.Validate()
		Debug.GetGLError()
		Debug.Log("Post processing renderer initialized succesfully.", LogLevel.Info)

	def RenderFullscreen(self, framebuffer: Framebuffer, attachmentTextureId: int) -> None:
		color = framebuffer.specification.color
		self._vertexData[:self._vertexData.size] = (
			-1.0, -1.0, 0.0, color.x, color.y, color.z, color.w, 0.0, 0.0, 
			-1.0,  1.0, 0.0, color.x, color.y, color.z, color.w, 0.0, 1.0, 
			 1.0,  1.0, 0.0, color.x, color.y, color.z, color.w, 1.0, 1.0, 
			 1.0, -1.0, 0.0, color.x, color.y, color.z, color.w, 1.0, 0.0)
		
		self._samplesToRender = framebuffer.specification.samples
		self._textureIdToRender = attachmentTextureId

		self.__Flush()

	def __Flush(self):
		self.shader.Use()

		self.shader.SetUniform1i("uSamples", self._samplesToRender)

		sampler = MULTISAMPLE_TEXTURE_SAMPLER_INDEX if self._samplesToRender > 1 else NORMAL_TEXTURE_SAMPLER_INDEX
		GL.glBindTextureUnit(sampler, self._textureIdToRender)

		self.vbo.TransferData(self._vertexData.size * _GL_FLOAT_SIZE)
		
		self.vao.Bind()
		
		GL.glDrawElements(GL.GL_TRIANGLES, 6, self.ibo.Type, None)

		RenderStats.drawsCount += 1
		RenderStats.quadsCount += 1
		RenderStats.vertexCount += VERTICES_PER_QUAD