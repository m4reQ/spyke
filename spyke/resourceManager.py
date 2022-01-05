from spyke import debug
from .ecs import Scene
from .ecs.components import *
from .ecs.processors import *
from .constants import _IMAGE_FORMAT_MAP, MAX_LOADING_TASKS_COUNT
from .exceptions import GraphicsException, SpykeException
from .graphics.texturing.texture import Texture, TextureData, TextureSpec
from .graphics.text import Font, Glyph
from .graphics.rectangle import RectangleF

from OpenGL import GL
from PIL import Image
from functools import lru_cache
from typing import Dict, List, Tuple
import numpy as np
import time
import threading
import yaml

_fonts = {}
_textures = {}
_models = {}
_currentScene = None

_loadingTasks = []
_loadingTasksCount = 0
_loadingSemaphore = threading.BoundedSemaphore(MAX_LOADING_TASKS_COUNT)

SCENE_SECTION_MARKER = "--scene--"
RESOURCE_SECTION_MARKER = "--resources--"
RESOURCE_END_MARKER = "res_end"

DUMP_STANDARD_ARGS = {
    "sort_keys": True,
    "allow_unicode": True,
    "explicit_start": True,
    "explicit_end": True
}


def get_image_data(im: Image.Image) -> np.ndarray:
    im.load()

    encoder = Image._getencoder(im.mode, 'raw', im.mode)
    encoder.setimage(im.im)

    shape, typestr = Image._conv_type_shape(im)
    data = np.empty(shape, dtype=np.dtype(typestr))
    mem = data.data.cast('B', (data.data.nbytes,))

    bufsize, s, offset = 65536, 0, 0
    while not s:
        _, s, d = encoder.encode(bufsize)
        mem[offset:offset + len(d)] = d
        offset += len(d)
    if s < 0:
        raise GraphicsException(f"Encoder error: {s}")

    return data


class ALoadingTask:
    def __init__(self, filepath: str):
        self._thread: threading.Thread = None
        self.filepath: str = filepath
        self.isFinished: bool = False
        self.loadingTime: float = 0.0

    def Start(self) -> None:
        self._thread = threading.Thread(target=self._Load)
        self._thread.start()

    def _Load(self) -> None:
        pass

    def Finalize(self) -> bool:
        pass


class TextureLoadingTask(ALoadingTask):
    def __init__(self, filepath: str, name: str):
        super().__init__(filepath)

        self.texData: TextureData = None
        self.texSpec: TextureSpec = None
        self.texName: str = name

    def _Load(self) -> None:
        start = time.perf_counter()

        try:
            img = Image.open(self.filepath, mode="r")
        except FileNotFoundError as e:
            raise SpykeException(f"Cannot find texture file '{e.filename}'.")

        self.texData = TextureData(img.size[0], img.size[1])
        self.texData.format = _IMAGE_FORMAT_MAP[img.mode]
        self.texData.data = get_image_data(img).data
        self.texData.filepath = self.filepath

        img.close()

        self.isFinished = True
        self.loadingTime += time.perf_counter() - start

    def Finalize(self) -> bool:
        start = time.perf_counter()

        if self.texName in _textures:
            debug.log_warning(
                'Texture with given name already exists. Texture will be overwritten.')
            _textures[self.texName].Delete(True)

        _textures[self.texName] = Texture(self.texData, self.texSpec)

        self.loadingTime += time.perf_counter() - start
        debug.log_info(
            f'Texture {self.texName} loaded in {self.loadingTime} seconds.')

        return True


class FontLoadingTask(ALoadingTask):
    def __init__(self, filepath: str, texName: str, name: str):
        super().__init__(filepath)

        self.glyphs: Dict[str, Glyph] = {}
        self.baseSize: Tuple[int, int] = None
        self.texName: str = texName
        self.fontName: str = name

    def _Load(self):
        start = time.perf_counter()

        f = open(self.filepath, mode="r")

        for line in f.readlines():
            if not line.startswith("char "):
                idx = line.find("base=")
                if idx != -1:
                    self.baseSize = line[idx:].split(' ')[0]
                    self.baseSize = int(self.baseSize.split('=')[-1])

                continue

            lineData = line[5:len(line) - 20]
            lineData = lineData.split(' ')
            lineData = [e for e in lineData if e != '' and e != ' ']

            width = int(lineData[3][6:])
            height = int(lineData[4][7:])
            bearX = int(lineData[5][8:])
            bearY = int(lineData[6][8:])
            adv = int(lineData[7][9:])
            _chr = chr(int(lineData[0][3:]))

            texX = int(lineData[1][2:])
            texY = int(lineData[2][2:])
            texWidth = int(lineData[3][6:])
            texHeight = int(lineData[4][7:])
            texRect = RectangleF(texX, texY, texWidth, texHeight)

            self.glyphs[_chr] = Glyph(
                width, height, bearX, bearY, adv, texRect, _chr)

        f.close()

        self.isFinished = True
        self.loadingTime += time.perf_counter() - start

    def Finalize(self):
        start = time.perf_counter()

        if not self.texName in _textures:
            return False

        tex = _textures[self.texName]

        for glyph in self.glyphs.values():
            glyph.texRect.x /= tex.width
            glyph.texRect.y /= tex.height
            glyph.texRect.width /= tex.width
            glyph.texRect.height /= tex.height

        font = Font()
        font.image_filepath = tex.filepath
        font.font_filepath = self.filepath
        font.name = self.fontName
        font.texture = self.texName
        font.characters = self.glyphs
        font.base_size = self.baseSize

        if self.fontName in _fonts:
            debug.log_warning(
                'Font with given name already exists. Font will be overwritten.')

        _fonts[self.fontName] = font

        self.loadingTime += time.perf_counter() - start
        debug.log_info(
            f'Font {self.fontName} loaded in {self.loadingTime} seconds.')

        return True


class ModelLoadingTask(ALoadingTask):
    def __init__(self, filepath: str, name: str):
        super().__init__(filepath)

        self.modelName: str = name
        self.vertices: List[float] = []
        self.indices: List[int] = []

    def _Load(self) -> None:
        raise NotImplementedError()

    def Finalize(self) -> bool:
        raise NotImplementedError()


def FinishLoading():
    """
    Call this function to ensure that all resources are loaded
    properly and ready to use.
    """

    global _loadingTasksCount

    while _loadingTasksCount != 0:
        toRemove = []

        for task in _loadingTasks:
            if not task.isFinished:
                continue

            if task.Finalize():
                toRemove.append(task)

        for task in toRemove:
            task._thread.join()
            _loadingSemaphore.release()
            _loadingTasks.remove(task)
            _loadingTasksCount -= 1

    debug.log_info('Resource loading finished.')


def CreateTexture(filepath: str, name: str = "", texSpec=TextureSpec()):
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

    loadingTask = TextureLoadingTask(filepath, name)
    loadingTask.texSpec = texSpec

    _loadingSemaphore.acquire()
    _loadingTasks.append(loadingTask)
    _loadingTasksCount += 1
    loadingTask.Start()


def CreateFont(filepath: str, image_filepath: str, name: str = "") -> None:
    """
    Creates a spyke font from given font and image files
    and associates it with a name. If the name argument is empty
    the name becomes the font filename.

    :param filepath: font file (.fnt)
    :param image_filepath: image file
    :param name: name that will be used to access font
    """

    global _loadingTasksCount

    tSpec = TextureSpec()
    tSpec.min_filter = GL.GL_NEAREST
    tSpec.mag_filter = GL.GL_NEAREST
    tSpec.mipmaps = 1
    tSpec.wrap_mode = GL.GL_CLAMP_TO_EDGE
    tSpec.compress = False

    tex_name = f'font_{name}_texture'

    CreateTexture(image_filepath, tex_name, tSpec)

    if not name:
        name = filepath

    loadingTask = FontLoadingTask(filepath, tex_name, name)

    _loadingSemaphore.acquire()
    _loadingTasks.append(loadingTask)
    _loadingTasksCount += 1
    loadingTask.Start()


def CreateModel(filepath: str, name: str = "") -> None:
    raise NotImplementedError()


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
        file.write(
            f"res_texture\n{texture.filepath}\n{name}\n{len(dumped)}\n{dumped}\n{RESOURCE_END_MARKER}\n")
    for name, font in _fonts.items():
        file.write(
            f"res_font\n{font.fontFilepath}\n{font.imageFilepath}\n{name}\n{RESOURCE_END_MARKER}\n")

    file.flush()

    file.write(SCENE_SECTION_MARKER + '\n')
    dumped = yaml.dump(scene, **DUMP_STANDARD_ARGS)
    file.write(f"{len(dumped)}\n{dumped}")

    file.close()

    debug.log_info(
        f'Scene {scene.name} saved as {filepath} in {time.perf_counter() - start} seconds.')


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
                    raise SpykeException(
                        "Another scene resource data appeared while reading previous one.")

                texPath = readline()
                texName = readline()
                dataSize = int(readline())
                texSpec = yaml.load(file.read(dataSize), Loader=yaml.Loader)

                CreateTexture(texPath, texName, texSpec)
            elif line == "res_font":
                if isLoadingRes:
                    raise SpykeException(
                        "Another scene resource data appeared while reading previous one.")

                fontPath = readline()
                texPath = readline()
                name = readline()

                CreateFont(fontPath, texPath, name)
            elif line == "res_end":
                isLoadingRes = False

    FinishLoading()

    debug.log_info(
        f'Scene "{scene.name}" from file "{filepath}" loaded succesfully in {time.perf_counter() - start} seconds.')
    SetSceneCurrent(scene)

    return scene


def ReleaseResources() -> None:
    '''
    Releases all resources that are already
    loaded and clears current scene.
    '''

    global _currentScene

    for tex in _textures.values():
        tex.Delete(True)

    for font in _fonts.values():
        GetTexture(font.texture).Delete(True)

    _textures.clear()
    _fonts.clear()

    _currentScene = None


def SetSceneCurrent(scene: Scene) -> None:
    global _currentScene
    _currentScene = scene

    debug.log_info(f'Scene "{scene.name}" has been made current.')


@lru_cache
def GetCurrentScene() -> Scene:
    '''
    Returns current scene. Raises SpykeException
    if current scene is not set.
    '''

    if not _currentScene:
        raise SpykeException('No scene is set current.')

    return _currentScene


@lru_cache
def GetTexture(name: str) -> Texture:
    '''
    Returns texture from texture pool that coresponds
    to the given name. If the name is an empty string
    white texture will be returned. Raises GraphicsException
    if certain texture cannot be found.

    :param name: Name of a texture.
    '''

    if name == '':
        return None

    if not name in _textures:
        raise GraphicsException(f'No such texture: "{name}".')

    return _textures[name]


@lru_cache
def GetFont(name: str) -> Font:
    '''
    Returns font from font pool that coresponds
    to the given name. Raises GraphicsException
    if certain font cannot be found.

    :param name: Name of a font.
    '''

    if not name in _fonts:
        raise GraphicsException(f'No such font: "{name}".')

    return _fonts[name]


@lru_cache
def GetModel(name: str) -> None:
    '''
    Returns model from model pool that coresponds
    to the given name. Raises GraphicsException
    if certain model cannot be found.

    :param name: Name of a model.
    '''

    if not name in _models:
        raise GraphicsException(f'No such model "{name}".')

    return _models[name]
