from ..shader import Shader
from ..buffers import DynamicVertexBuffer, StaticIndexBuffer
from ..vertexArray import VertexArray, VertexArrayLayout
from ...text.fontManager import FontManager
from ...text.font import Font
from ....utils import GetQuadIndexData, GL_FLOAT_SIZE
from ....enums import GLType, VertexAttribType
from ....debug import Log, LogLevel

import glm
from OpenGL import GL

class TextRenderer(object):
	MaxChars = 500
	MaxVertexCount = MaxChars * 4

	__VertexSize = (3 + 4 + 1 + 2) * GL_FLOAT_SIZE
	
	def __init__(self, shader: Shader):
		self.shader = shader

		self.vao = VertexArray(TextRenderer.__VertexSize)
		self.vbo = DynamicVertexBuffer(TextRenderer.MaxVertexCount * TextRenderer.__VertexSize)
		self.ibo = StaticIndexBuffer(GetQuadIndexData(TextRenderer.MaxChars))

		self.vbo.Bind()
		self.vao.Bind()
		self.vao.AddLayouts(
			[VertexArrayLayout(self.shader.GetAttribLocation("aPosition"), 	3, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aColor"), 		4, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTexCoord"), 	2, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTexIdx"), 	1, VertexAttribType.Float, False)])
		
		self.winSize = (1, 1)

		self.__vertexData = []
		self.__vertexCount = 0
		self.__indexCount = 0

		self.__viewProjection = glm.mat4(1.0)

		self.drawsCount = 0

		Log("Text renderer initialized", LogLevel.Info)

	def Resize(self, width: int, height: int):
		self.winSize = (width, height)

	def BeginScene(self, viewProjection: glm.mat4, uniformName: str):
		self.__viewProjection = viewProjection
		self.__viewProjectionName = uniformName

		self.drawsCount = 0
	
	def EndScene(self):
		if len(self.__vertexData) != 0:
			self.__Flush()

	def __Flush(self):
		self.shader.Use()

		self.shader.SetUniformMat4(self.__viewProjectionName, self.__viewProjection, False)

		FontManager.Use()

		self.vbo.Bind()
		self.vbo.AddData(self.__vertexData, len(self.__vertexData) * GL_FLOAT_SIZE)

		self.vao.Bind()

		self.ibo.Bind()

		GL.glDrawElements(GL.GL_TRIANGLES, self.__indexCount, GLType.UnsignedInt, None)

		self.__vertexData.clear()

		self.__vertexCount = 0
		self.__indexCount = 0

		self.drawsCount += 1

	def DrawText(self, pos: glm.vec3, color: tuple, font: Font, size: int, text: str):
		advanceSum = 0

		glyphSize = size / font.baseSize

		for char in text:
			if self.__vertexCount + 4 > TextRenderer.MaxVertexCount:
				self.__Flush()

			glyph = font.GetGlyph(ord(char))

			advance = advanceSum / self.winSize[0] * glyphSize

			width = glyph.Width / self.winSize[0] * glyphSize
			height = glyph.Height / self.winSize[1] * glyphSize

			xPos = pos.x + advance
			charData = [
				xPos, pos.y,                  pos[2], color[0], color[1], color[2], color[3], glyph.X, glyph.Y + glyph.TexHeight,					font.TextureIndex,
				xPos, pos.y + height,         pos[2], color[0], color[1], color[2], color[3], glyph.X, glyph.Y,										font.TextureIndex,
				xPos + width, pos.y + height, pos[2], color[0], color[1], color[2], color[3], glyph.X + glyph.TexWidth, glyph.Y,					font.TextureIndex,
				xPos + width, pos.y,          pos[2], color[0], color[1], color[2], color[3], glyph.X + glyph.TexWidth, glyph.Y + glyph.TexHeight, 	font.TextureIndex]
			
			advanceSum += glyph.Advance

			self.__vertexData.extend(charData)
			self.__vertexCount += 4
			self.__indexCount += 6