#region Import
from .particle import Particle
from ..transform import CreateTransform3D
from ..debug import Log, LogLevel
from ..graphics import Font
from ..audio.sound import Sound
from ..graphics.texturing.textureUtils import TextureHandle, NoTexture
from ..enums import CameraType
from ..graphics.cameras import *

import glm
import random
#endregion

class ColorComponent(object):
	def __init__(self, *args):
		if isinstance(args[0], tuple):
			tup = args[0]
			self.R = tup[0]
			self.G = tup[1]
			self.B = tup[2]
			self.A = tup[3]
		elif len(args) == 4:
			self.R = args[0]
			self.G = args[1]
			self.B = args[2]
			self.A = args[3]
		else:
			raise TypeError("Invalid color arguments.")
	
	def __iter__(self):
		yield self.R
		yield self.G
		yield self.B
		yield self.A

class TransformComponent(object):
	def __init__(self, pos: glm.vec3, size: glm.vec2, rotation: float):
		self.__pos = pos
		self.__size = size
		self.__rot = rotation

		self.__posChanged = True
		self.__sizeChanged = True
		self.__rotChanged = True

		self.Matrix = glm.mat4(1.0)
		
		self.Recalculate()

		self.__transMatrix = glm.mat4(1.0)
		self.__rotMatrix = glm.mat4(1.0)
		self.__scaleMatrix = glm.mat4(1.0)
	
	def Recalculate(self):
		if all([self.__posChanged, self.__rotChanged, self.__sizeChanged]):
			self.Matrix = CreateTransform3D(self.__pos, self.__size, self.__rot)
			return
			
		if self.__posChanged:
			self.__transMatrix = glm.translate(glm.mat4(1.0), self.__pos)
		
		if self.__rotChanged:
			self.__rotMatrix = glm.rotate(glm.mat4(1.0), self.__rot, glm.vec3(0.0, 0.0, 1.0))
		
		if self.__sizeChanged:
			self.__scaleMatrix = glm.scale(glm.mat4(1.0), glm.vec3(self.__size.x, self.__size.y, 0.0))
		
		self.Matrix = self.__transMatrix * self.__rotMatrix * self.__scaleMatrix
	
	@property
	def ShouldRecalculate(self):
		return any([self.__posChanged, self.__sizeChanged, self.__rotChanged])

	@property
	def Position(self):
		return self.__pos
	
	@Position.setter
	def Position(self, val: glm.vec3):
		self.__pos = val
		self.__posChanged = True
	
	@property
	def Size(self):
		return self.__size
	
	@Size.setter
	def Size(self, val: glm.vec2):
		self.__size = val
		self.__sizeChanged = True
	
	@property
	def Rotation(self):
		return self.__rot
	
	@Rotation.setter
	def Rotation(self, val: float):
		self.__rot = val
		self.__rotChanged = True

class TextComponent(object):
	def __init__(self, text: str, size: int, font: Font):
		self.Text = text
		self.Size = size
		self.Font = font

class SpriteComponent(object):
	def __init__(self, textureHandle: TextureHandle, tilingFactor: tuple):
		self.TextureHandle = textureHandle
		self.TilingFactor = tilingFactor

class LineComponent(object):
	def __init__(self, startPos: glm.vec3, endPos: glm.vec3):
		self.StartPos = startPos
		self.EndPos = endPos

class ScriptComponent(object):
	@staticmethod
	def __defaultcaller(func, _object):
		def inner(*args, **kwargs):
			return func(_object, *args, **kwargs)

		return inner

	def __init__(self, file):
		self.file = file

		ext = __import__(self.file[:-3], globals(), locals())
		
		func = None
		for attr in dir(ext):
			if attr == "OnInit":
				func = getattr(ext, attr)
				break

		if not func or not callable(func):
			Log("OnInit function not found. Object members may not be properly initialized.", LogLevel.Warning)
		else:
			if callable(func):
				func(self)

		onProcessFound = False
		self.Process = lambda *args, **kwargs: None
		for attr in dir(ext):
			if attr == "OnInit":
				continue

			_func = getattr(ext, attr)
			if callable(_func):
				if attr[:2] == "__":
					attr = "_" + type(self).__name__ + attr
				setattr(self, attr, ScriptComponent.__defaultcaller(_func, self))
			
			if attr == "OnProcess":
				onProcessFound = True
		
		if onProcessFound:
			self.Process = self.__Process
		else:
			Log("OnProcess function not found. Process function won't be called.", LogLevel.Warning)
		
	def __Process(self, *args, **kwargs):
		self.OnProcess(*args, **kwargs)

class ParticleComponent(object):
	MaxCount = 50

	def __init__(self, basePos: glm.vec2, duration: float, maxCount: int):
		self.basePos = basePos
		self.baseRot = 0.0

		self.duration = duration
		self.velocity = glm.vec2(0.0)
		self.rotationVelocity = 0.0

		self._sizeBegin = glm.vec2(0.0)
		self._sizeEnd = glm.vec2(0.0)
		self.sizeChange = False

		self._colorBegin = glm.vec4(1.0)
		self._colorEnd = glm.vec4(1.0)
		self.colorChange = False

		self.randomizeMovement = False
		self.fadeOut = False

		self.texHandle = NoTexture

		self.maxCount = max(maxCount, ParticleComponent.MaxCount)
		
		self.particlePool = []
		for _ in range(self.maxCount):
			self.particlePool.append(Particle())
		self.activeParticleIdx = self.maxCount - 1
	
	def EmitParticle(self):
		particle = self.particlePool[self.activeParticleIdx]
		particle.isAlive = True

		particle.position = self.basePos
		
		if self.randomizeMovement:
			randomChange = random.random() - 0.5
		else:
			randomChange = 1.0
		
		particle.velocity = self.velocity * randomChange
		particle.rotation = self.baseRot * randomChange

		particle.color = self._colorBegin
		particle.size = self._sizeBegin

		particle.life = self.duration
		
		particle.texHandle = self.texHandle

		oldIndex = self.activeParticleIdx
		self.activeParticleIdx = (oldIndex - 1) % self.maxCount
	
	#region Setters
	@property
	def colorBegin(self):
		return self._colorBegin

	@colorBegin.setter
	def colorBegin(self, value):
		if value != self._colorBegin:
			self.colorChange = True
		else:
			self.colorChange = False
		
		self._colorBegin = value

	@property
	def colorEnd(self):
		return self._colorEnd
	
	@colorEnd.setter
	def colorEnd(self, value):
		if value != self._colorEnd:
			self.colorChange = True
		else:
			self.colorChange = False
		
		self._colorEnd = value
	
	@property
	def sizeBegin(self):
		return self._sizeBegin
	
	@sizeBegin.setter
	def sizeBegin(self, value):
		if value != self._sizeBegin:
			self.sizeChange = True
		else:
			self.sizeChange = False
		
		self._sizeBegin = value

	@property
	def sizeEnd(self):
		return self._sizeEnd
	
	@sizeEnd.setter
	def sizeEnd(self, value):
		if value != self._sizeEnd:
			self.sizeChange = True
		else:
			self.sizeChange = False
		
		self._sizeEnd = value
	#endregion

class AudioComponent(object):
	def __init__(self, filepath: str, looping: bool):
		self.Filepath = filepath
		self.Handle = Sound(filepath)
		self.Ended = False
		self.Looping = looping

class CameraComponent(object):
	def __init__(self, cameraType: CameraType, left: float, right: float, bottom: float, top: float, zNear = -1.0, zFar = 10.0):
		if cameraType == CameraType.Orthographic:
			self.Camera = OrthographicCamera(left, right, bottom, top, zNear, zFar)
		else:
			raise RuntimeError("Invalid camera type")
