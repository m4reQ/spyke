from .utils import Timer
from .debug import Log, LogLevel
from .managers import TextureManager, FontManager
from .enums import TextureMagFilter
from .ecs.components import *
from .ecs import Scene
from .transform import Vector3, Vector2

from pydoc import locate
from typing import List, TypeAlias

def __CreateComponent(_type: TypeAlias, data: List[str]):
	if _type == ColorComponent:
		return ColorComponent(float(data[0]), float(data[1]), float(data[2]), float(data[3]))
	elif _type == ScriptComponent:
		return ScriptComponent(data[0])
	elif _type == TransformComponent:
		convData = [float(x) for x in data]
		return TransformComponent(Vector3(convData[0], convData[1], convData[2]), Vector2(convData[3], convData[4]), convData[5])
	elif _type == LineComponent:
		convData = [float(x) for x in data]
		return LineComponent(Vector3(convData[0], convData[1], convData[2]), Vector3(convData[3], convData[4], convData[5]))
	elif _type == SpriteComponent:
		return SpriteComponent(data[0], (data[1], data[2]))
	elif _type == CameraComponent:
		if data[0] == "O":
			camType = CameraType.Orthographic
		elif data[0] == "P":
			camType = CameraType.Perspective

		return CameraComponent(camType, float(data[1]), float(data[2]), float(data[3]), float(data[4]), float(data[5]), float(data[6]))
	elif _type == TextComponent:
		return TextComponent(data[0], int(data[1]), data[2])

def __DecodeLine(line: str, scene: Scene):
	if line.startswith("#"):
		return
	
	if line.startswith("r "):
		lineData = line.split(" ")
		_type = lineData[1]

		if _type == "arr":
			width = int(lineData[2])
			height = int(lineData[3])
			layers = int(lineData[4])
			levels = int(lineData[5])

			if lineData[6] == "Linear":
				magFilter = TextureMagFilter.Linear
			elif lineData[6] == "Nearest":
				magFilter = TextureMagFilter.Nearest

			TextureManager.CreateTextureArray(width, height, layers, levels, magFilter)
		elif _type == "tex":
			filepath = lineData[2]
			arrId = int(lineData[3])

			TextureManager.LoadTexture(filepath, arrId)
		elif _type == "fnt":
			fontFilepath = lineData[2]
			bitmapFilepath = lineData[3]
			name = lineData[4]

			FontManager.CreateFont(fontFilepath, bitmapFilepath, name)
	elif line.startswith("e "):
		EntityManager.CreateEntity(scene, line[1])
	elif line.startswith("c "):
		_type = locate(lineData[1])
		ent = lineData[2]
		args = lineData[3:]

		comp = _type(*args)
		scene.AddComponent(ent, comp)

def LoadScene(filepath: str):
	Timer.Start()

	try:
		f = open(filepath, "r")
	except FileNotFoundError as e:
		raise RuntimeError(f"Cannot find scene file named '{e.filename}'.")

	scene = None

	for line in f:
		if line.startswith("/n ") and not scene:
			scene = SceneManager.CreateScene(line[1])
			__DecodeLine(line, scene)
	else:
		f.close()
		Log(f"Scene from file '{filepath}' loaded in {Timer.Stop()} seconds.", LogLevel.Info)

def SaveScene(scene: Scene, filepath: str):
	Timer.Start()

	

