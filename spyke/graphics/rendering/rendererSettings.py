class RendererSettings:
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
    """

    MaxTextures = 16
    """
    Max number of textures that can be used within one draw batch.
    """

    MultisamplingEnabled = True
    """
    Indicates that renderer should use multisampling.
    This is only applied when using direct screen rendering.
    When using custom framebuffer multisampling should be set using appropriate
    framebuffer specifications.
    """

    ScreenCaptureDirectory = "screenshots"