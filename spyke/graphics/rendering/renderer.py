from spyke import debug
from spyke.enums import GLType
from spyke import events
from ..rectangle import RectangleF
from ..texturing import Texture
from ..vertexArray import VertexArray
from ...utils import create_quad_indices, Iterator
from .renderStats import RenderStats
from ..shader import Shader
from ..buffers import *
from ..screenStats import ScreenStats
from ..contextInfo import ContextInfo
from ...constants import _C_FLOAT_P, _GL_FILL_MODE_NAMES_MAP, _GL_FLOAT_SIZE, _NP_FLOAT, _NP_UINT
from ...enums import Hint, InternalFormat, NvidiaIntegerName, Vendor, Keys
from ...ecs import components
from ... import resourceManager as ResourceManager

from OpenGL import GL
from OpenGL.GL.INTEL.framebuffer_CMAA import glApplyFramebufferAttachmentCMAAINTEL
from PIL import Image
import glm
import time
import numpy as np
import os

##############################################
# RESTORE PARTICLE RENDERER (REFACTORIZE IT) #
##############################################

SCREENSHOT_DIRECTORY = "screenshots/"
SHADER_SOURCES_DIRECTORY = "spyke/graphics/shaderSources/"

UNIFORM_BLOCK_SIZE = 16 * _GL_FLOAT_SIZE
MATRICES_UNIFORM_BLOCK_INDEX = 0

DEFAULT_RENDER_COLOR_ATTACHMENT = 0
ENTITY_ID_ATTACHMENT = 1

MAX_QUADS_COUNT = 400
VERTICES_PER_QUAD = 4
INDICES_PER_QUAD = 6

POS_VERTEX_VALUES_COUNT = 3

BASIC_INSTANCE_VERTEX_VALUES_COUNT = 4 + 2 + 1 + 1 + 16
BASIC_VERTEX_VERTEX_VALUES_COUNT = 2

POST_VERTEX_VERTEX_VALUES_COUNT = 3 + 2

POS_DATA_VERTEX_SIZE = POS_VERTEX_VALUES_COUNT * _GL_FLOAT_SIZE

BASIC_INSTANCE_DATA_VERTEX_SIZE = BASIC_INSTANCE_VERTEX_VALUES_COUNT * _GL_FLOAT_SIZE
BASIC_VERTEX_DATA_VERTEX_SIZE = BASIC_VERTEX_VERTEX_VALUES_COUNT * _GL_FLOAT_SIZE

POST_VERTEX_DATA_VERTEX_SIZE = POST_VERTEX_VERTEX_VALUES_COUNT * _GL_FLOAT_SIZE

POS_DATA_BUFFER_BINDING = 0
INSTANCE_DATA_BUFFER_BINDING = 1
POST_DATA_BUFFER_BINDING = 0

MAX_TEXTURES_COUNT = 15

MULTISAMPLE_TEXTURE_SAMPLER = 0
NORMAL_TEXTURE_SAMPLER = 1

BUFFER_TEXTURE_SAMPLER = 15

_quadVertices = [
    0.0, 1.0, 0.0,
    1.0, 1.0, 0.0,
    1.0, 0.0, 0.0,
    0.0, 0.0, 0.0]

_textures = [0] * MAX_TEXTURES_COUNT
_lastTexture = 1

_quadsCount = 0

_isInitialized = False
_polygonModeIter = Iterator(
    [GL.GL_LINE, GL.GL_POINT, GL.GL_FILL], looping=True)
_currentFillMode = GL.GL_FILL

_basicShader: Shader = None
_posVbo: StaticBuffer = None
_instanceDataVbo: DynamicBuffer = None
_vertexDataTbo: TextureBuffer = None
_ibo: StaticBuffer = None
_ubo: UniformBuffer = None
_basicVao: VertexArray = None
_whiteTexture: Texture = None
_framebuffer: Framebuffer = None

renderStats = RenderStats()
screenStats = ScreenStats()
contextInfo = ContextInfo()


def Initialize(initialWidth: int, initialHeight: int, samples: int) -> None:
    global _ubo, _isInitialized, _whiteTexture

    if _isInitialized:
        debug.log_warning('Renderer already initialized.')
        return

    contextInfo.get_info()
    Texture._CompressionEnabled = contextInfo.capabilities.arb_texture_compression_enabled

    _CreateBasicComponents()

    # if not contextInfo.capabilities.intel_framebuffer_cmaa_enabled:
    # 	_CreatePostProcessComponents()

    _CreateFramebuffer(initialWidth, initialHeight, samples)
    _SetGLSettings()

    if not os.path.exists(SCREENSHOT_DIRECTORY):
        os.mkdir(SCREENSHOT_DIRECTORY)

    _isInitialized = True

    debug.get_gl_error()
    debug.log_info('Master renderer fully initialized.')


def CaptureFrame():
    pixels = GL.glReadPixels(0, 0, screenStats.width, screenStats.height,
                             GL.GL_RGB, GL.GL_UNSIGNED_BYTE, outputType=None)

    img = Image.frombytes(
        'RGB', (screenStats.width, screenStats.height), pixels)
    img = img.transpose(Image.FLIP_TOP_BOTTOM)

    filename = os.path.join(SCREENSHOT_DIRECTORY,
                            f'screenshot_{time.time()}.jpg')
    img.save(filename, 'JPEG')
    debug.log_info(f'Screenshot was saved as "{filename}".')


def ClearScreen() -> None:
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)


def SetClearColor(r: float, g: float, b: float, a: float):
    GL.glClearColor(r, g, b, a)


def RenderScene(scene, viewProjectionMatrix: glm.mat4) -> None:
    renderStats.Clear()
    start = time.perf_counter()

    _ubo.add_data(np.asarray(viewProjectionMatrix,
                  dtype=np.float32).T.flatten())
    _ubo.flip()

    _ubo.bind()

    # _framebuffer.bind()

    ClearScreen()

    GL.glPolygonMode(GL.GL_FRONT_AND_BACK, _currentFillMode)
    GL.glEnable(GL.GL_DEPTH_TEST)

    # drawables = [x for x in scene.GetComponents(components.SpriteComponent, components.TransformComponent)]
    # opaque = [x for x in drawables if x[1][0].color.w == 1.0]
    # alpha = [x for x in drawables if x not in opaque]

    # alpha.sort(key = lambda x: x[1][0].color.w, reverse = True)
    # for ent, (sprite, transform) in opaque:
    # 	_RenderQuad(transform.matrix, sprite.color, ResourceManager.GetTexture(sprite.texture), sprite.tiling_factor, entId=int(ent))

    # _Flush()

    # GL.glDisable(GL.GL_DEPTH_TEST)
    # for ent, (sprite, transform) in alpha:
    # 	_RenderQuad(transform.matrix, sprite.color, ResourceManager.GetTexture(sprite.texture), sprite.tiling_factor, entId=int(ent))

    # _Flush()

    for ent, (sprite, transform) in scene.GetComponents(components.SpriteComponent, components.TransformComponent):
        _RenderQuad(transform.matrix, sprite.color, ResourceManager.GetTexture(
            sprite.texture), sprite.tiling_factor, entId=int(ent))

    _Flush()

    GL.glDisable(GL.GL_DEPTH_TEST)

    text_transform = glm.mat4(1.0)

    for ent, (text, transform) in scene.GetComponents(components.TextComponent, components.TransformComponent):
        font = ResourceManager.GetFont(text.font)
        texture = ResourceManager.GetTexture(font.texture)

        advSum = 0.0

        for char in text.text:
            glyph = font.get_glyph(char)

            adv = advSum / screenStats.width * (text.size / font.base_size)

            scWidth = glyph.width / screenStats.width * \
                (text.size / font.base_size)
            scHeight = glyph.height / screenStats.height * \
                (text.size / font.base_size)

            advSum += glyph.advance

            text_transform[3, 0] = transform.position.x + adv
            text_transform[3, 1] = transform.position.y
            text_transform[3, 2] = transform.position.z
            text_transform[0, 0] = scWidth
            text_transform[1, 1] = scHeight

            _RenderQuad(text_transform, text.color, texture,
                        glm.vec2(1.0, 1.0), glyph.texRect, int(ent))

    _Flush()

    # for _, system in scene.GetComponent(components.ParticleSystemComponent):
    # 	for particle in system.particlePool:
    # 		if particle.isAlive:
    # 			Renderer.__ParticleRenderer.RenderParticle(particle.position, particle.size, particle.rotation, particle.color, particle.texHandle)

    # Renderer.__ParticleRenderer.EndScene()

    # _basicRenderer.RenderQuad(glm.mat4(1.0), glm.vec4(1.0), _framebuffer.GetColorAttachment(DEFAULT_RENDER_COLOR_ATTACHMENT), glm.vec2(1.0))
    # _basicRenderer.EndScene()

    # if contextInfo.capabilities.intel_framebuffer_cmaa_enabled and _framebuffer.specification.samples > 1:
    # 	glApplyFramebufferAttachmentCMAAINTEL()

    # _framebuffer.Unbind()

    # ClearScreen()
    # GL.glViewport(0, 0, screenStats.width, screenStats.height)
    # GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

    # viewProjectionData = np.asarray(glm.mat4(1.0), dtype=_NP_FLOAT)
    # viewProjectionData[2, 2] = -1.0
    # _ubo.AddData(memoryview(viewProjectionData), viewProjectionData.size * _GL_FLOAT_SIZE)

    # viewProjectionData = np.asarray(glm.mat4(1.0), dtype=_NP_FLOAT)
    # _ubo.AddData(memoryview(viewProjectionData), viewProjectionData.size * _GL_FLOAT_SIZE)

    # if contextInfo.capabilities.intel_framebuffer_cmaa_enabled:
    # 	# _RenderQuad(glm.mat4(1.0), glm.vec4(1.0), DEFAULT_RENDER_COLOR_ATTACHMENT, glm.vec2(1.0))
    # 	_RenderQuad(glm.mat4(1.0), glm.vec4(1.0), _framebuffer.GetColorAttachment(DEFAULT_RENDER_COLOR_ATTACHMENT), glm.vec2(1.0))
    # 	_Flush()
    # else:
    # 	_RenderFramebuffer(_framebuffer.specification.samples, _framebuffer.GetColorAttachment(DEFAULT_RENDER_COLOR_ATTACHMENT))

    if contextInfo.vendor == Vendor.Nvidia:
        renderStats.videoMemoryUsed = contextInfo.memoryAvailable - \
            GL.glGetInteger(NvidiaIntegerName.GpuMemInfoCurrentAvailable)

    renderStats.draw_time = time.perf_counter() - start


def _Flush():
    global _quadsCount, _lastTexture

    if not _quadsCount:
        return

    _vertexDataTbo.flip()
    _instanceDataVbo.flip()

    for i in range(_lastTexture):
        GL.glBindTextureUnit(i, _textures[i])

    # GL.glBindTextures(0, len(textures), np.asarray(textures, dtype=np.uint32))
    GL.glBindTextureUnit(15, _vertexDataTbo.texture_id)

    _basicVao.bind()
    _basicShader.use()

    GL.glDrawElementsInstanced(
        GL.GL_TRIANGLES, _quadsCount * INDICES_PER_QUAD, _ibo.data_type, None, _quadsCount)

    renderStats.draws_count += 1
    renderStats.vertex_count += _quadsCount * VERTICES_PER_QUAD
    _quadsCount = 0
    _lastTexture = 1


def _RenderQuad(transform: glm.mat4, color: glm.vec4, texture: Texture, tilingFactor: glm.vec2, texRect: RectangleF = RectangleF.one(), entId: int = -1):
    global _lastTexture, _lastVertexPos, _lastInstancePos, _quadsCount

    if _quadsCount >= MAX_QUADS_COUNT:
        _Flush()

    texIdx = 0

    if texture:
        for i in range(1, _lastTexture):
            if _textures[i] == texture.id:
                texIdx = i
                break

        if texIdx == 0:
            if _lastTexture >= MAX_TEXTURES_COUNT:
                _Flush()

            texIdx = _lastTexture
            _textures[_lastTexture] = texture.id
            _lastTexture += 1

    vertex_data = np.array([
        texRect.left, texRect.top,
        texRect.right, texRect.top,
        texRect.right, texRect.bottom,
        texRect.left, texRect.bottom,
    ], dtype=np.float32)

    _vertexDataTbo.add_data(vertex_data)

    instance_data = np.concatenate((
        np.array([
            color.x,
            color.y,
            color.z,
            color.w,
            tilingFactor.x,
            tilingFactor.y,
            texIdx,
            entId
        ], dtype=np.float32),
        np.asarray(transform, dtype=np.float32).T.flatten()
    ))

    _instanceDataVbo.add_data(instance_data)

    _quadsCount += 1

# def _RenderFramebuffer(samplesToRender: int, attachmentToRender: int) -> None:
# 	_postProcessVao.bind()

# 	_postProcessShader.Use()
# 	_postProcessShader.SetUniform1i("uSamples", samplesToRender)

# 	GL.glBindTextureUnit(MULTISAMPLE_TEXTURE_SAMPLER if samplesToRender > 1 else NORMAL_TEXTURE_SAMPLER, attachmentToRender)

# 	GL.glDrawElementsInstanced(GL.GL_TRIANGLES, INDICES_PER_QUAD, _ibo.dataType, None, 1)

# 	renderStats.drawsCount += 1
# 	renderStats.vertexCount += VERTICES_PER_QUAD
# 	_ResetCounters()


@events.register(events.KeyDownEvent, priority=-1)
def _key_down_callback(e: events.KeyDownEvent) -> None:
    global _currentFillMode

    if e.repeat:
        return

    if e.key == Keys.KeyGrave:
        _currentFillMode = next(_polygonModeIter)
        debug.log_info(
            f'Renderer drawing mode set to: {_GL_FILL_MODE_NAMES_MAP[_currentFillMode]}')
    elif e.key == Keys.KeyF1:
        CaptureFrame()


@events.register(events.ResizeEvent, priority=-1)
def _resize_callback(e: events.ResizeEvent) -> None:
    GL.glScissor(0, 0, e.width, e.height)
    GL.glViewport(0, 0, e.width, e.height)

    if e.width != 0 and e.height != 0:
        _framebuffer.Resize(e.width, e.height)


def _SetGLSettings() -> None:
    GL.glEnable(GL.GL_MULTISAMPLE)

    if contextInfo.vendor == Vendor.Nvidia:
        GL.glHint(Hint.MultisampleFilterNvHint, GL.GL_NICEST)

    GL.glHint(GL.GL_TEXTURE_COMPRESSION_HINT, GL.GL_NICEST)

    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glDepthFunc(GL.GL_LEQUAL)

    GL.glCullFace(GL.GL_FRONT)
    GL.glFrontFace(GL.GL_CW)
    GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

    GL.glPointSize(4.0)

    GL.glEnable(GL.GL_LINE_SMOOTH)

    GL.glClearColor(0.0, 0.0, 0.0, 1.0)


def _CreateFramebuffer(initialWidth: int, initialHeight: int, samples: int) -> None:
    global _framebuffer

    fbSpec = FramebufferSpec(initialWidth, initialHeight)
    fbSpec.samples = 1 if contextInfo.capabilities.intel_framebuffer_cmaa_enabled else samples

    colorAttachmentSpec = FramebufferAttachmentSpec(GL.GL_RGBA)

    entIdAttachmentSpec = FramebufferAttachmentSpec(GL.GL_RED_INTEGER)
    entIdAttachmentSpec.minFilter = GL.GL_NEAREST
    entIdAttachmentSpec.magFilter = GL.GL_NEAREST

    depthAttachmentSpec = FramebufferAttachmentSpec(GL.GL_DEPTH24_STENCIL8)
    depthAttachmentSpec.minFilter = GL.GL_NEAREST
    depthAttachmentSpec.magFilter = GL.GL_NEAREST

    fbSpec.attachment_specs = [
        colorAttachmentSpec,
        entIdAttachmentSpec,
        depthAttachmentSpec
    ]

    _framebuffer = Framebuffer(fbSpec)


def _CreateBasicComponents() -> None:
    global _posVbo, _instanceDataVbo, _vertexDataTbo, _ibo, _basicShader, _basicVao, _vertexData, _instanceData, _ubo

    _posVbo = StaticBuffer(_quadVertices, GLType.Float)
    _instanceDataVbo = DynamicBuffer(
        BASIC_INSTANCE_DATA_VERTEX_SIZE * MAX_QUADS_COUNT, GLType.Float)
    _vertexDataTbo = TextureBuffer(BASIC_VERTEX_DATA_VERTEX_SIZE *
                                   MAX_QUADS_COUNT * VERTICES_PER_QUAD, GLType.Float, InternalFormat.Rg32f)
    _ibo = StaticBuffer(create_quad_indices(
        MAX_QUADS_COUNT), GLType.UnsignedInt)

    _basicShader = Shader()
    _basicShader.add_stage(GL.GL_VERTEX_SHADER,
                           SHADER_SOURCES_DIRECTORY + 'basic.vert')
    _basicShader.add_stage(GL.GL_FRAGMENT_SHADER,
                           SHADER_SOURCES_DIRECTORY + 'basic.frag')
    _basicShader.compile()

    _basicShader.set_uniform_int(
        'uTextures', list(range(MAX_TEXTURES_COUNT)))
    _basicShader.set_uniform_int('uTexCoordsBuffer', BUFFER_TEXTURE_SAMPLER)
    _basicShader.set_uniform_block_binding(
        'uMatrices', MATRICES_UNIFORM_BLOCK_INDEX)
    _basicShader.validate()

    _basicVao = VertexArray()

    _basicVao.bind_vertex_buffer(
        POS_DATA_BUFFER_BINDING, _posVbo, 0, POS_DATA_VERTEX_SIZE)
    _basicVao.bind_vertex_buffer(
        INSTANCE_DATA_BUFFER_BINDING, _instanceDataVbo, 0, BASIC_INSTANCE_DATA_VERTEX_SIZE)
    _basicVao.bind_element_buffer(_ibo)

    _basicVao.add_layout(_basicShader.get_attrib_location(
        'aPosition'), POS_DATA_BUFFER_BINDING, 3, GLType.Float, False)
    _basicVao.add_layout(_basicShader.get_attrib_location(
        'aColor'), INSTANCE_DATA_BUFFER_BINDING, 4, GLType.Float, False, 1)
    _basicVao.add_layout(_basicShader.get_attrib_location(
        'aTilingFactor'), INSTANCE_DATA_BUFFER_BINDING, 2, GLType.Float, False, 1)
    _basicVao.add_layout(_basicShader.get_attrib_location(
        'aTexIdx'), INSTANCE_DATA_BUFFER_BINDING, 1, GLType.Int, False, 1)
    _basicVao.add_layout(_basicShader.get_attrib_location(
        'aEntId'), INSTANCE_DATA_BUFFER_BINDING, 1, GLType.Int, False, 1)
    _basicVao.add_matrix_layout(_basicShader.get_attrib_location(
        'aTransform'), INSTANCE_DATA_BUFFER_BINDING, 4, 4, GLType.Float, False, 1)

    _textures[0] = Texture.CreateWhiteTexture().id

    _ubo = UniformBuffer(UNIFORM_BLOCK_SIZE, GLType.Float)
    _ubo.bind_to_uniform(MATRICES_UNIFORM_BLOCK_INDEX)

# def _CreatePostProcessComponents() -> None:
# 	global _postProcessVao, _postProcessShader, _postDataVbo

# 	# _postDataVbo = StaticBuffer(_postData, GLType.Float)

# 	_postProcessShader = Shader()
# 	_postProcessShader.add_stage(GL.GL_VERTEX_SHADER, SHADER_SOURCES_DIRECTORY + "post.vert")
# 	_postProcessShader.add_stage(GL.GL_FRAGMENT_SHADER, SHADER_SOURCES_DIRECTORY + "post.frag")
# 	_postProcessShader.Compile()

# 	_postProcessShader.SetUniform1i("uTexture", NORMAL_TEXTURE_SAMPLER)
# 	_postProcessShader.SetUniform1i("uTextureMS", MULTISAMPLE_TEXTURE_SAMPLER)
# 	_postProcessShader.set_uniform_block_binding("uMatrices", MATRICES_UNIFORM_BLOCK_INDEX)
# 	_postProcessShader.Validate()

# 	_postProcessVao = VertexArray()

# 	_postProcessVao.bind_vertex_buffer(POST_DATA_BUFFER_BINDING, _postDataVbo, 0, POST_VERTEX_DATA_VERTEX_SIZE)
# 	_postProcessVao.bind_element_buffer(_ibo)

# 	_postProcessVao.add_layout(_postProcessShader.get_attrib_location("aPosition"), POST_DATA_BUFFER_BINDING, 3, GLType.Float, False)
# 	_postProcessVao.add_layout(_postProcessShader.get_attrib_location("aTexCoord"), POST_DATA_BUFFER_BINDING, 2, GLType.Float, False)
