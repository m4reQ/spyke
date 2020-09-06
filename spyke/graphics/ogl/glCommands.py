from ...enums import *

from OpenGL import GL

class GLCommand:
	@staticmethod
	def Clear(masks: ClearMask):
		GL.glClear(masks)
	
	@staticmethod
	def Viewport(x: int, y: int, width: int, height: int):
		GL.glViewport(x, y, width, height)
	
	@staticmethod
	def Scissor(x: int, y: int, width: int, height: int):
		GL.glScissor(x, y, width, height)
	
	@staticmethod
	def SetClearcolor(r: float, g: float, b: float):
		GL.glClearColor(r, g, b, 1.0)
	
	@staticmethod
	def Enable(cap: EnableCap):
		GL.glEnable(cap)
	
	@staticmethod
	def Disable(cap: EnableCap):
		GL.glDisable(cap)
	
	@staticmethod
	def AlphaTest(operator: AlphaOperator, value: float):
		GL.glAlphaFunc(operator, value)
	
	@staticmethod
	def BlendFunction(src: BlendFactor, dst: BlendFactor):
		GL.glBlendFunc(src, dst)
	
	@staticmethod
	def BlendFunctionSeparate(srcRgb: BlendFactor, dstRgb: BlendFactor, srcAlpha: BlendFactor, dstAlpha: BlendFactor):
		GL.glBlendFuncSeparate(srcRgb, dstRgb, srcAlpha, dstAlpha)
