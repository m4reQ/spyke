#region Import
from ..transform import CreateTransform
from ..debug import Log, LogLevel
from ..graphics import Font
from ..audio.sound import Sound
from ..graphics.texturing.textureUtils import TextureHandle
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
			self.Matrix = CreateTransform(self.__pos, self.__size, self.__rot)
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
	MaxCount = 20

	class Particle(object):
		def __init__(self):
			self.TexHandle = TextureHandle(0.0, 0.0, 0, -1)

			self.Position = glm.vec2(0.0)
			self.Velocity = glm.vec2(0.0)
			self.Rotation = 0.0

			self.ColorBegin = glm.vec4(1.0, 1.0, 1.0, 1.0)
			self.ColorEnd = glm.vec4(1.0, 1.0, 1.0, 1.0)
			self.Color = glm.vec4(1.0, 1.0, 1.0, 1.0)

			self.SizeBegin = glm.vec2(1.0)
			self.SizeEnd = glm.vec2(1.0)

			self.LifeTime = 1.0
			self.LifeRemaining = 0.0

			self.IsActive = False

			self.Transform = glm.mat4(1.0)
		
		def __repr__(self):
			return "Active: " + str(self.IsActive)

	def __init__(self, position: glm.vec2, duration: float, texHandle: TextureHandle, count: int):
		self.Duration = duration
		self.TimeElapsed = 0.0

		self.Started = False
		self.Ended = False
		self.Paused = False
		self.Looping = False

		self.TexHandle = texHandle

		self.ColorBegin = glm.vec4(1.0, 1.0, 1.0, 1.0)
		self.ColorEnd = glm.vec4(1.0, 1.0, 1.0, 1.0)
		self.Color = glm.vec4(1.0, 1.0, 1.0, 1.0)
		self.FadeAway = False

		self.SizeBegin = glm.vec2(1.0)
		self.SizeEnd = glm.vec2(1.0)

		self.Velocity = glm.vec2(0.0)
		self.VelocityVariation = glm.vec2(0.0)
		self.MovementSpeed = 0.08
		self.RotationSpeed = 0.01
		self.RotationDelta = 0.0
		self.BasePosition = position
		self.RandomizeMovement = False

		self.Count = max(count, ParticleComponent.MaxCount)

		self.ParticlePool = []
		self.ActiveParticleIndex = ParticleComponent.MaxCount - 1

		for _ in range(self.Count):
			self.ParticlePool.append(ParticleComponent.Particle())
	
	def Start(self):
		self.Started = True
	
	def Pause(self):
		self.Paused = True
	
	def EmitParticle(self):
		particle = self.ParticlePool[self.ActiveParticleIndex]
		
		particle.IsActive = True

		particle.Position = self.BasePosition
		if self.RandomizeMovement:
			particle.Rotation = random.random() * self.RotationDelta * glm.pi()
		else:
			particle.Rotation = self.RotationDelta * glm.pi()
		
		particle.Velocity = self.Velocity
		if self.RandomizeMovement:
			particle.Velocity.x += self.VelocityVariation.x * (random.random() - 0.5)
			particle.Velocity.y += self.VelocityVariation.y * (random.random() - 0.5)
		else:
			particle.Velocity.x += self.VelocityVariation.x
			particle.Velocity.y += self.VelocityVariation.y
		
		particle.BeginColor = self.ColorBegin
		particle.EndColor = self.ColorEnd
		particle.Color = self.ColorBegin

		particle.SizeBegin = self.SizeBegin
		particle.SizeEnd = self.SizeEnd

		particle.LifeTime = self.Duration
		particle.LifeRemaining = self.Duration

		oldIndex = self.ActiveParticleIndex
		self.ActiveParticleIndex = (oldIndex - 1) % len(self.ParticlePool)

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
