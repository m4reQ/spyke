from spyke.utils.converters import PilImageToNp
from .ecs import Scene
from .ecs.components import *
from .ecs.processors import *
from .debugging import Debug, LogLevel
from .constants import _IMAGE_FORMAT_MAP, _NP_UBYTE, MAX_LOADING_TASKS_COUNT
from .exceptions import GraphicsException, SpykeException
from .graphics.texturing.texture import Texture, TextureData, TextureSpec
from .graphics.text import Font, Glyph
from .graphics.rectangle import RectangleF
from .autoslot import WeakSlots

from OpenGL import GL
from PIL import Image
from functools import lru_cache
import numpy as np
import time
import threading
import queue
import yaml

_fonts = {}
_textures = {}
_currentScene = None

_loadingTasksCount = 0
_loadingSemaphore = threading.BoundedSemaphore(MAX_LOADING_TASKS_COUNT)
_loadingQueue = queue.Queue()
_loadingThreads = []

SCENE_SECTION_MARKER = "--scene--"
RESOURCE_SECTION_MARKER = "--resources--"
RESOURCE_END_MARKER = "res_end"

DUMP_STANDARD_ARGS = {
	"sort_keys": True,
	"allow_unicode": True,
	"explicit_start": True,
	"explicit_end": True
}

class TextureLoadingData(WeakSlots):
	def __init__(self):
		self.texName: str = ""
		self.texData: TextureData = None
		self.texSpec: TextureSpec = None

def FinishLoading():
	"""
	Call this function to ensure that all resources are loaded
	properly and ready to use.
	"""

	global _loadingTasksCount

	while _loadingTasksCount != 0:
		task = _loadingQueue.get()
		_textures[task.texName] = Texture(task.texData, task.texSpec)
		
		_loadingTasksCount -= 1
	
	for t in _loadingThreads:
		t.join()
	
	_loadingThreads.clear()

def CreateTexture(filepath: str, name: str="", texSpec=TextureSpec()):
	"""
	Creates a spyke texture from a given image file
	and associates it with a name. If the name argument is empty
	the texture name becomes the filename.
	
	param filepath: image file
	param name: name that will be used to access texture
	"""
	
	global _loadingTasksCount
	if not name:
		name = filepath

	if name in _textures:
		Debug.Log(f"Texture named '{name}' already exists. Texture will be overwritten.", LogLevel.Warning)

		_textures[name].Delete(True)
		del _textures[name]
	
	thread = threading.Thread(target=_LoadTexture, args=(filepath, name, texSpec))

	_loadingSemaphore.acquire()

	_loadingTasksCount += 1
	thread.start()
	_loadingThreads.append(thread)

def CreateFont(fontFilepath: str, imageFilepath: str, name: str = "") -> None:
	"""
	Creates a spyke font from given font and image files
	and associates it with a name. If the name argument is empty
	the name becomes the font filename.

	param fontfilepath: font file (.fnt)
	param imageFilepath: image file
	param name: name that will be used to access font
	"""

	start = time.perf_counter()

	if not name:
		name = fontFilepath

	if name in _fonts:
		Debug.Log(f"Font named '{name}' already exists. Font will be overwritten.", LogLevel.Warning)

		_fonts[name].texture.Delete(True)
		del _fonts[name]

	tSpec = TextureSpec()
	tSpec.minFilter = GL.GL_NEAREST
	tSpec.magFilter = GL.GL_NEAREST
	tSpec.mipmaps = 1
	tSpec.wrapMode = GL.GL_CLAMP_TO_EDGE
	tSpec.compress = False

	loadingData = _LoadTextureImmediate(imageFilepath, imageFilepath, tSpec)

	font = Font()
	font.imageFilepath = imageFilepath
	font.fontFilepath = fontFilepath
	font.name = name
	font.texture = Texture(loadingData.texData, loadingData.texSpec)
	font.characters, font.baseSize = _LoadFontData(fontFilepath, (font.texture.width, font.texture.height))

	_fonts[name] = font

	Debug.Log(f"Font '{name}' loaded in {time.perf_counter() - start} seconds.", LogLevel.Info)

def CreateScene(name: str) -> Scene:
	"""
	Creates empty spyke scene.
	"""

	s = Scene(name)
	s.AddProcessor(TransformProcessor())
	s.AddProcessor(ParticleProcessor())

	return s

def SaveScene(filepath: str, scene: Scene) -> None:
	start = time.perf_counter()

	try:
		file = open(filepath, "w+")
	except (IOError, OSError):
		raise SpykeException(f"Cannot save scene as '{filepath}'.")

	file.write(RESOURCE_SECTION_MARKER + '\n')

	for name, texture in _textures.items():
		dumped = yaml.dump(texture.specification, **DUMP_STANDARD_ARGS)
		file.write(f"res_texture\n{texture.filepath}\n{name}\n{len(dumped)}\n{dumped}\n{RESOURCE_END_MARKER}\n")
	for name, font in _fonts.items():
		file.write(f"res_font\n{font.fontFilepath}\n{font.imageFilepath}\n{name}\n{RESOURCE_END_MARKER}\n")
	
	file.flush()

	file.write(SCENE_SECTION_MARKER + '\n')
	dumped = yaml.dump(scene, **DUMP_STANDARD_ARGS)
	file.write(f"{len(dumped)}\n{dumped}")

	file.close()

	Debug.Log(f"Scene {scene.name} saved as {filepath} in {time.perf_counter() - start} seconds.", LogLevel.Info)

def LoadScene(filepath: str):
	"""
	Loads spyke scene from given file and makes the scene current.

	param filepath: Scene filepath.
	"""

	def readline():
		nonlocal file

		line = file.readline()
		if not line:
			raise EOFError

		return line.replace('\n', '')

	start = time.perf_counter()

	try:
		file = open(filepath, "r")
	except (IOError, OSError):
		raise SpykeException(f"Cannot load scene file '{filepath}'.")

	isInResSection = False
	isLoadingRes = False

	scene = None

	while True:
		try:
			line = readline()
		except EOFError:
			break

		if line == RESOURCE_SECTION_MARKER:
			isInResSection = True
			continue

		if line == SCENE_SECTION_MARKER:
			dataSize = int(readline())
			scene = yaml.load(file.read(dataSize), Loader=yaml.Loader)

			isInResSection = False
		
		if isInResSection:
			if line == "res_texture":
				if isLoadingRes:
					raise SpykeException("Another scene resource data appeared while reading previous one.")

				texPath = readline()
				texName = readline()
				dataSize = int(readline())
				texSpec = yaml.load(file.read(dataSize), Loader=yaml.Loader)

				CreateTexture(texPath, texName, texSpec)
			elif line == "res_font":
				if isLoadingRes:
					raise SpykeException("Another scene resource data appeared while reading previous one.")
				
				fontPath = readline()
				texPath = readline()
				name = readline()

				CreateFont(fontPath, texPath, name)
			elif line == "res_end":
				isLoadingRes = False
	
	FinishLoading()

	Debug.Log(f"Scene '{scene.name}' from file '{filepath}' loaded succesfully in {time.perf_counter() - start} seconds.", LogLevel.Info)
	SetSceneCurrent(scene)

	return scene

def ReleaseResources() -> None:
	"""
	Release all resources that are already
	loaded and clear current scene.
	"""

	for tex in _textures.values():
		tex.Delete(removeRef=True)
	
	for font in _fonts.values():
		font.texture.Delete(removeRef=True)
	
	_textures.clear()
	_fonts.clear()

def SetSceneCurrent(scene: Scene) -> None:
	global _currentScene
	_currentScene = scene

	Debug.Log(f"Scene '{scene.name}' has been made current.", LogLevel.Info)

@lru_cache
def GetCurrentScene() -> Scene:
	"""
	Returns current scene.
	"""

	if not _currentScene:
		raise SpykeException("No scene is made current.")

	return _currentScene

@lru_cache
def GetTexture(name: str) -> Texture:
	"""
	Returns texture from texture pool that coresponds
	to the given name. If the name is an empty string
	white texture will be returned.
	"""

	if name == '':
		return None

	if not name in _textures:
		raise GraphicsException(f"No such texture: '{name}'.")
	
	return _textures[name]

@lru_cache
def GetFont(name: str) -> Font:
	if not name in _fonts:
		raise GraphicsException(f"No such font: '{name}'.")
	
	return _fonts[name]

def _LoadTexture(filepath: str, name: str, texSpec: TextureSpec) -> None:
	data = _LoadTextureImmediate(filepath, name, texSpec)

	_loadingQueue.put(data)
	_loadingSemaphore.release()

def _LoadTextureImmediate(filepath: str, name: str, texSpec: TextureSpec) -> TextureLoadingData:
	start = time.perf_counter()

	try:
		img = Image.open(filepath, mode="r")
	except FileNotFoundError as e:
		raise SpykeException(f"Cannot find texture file '{e.filename}'.")

	tData = TextureData(img.size[0], img.size[1])
	tData.format = _IMAGE_FORMAT_MAP[img.mode]
	tData.data = PilImageToNp(img).data
	tData.filepath = filepath

	img.close()

	loadingData = TextureLoadingData()
	loadingData.texName = name
	loadingData.texData = tData
	loadingData.texSpec = texSpec

	Debug.Log(f"Texture '{filepath}' loaded in {time.perf_counter() - start} seconds.", LogLevel.Info)

	return loadingData

def _LoadFontData(filepath: str, texSize: tuple) -> tuple:
	characters = {}
	base = 1

	f = open(filepath, mode="r")

	for line in f.readlines():
		if not line.startswith("char "):
			idx = line.find("base=")
			if idx != -1:
				base = line[idx:].split(' ')[0]
				base = int(base.split('=')[-1])

			continue
			
		lineData = line[5:len(line) - 20]
		lineData = lineData.split(' ')
		lineData = [e for e in lineData if e != '' and e != ' ']

		width = int(lineData[3][6:])
		height = int(lineData[4][7:])
		bearX = int(lineData[5][8:])
		bearY = int(lineData[6][8:])
		adv = int(lineData[7][9:])
		_ord = int(lineData[0][3:])

		texX = int(lineData[1][2:]) / texSize[0]
		texY = int(lineData[2][2:]) / texSize[1]
		texWidth = int(lineData[3][6:]) / texSize[0]
		texHeight = int(lineData[4][7:]) / texSize[1]
		texRect = RectangleF(texX, texY, texWidth, texHeight)

		characters[_ord] = Glyph(width, height, bearX, bearY, adv, texRect, _ord)

	f.close()

	return (characters, base)
