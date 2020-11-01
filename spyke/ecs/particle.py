from ..transform import Vector2, Matrix4, Vector4
from ..graphics import NoTexture

class Particle(object):
	def __init__(self):
		self.position = Vector2(0.0)
		self.velocity = Vector2(0.0)
		self.size = Vector2(0.0)
		self.rotation = 0.0
		self.rotationVelocity = 0.0
		self.transform = Matrix4(1.0)

		self.life = 0.0
		self.isAlive = False
		
		self.gravity = 0.0

		self.color = Vector4(1.0)

		self.texHandle = NoTexture
	
	def __repr__(self):
		return f"Active: {self.isAlive}"
