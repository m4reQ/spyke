from ...enums import *

from OpenGL import GL

class GLCommand:
	def Clear(masks: ClearMask):
		GL.glClear(masks)
	
	def Hint(hint: int, value: int):
		GL.glHint(hint, value)
	
	def Viewport(x: int, y: int, width: int, height: int):
		GL.glViewport(x, y, width, height)
	
	def Scissor(x: int, y: int, width: int, height: int):
		GL.glScissor(x, y, width, height)
	
	def SetClearcolor(r: float, g: float, b: float):
		GL.glClearColor(r, g, b, 1.0)
	
	def Enable(cap: EnableCap):
		GL.glEnable(cap)
	
	def Disable(cap: EnableCap):
		GL.glDisable(cap)
	
	def AlphaTest(operator: AlphaOperator, value: float):
		GL.glAlphaFunc(operator, value)
	
	def BlendFunction(src: BlendFactor, dst: BlendFactor):
		GL.glBlendFunc(src, dst)
	
	def BlendFunctionSeparate(srcRgb: BlendFactor, dstRgb: BlendFactor, srcAlpha: BlendFactor, dstAlpha: BlendFactor):
		GL.glBlendFuncSeparate(srcRgb, dstRgb, srcAlpha, dstAlpha)
	
	def DepthMask(value: bool):
		GL.glDepthMask(value)