from ...utils import Static

from OpenGL import GL
import glm

class RendererSettings(Static):
    """
    A class that stores set of rules about how renderer
    should work. To make them work any changes have to
    be made before renderer initialization. Be aware that
    in cetian cases renderer may not use settings provided
    here if it is necessary.
    """

    MaxQuadsCount = 300
    """
    Max quads count that can be renderer within one batch.
    This value has to be the same as value in the value that coresponds
    to transformation matrices count declared in the shader.
    """

    MaxTextures = 16
    """
    Max number of textures that can be used within one draw batch.
    """

    BlendingEnabled = True
    """
    Indicates that blending should be enabled.
    """

    BlendingFunc = (GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    """
    Function that will be used by rasterizer when applying blending if
    it is enabled. The variable has form of (fource factor, destination factor).
    """

    MultisamplingEnabled = True
    """
    Indicates that renderer should use multisampling.
    This is only applied when using direct screen rendering.
    When using custom framebuffer multisampling should be set using appropriate
    framebuffer specifications.
    """

    ClearColor = glm.vec4(0.0)
    """
    Default color that will be used when clearing screen or framebuffer.
    """