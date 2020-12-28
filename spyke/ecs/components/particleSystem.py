#region Import
from ...managers.textureManager import TextureManager
from ...graphics.texturing.textureUtils import NoTexture

import random
import glm
#endregion

class Particle(object):
	def __init__(self):
		self.position = glm.vec2(0.0)
		self.velocity = glm.vec2(0.0)
		self.size = glm.vec2(0.0)
		self.rotation = 0.0
		self.rotationVelocity = 0.0
		self.transform = glm.mat4(1.0)

		self.life = 0.0
		self.isAlive = False

		self.color = glm.vec4(1.0)

		self.texHandle = NoTexture
	
	def __repr__(self):
		return f"Active: {self.isAlive}"

class ParticleSystemComponent(object):
	MaxCount = 100

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

		self.__texHandle = NoTexture

		self.maxCount = max(maxCount, ParticleSystemComponent.MaxCount)
		
		self.particlePool = []
		for _ in range(self.maxCount):
			self.particlePool.append(Particle())
		self.activeParticleIdx = self.maxCount - 1
	
	@property
	def texHandle(self):
		return self.__texHandle
	
	@texHandle.setter
	def texHandle(self, value: str):
		self.__texHandle = TextureManager.GetTexture(value)
	
	def EmitParticles(self, count: int) -> None:
		for _ in range(count):
			self.EmitParticle()

	def EmitParticle(self) -> None:
		particle = self.particlePool[self.activeParticleIdx]
		particle.isAlive = True

		particle.position = self.basePos.__copy__()
		particle.rotation = self.baseRot
		
		if self.randomizeMovement:
			randomChange = random.random() - 0.5
		else:
			randomChange = 1.0
		
		particle.velocity = self.velocity * randomChange
		particle.rotationVelocity = self.rotationVelocity * randomChange

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