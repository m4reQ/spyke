#region Import
from .renderStats import RenderStats
from .renderBatch import RenderBatch
from .rendererComponent import RendererComponent
from .rendererSettings import RendererSettings
from ..shader import Shader
from ..buffers import VertexBuffer, IndexBuffer
from ..vertexArray import VertexArray, VertexArrayLayout
from ..text.font import Font
from ...managers import FontManager
from ...transform import CreateQuadIndices
from ...utils import GL_FLOAT_SIZE, Timer
from ...enums import GLType, VertexAttribType, ShaderType
from ...debug import Log, LogLevel

from OpenGL import GL
import glm
#endregion

VERTEX_SIZE = (3 + 4 + 1 + 2) * GL_FLOAT_SIZE

class TextRenderer(RendererComponent):
	def __init__(self):
		self.shader = Shader()
		self.shader.AddStage(ShaderType.VertexShader, "spyke/graphics/shaderSources/text.vert")
		self.shader.AddStage(ShaderType.FragmentShader, "spyke/graphics/shaderSources/text.frag")
		self.shader.Compile()

		self.vao = VertexArray()
		self.vbo = VertexBuffer(RendererSettings.MaxQuadsCount * 4 * VERTEX_SIZE)
		self.ibo = IndexBuffer(CreateQuadIndices(RendererSettings.MaxQuadsCount))

		self.vao.Bind()
		self.vao.SetVertexSize(VERTEX_SIZE)
		self.vbo.Bind()
		self.vao.AddLayouts(
			[VertexArrayLayout(self.shader.GetAttribLocation("aPosition"), 	3, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aColor"), 		4, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTexCoord"), 	2, VertexAttribType.Float, False),
			VertexArrayLayout(self.shader.GetAttribLocation("aTexIdx"), 	1, VertexAttribType.Float, False)])
		
		self.winSize = (1, 1)

		self.__batches = []

		Log("Text renderer initialized", LogLevel.Info)

	def Resize(self, width: int, height: int):
		self.winSize = (width, height)
	
	def EndScene(self) -> None:
		needsDraw = False
		for batch in self.__batches:
			needsDraw |= batch.dataSize != 0
			if needsDraw:
				self.__Flush()
				break

	def __Flush(self) -> None:
		Timer.Start()

		self.shader.Use()
		FontManager.Use()

		self.vbo.Bind()
		self.vao.Bind()
		self.ibo.Bind()

		for batch in self.__batches:
			self.vbo.AddData(batch.data, batch.dataSize)

			GL.glDrawElements(GL.GL_TRIANGLES, batch.indexCount, GL.GL_UNSIGNED_INT, None)
			RenderStats.DrawsCount += 1

			batch.Clear()

	def RenderText(self, pos: glm.vec3, color: glm.vec4, font: Font, size: int, text: str) -> None:
		advanceSum = 0

		glyphSize = size / font.baseSize

		try:
			batch = next(x for x in self.__batches if x.IsAccepting)
		except StopIteration:
			batch = RenderBatch(RendererSettings.MaxQuadsCount * 4 * VERTEX_SIZE)
			self.__batches.append(batch)

		for char in text:
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

			if not batch.WouldAccept(len(charData) * GL_FLOAT_SIZE):
				batch = RenderBatch(RendererSettings.MaxQuadsCount * 4 * VERTEX_SIZE)
				self.__batches.append(batch)
			
			batch.AddData(charData)
			
			batch.indexCount += 6
			RenderStats.QuadsCount += 1