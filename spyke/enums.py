from OpenGL import GL
import openal
import glfw
import enum

# TODO: Make all OpenGL enums `IntEnum`

# region Audio


class AudioState:
    Initial = openal.AL_INITIAL
    Paused = openal.AL_PAUSED
    Playing = openal.AL_PLAYING
    Stopped = openal.AL_STOPPED
# endregion

# region Graphics


class CameraType(enum.Enum):
    Orthographic = enum.auto()
    Perspective = enum.auto()


class Vendor(enum.Enum):
    Nvidia = enum.auto()
    Intel = enum.auto()
    Amd = enum.auto()
    WindowsSoftware = enum.auto()
    Unknown = enum.auto()
# endregion

# region OpenGL


class TextureMagFilter:
    Linear = GL.GL_LINEAR
    Nearest = GL.GL_NEAREST


class TextureType:
    Rgb = GL.GL_RGB
    Rgba = GL.GL_RGBA


class HintMode:
    Fastest = GL.GL_FASTEST
    Nicest = GL.GL_NICEST
    DontCare = GL.GL_DONT_CARE


class Hint:
    FogHint = GL.GL_FOG_HINT
    FragmentShaderDerivativeHint = GL.GL_FRAGMENT_SHADER_DERIVATIVE_HINT
    GenerateMipmapHint = GL.GL_GENERATE_MIPMAP_HINT
    LineSmoothHint = GL.GL_LINE_SMOOTH_HINT
    PerspectiveCorrectionHint = GL.GL_PERSPECTIVE_CORRECTION_HINT
    PointSmoothHint = GL.GL_POINT_SMOOTH_HINT
    PolygonSmoothHint = GL.GL_POLYGON_SMOOTH_HINT
    TextureCompressionHint = GL.GL_TEXTURE_COMPRESSION_HINT
    MultisampleFilterNvHint = 0x8534


class NvidiaIntegerName:
    GpuMemInfoTotalAvailable = 0x9048
    GpuMemInfoCurrentAvailable = 0x9049


class FramebufferStatus(enum.IntEnum):
    Complete = GL.GL_FRAMEBUFFER_COMPLETE
    Undefined = GL.GL_FRAMEBUFFER_UNDEFINED
    IncompleteAttachment = GL.GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT
    MissingAttachment = GL.GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT
    IncompleteDrawBuffer = GL.GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER
    IncompleteReadBuffer = GL.GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER
    Unsupported = GL.GL_FRAMEBUFFER_UNSUPPORTED
    IncompleteMultisample = GL.GL_FRAMEBUFFER_INCOMPLETE_MULTISAMPLE
    IncompleteLayerTargets = GL.GL_FRAMEBUFFER_INCOMPLETE_LAYER_TARGETS


class ErrorCode(enum.IntEnum):
    NoError = GL.GL_NO_ERROR
    InvalidEnum = GL.GL_INVALID_ENUM
    InvalidValue = GL.GL_INVALID_VALUE
    InvalidOperation = GL.GL_INVALID_OPERATION
    StackOverflow = GL.GL_STACK_OVERFLOW
    StackUnderflow = GL.GL_STACK_UNDERFLOW
    InvalidFramebufferOperation = GL.GL_INVALID_FRAMEBUFFER_OPERATION
    OutOfMemory = GL.GL_OUT_OF_MEMORY
    ContextLost = GL.GL_CONTEXT_LOST


class MinFilter(enum.IntEnum):
    Nearest = GL.GL_NEAREST
    Linear = GL.GL_LINEAR
    NearestMipmapNearest = GL.GL_NEAREST_MIPMAP_NEAREST
    NearestMipmapLinear = GL.GL_NEAREST_MIPMAP_LINEAR
    LinearMipmapNearest = GL.GL_LINEAR_MIPMAP_NEAREST
    LinearMipmapLinear = GL.GL_LINEAR_MIPMAP_LINEAR


class AttachmentPoint(enum.IntEnum):
    ColorAttachment = GL.GL_COLOR_ATTACHMENT0
    DepthAttachment = GL.GL_DEPTH_ATTACHMENT
    StencilAttachment = GL.GL_STENCIL_ATTACHMENT
    DepthStencilAttachment = GL.GL_DEPTH_STENCIL_ATTACHMENT


class MagFilter(enum.IntEnum):
    Nearest = GL.GL_NEAREST
    Linear = GL.GL_LINEAR


class WrapMode(enum.IntEnum):
    Repeat = GL.GL_REPEAT
    MirroredRepeat = GL.GL_MIRRORED_REPEAT
    ClampToEdge = GL.GL_CLAMP_TO_EDGE
    MirrorClampToEdge = GL.GL_MIRROR_CLAMP_TO_EDGE
    ClampToBorder = GL.GL_CLAMP_TO_BORDER


class PrimitiveMode:
    Triangles = GL.GL_TRIANGLES
    Points = GL.GL_POINTS
    LineStrip = GL.GL_LINE_STRIP
    LineLoop = GL.GL_LINE_LOOP
    Lines = GL.GL_LINES
    LineStripAdjacency = GL.GL_LINE_STRIP_ADJACENCY
    LinesAdjacency = GL.GL_LINES_ADJACENCY
    TriangleStrip = GL.GL_TRIANGLE_STRIP
    TriangleFan = GL.GL_TRIANGLE_FAN
    Triangles = GL.GL_TRIANGLES
    TriangleStripAdjacency = GL.GL_TRIANGLE_STRIP_ADJACENCY
    TrianglesAdjacency = GL.GL_TRIANGLES_ADJACENCY
    Patches = GL.GL_PATCHES


class BlendFactor:
    Zero = GL.GL_ZERO
    One = GL.GL_ONE
    SrcColor = GL.GL_SRC_COLOR
    OneMinusSrcColor = GL.GL_ONE_MINUS_SRC_COLOR
    DstColor = GL.GL_DST_COLOR
    OneMinusDstColor = GL.GL_ONE_MINUS_DST_COLOR
    SrcAlpha = GL.GL_SRC_ALPHA
    OneMinusSrcAlpha = GL.GL_ONE_MINUS_SRC_ALPHA
    DstAlpha = GL.GL_DST_ALPHA
    OneMinusDstAlpha = GL.GL_ONE_MINUS_DST_ALPHA
    ConstantColor = GL.GL_CONSTANT_COLOR
    OneMinusConstantColor = GL.GL_ONE_MINUS_CONSTANT_COLOR
    ConstantAlpha = GL.GL_CONSTANT_ALPHA
    OneMinusConstantAlpha = GL.GL_ONE_MINUS_CONSTANT_ALPHA
    SrcAlphaSaturate = GL.GL_SRC_ALPHA_SATURATE
    Src1Color = GL.GL_SRC1_COLOR
    OneMinusSrc1Color = GL.GL_ONE_MINUS_SRC1_COLOR
    Src1Alpha = GL.GL_SRC1_ALPHA
    OneMinusSrc1Alpha = GL.GL_ONE_MINUS_SRC1_ALPHA


class StringName(enum.IntEnum):
    Vendor = GL.GL_VENDOR,
    Renderer = GL.GL_RENDERER,
    Version = GL.GL_VERSION,
    ShadingLanguageVersion = GL.GL_SHADING_LANGUAGE_VERSION


class GLType(enum.IntEnum):
    Float = GL.GL_FLOAT
    Double = GL.GL_DOUBLE
    Fixed = GL.GL_FIXED
    HalfFloat = GL.GL_HALF_FLOAT
    Int = GL.GL_INT
    UnsignedInt = GL.GL_UNSIGNED_INT
    Byte = GL.GL_BYTE
    UnsignedByte = GL.GL_UNSIGNED_BYTE
    Short = GL.GL_SHORT
    UnsignedShort = GL.GL_UNSIGNED_SHORT


class TextureFormat(enum.IntEnum):
    Red = GL.GL_RED
    Rg = GL.GL_RG
    Rgb = GL.GL_RGB
    Bgr = GL.GL_BGR
    Rgba = GL.GL_RGBA
    Bgra = GL.GL_BGRA
    DepthComponent = GL.GL_DEPTH_COMPONENT
    StencilIndex = GL.GL_STENCIL_INDEX


class SwizzleMask(enum.IntEnum):
    Red = GL.GL_RED
    Green = GL.GL_GREEN
    Blue = GL.GL_BLUE
    Alpha = GL.GL_ALPHA
    Zero = GL.GL_ZERO
    One = GL.GL_ONE


class SwizzleTarget(enum.IntEnum):
    TextureSwizzleR = GL.GL_TEXTURE_SWIZZLE_R
    TextureSwizzleG = GL.GL_TEXTURE_SWIZZLE_G
    TextureSwizzleB = GL.GL_TEXTURE_SWIZZLE_B
    TextureSwizzleA = GL.GL_TEXTURE_SWIZZLE_A
    TextureSwizzleRgba = GL.GL_TEXTURE_SWIZZLE_RGBA


class TextureCompareFunc(enum.IntEnum):
    LessEqual = GL.GL_LEQUAL
    GreaterEqual = GL.GL_GEQUAL
    Less = GL.GL_LESS
    Greater = GL.GL_GREATER
    Equal = GL.GL_EQUAL
    NotEqual = GL.GL_NOTEQUAL
    Always = GL.GL_ALWAYS
    Never = GL.GL_NEVER


class TextureCompareMode(enum.IntEnum):
    CompareRefToTexture = GL.GL_COMPARE_REF_TO_TEXTURE
    None_ = GL.GL_NONE


class TextureParameter(enum.IntEnum):
    DepthStencilTextureMode = GL.GL_DEPTH_STENCIL_TEXTURE_MODE
    TextureBaseLevel = GL.GL_TEXTURE_BASE_LEVEL
    TextureBorderColor = GL.GL_TEXTURE_BORDER_COLOR
    TextureCompareFunc = GL.GL_TEXTURE_COMPARE_FUNC
    TextureCompareMode = GL.GL_TEXTURE_COMPARE_MODE
    TextureLodBias = GL.GL_TEXTURE_LOD_BIAS
    TextureMinFilter = GL.GL_TEXTURE_MIN_FILTER
    TextureMagFilter = GL.GL_TEXTURE_MAG_FILTER
    TextureMinLod = GL.GL_TEXTURE_MIN_LOD
    TextureMaxLod = GL.GL_TEXTURE_MAX_LOD
    TextureMaxLevel = GL.GL_TEXTURE_MAX_LEVEL
    TextureSwizzleR = GL.GL_TEXTURE_SWIZZLE_R
    TextureSwizzleG = GL.GL_TEXTURE_SWIZZLE_G
    TextureSwizzleB = GL.GL_TEXTURE_SWIZZLE_B
    TextureSwizzleA = GL.GL_TEXTURE_SWIZZLE_A
    TextureSwizzleRgba = GL.GL_TEXTURE_SWIZZLE_RGBA
    TextureWrapS = GL.GL_TEXTURE_WRAP_S
    TextureWrapT = GL.GL_TEXTURE_WRAP_T
    TextureWrapR = GL.GL_TEXTURE_WRAP_R


class SizedInternalFormat(enum.IntEnum):
    R8 = GL.GL_R8
    R8Snorm = GL.GL_R8_SNORM
    R16 = GL.GL_R16
    R16Snorm = GL.GL_R16_SNORM
    Rg8 = GL.GL_RG8
    Rg8Snorm = GL.GL_RG8_SNORM
    Rg16 = GL.GL_RG16
    Rg16Snorm = GL.GL_RG16_SNORM
    R3g3b2 = GL.GL_R3_G3_B2
    Rgb4 = GL.GL_RGB4
    Rgb5 = GL.GL_RGB5
    Rgb8 = GL.GL_RGB8
    Rgb8Snorm = GL.GL_RGB8_SNORM
    Rgb10 = GL.GL_RGB10
    Rgb12 = GL.GL_RGB12
    Rgb16Snorm = GL.GL_RGB16_SNORM
    Rgba2 = GL.GL_RGBA2
    Rgba4 = GL.GL_RGBA4
    Rgb5a1 = GL.GL_RGB5_A1
    Rgba8 = GL.GL_RGBA8
    Rgba8Snorm = GL.GL_RGBA8_SNORM
    Rgb10a2 = GL.GL_RGB10_A2
    Rgb10a2ui = GL.GL_RGB10_A2UI
    Rgba12 = GL.GL_RGBA12
    Rgba16 = GL.GL_RGBA16
    Srgb8 = GL.GL_SRGB8
    Srgb8Alpha8 = GL.GL_SRGB8_ALPHA8
    R16f = GL.GL_R16F
    Rg16f = GL.GL_RG16F
    Rgb16f = GL.GL_RGB16F
    Rgba16f = GL.GL_RGBA16F
    R32f = GL.GL_R32F
    Rg32f = GL.GL_RG32F
    Rgb32f = GL.GL_RGB32F
    Rgba32f = GL.GL_RGBA32F
    R11fg11fb10f = GL.GL_R11F_G11F_B10F
    Rgb9e5 = GL.GL_RGB9_E5
    R8i = GL.GL_R8I
    R8ui = GL.GL_R8UI
    R16i = GL.GL_R16I
    R16ui = GL.GL_R16UI
    R32i = GL.GL_R32I
    R32ui = GL.GL_R32UI
    Rg8i = GL.GL_RG8I
    Rg8ui = GL.GL_RG8UI
    Rg16i = GL.GL_RG16I
    Rg16ui = GL.GL_RG16UI
    Rg32i = GL.GL_RG32I
    Rg32ui = GL.GL_RG32UI
    Rgb8i = GL.GL_RGB8I
    Rgb8ui = GL.GL_RGB8UI
    Rgb16i = GL.GL_RGB16I
    Rgb16ui = GL.GL_RGB16UI
    Rgb32i = GL.GL_RGB32I
    Rgb32ui = GL.GL_RGB32UI
    Rgba8i = GL.GL_RGBA8I
    Rgba8ui = GL.GL_RGBA8UI
    Rgba16i = GL.GL_RGBA16I
    Rgba16ui = GL.GL_RGBA16UI
    Rgba32i = GL.GL_RGBA32I
    Rgba32ui = GL.GL_RGBA32UI
    DepthComponent16 = GL.GL_DEPTH_COMPONENT16
    DepthComponent24 = GL.GL_DEPTH_COMPONENT24
    DepthComponent32f = GL.GL_DEPTH_COMPONENT32F
    StencilIndex8 = GL.GL_STENCIL_INDEX8
    Depth24Stencil8 = GL.GL_DEPTH24_STENCIL8
    Depth32fStencil8 = GL.GL_DEPTH32F_STENCIL8


class TextureBufferSizedInternalFormat(enum.IntEnum):
    R8 = GL.GL_R8
    R16 = GL.GL_R16
    R16f = GL.GL_R16F
    R32f = GL.GL_R32F
    R8i = GL.GL_R8I
    R16i = GL.GL_R16I
    R32i = GL.GL_R32I
    R8ui = GL.GL_R8UI
    R16ui = GL.GL_R16UI
    R32ui = GL.GL_R32UI
    Rg8 = GL.GL_RG8
    Rg16 = GL.GL_RG16
    Rg16f = GL.GL_RG16F
    Rg32f = GL.GL_RG32F
    Rg8i = GL.GL_RG8I
    Rg16i = GL.GL_RG16I
    Rg32i = GL.GL_RG32I
    Rg8ui = GL.GL_RG8UI
    Rg16ui = GL.GL_RG16UI
    Rg32ui = GL.GL_RG32UI
    Rgb32f = GL.GL_RGB32F
    Rgb32i = GL.GL_RGB32I
    Rgb32ui = GL.GL_RGB32UI
    Rgba8 = GL.GL_RGBA8
    Rgba16 = GL.GL_RGBA16
    Rgba16f = GL.GL_RGBA16F
    Rgba32f = GL.GL_RGBA32F
    Rgba8i = GL.GL_RGBA8I
    Rgba16i = GL.GL_RGBA16I
    Rgba32i = GL.GL_RGBA32I
    Rgba8ui = GL.GL_RGBA8UI
    Rgba16ui = GL.GL_RGBA16UI
    Rgba32ui = GL.GL_RGBA32UI


class ShaderType(enum.IntEnum):
    ComputeShader = GL.GL_COMPUTE_SHADER
    VertexShader = GL.GL_VERTEX_SHADER
    TessControlShader = GL.GL_TESS_CONTROL_SHADER
    TexxEvaluationShader = GL.GL_TESS_EVALUATION_SHADER
    GeometryShader = GL.GL_GEOMETRY_SHADER
    FragmentShader = GL.GL_FRAGMENT_SHADER


class TextureTarget(enum.IntEnum):
    Texture1d = GL.GL_TEXTURE_1D
    Texture2d = GL.GL_TEXTURE_2D
    Texture3d = GL.GL_TEXTURE_3D
    Texture1dArray = GL.GL_TEXTURE_1D_ARRAY
    Texture2dArray = GL.GL_TEXTURE_2D_ARRAY
    TextureRectangle = GL.GL_TEXTURE_RECTANGLE
    TextureCubeMap = GL.GL_TEXTURE_CUBE_MAP
    TextureCubeMapArray = GL.GL_TEXTURE_CUBE_MAP_ARRAY
    TextureBuffer = GL.GL_TEXTURE_BUFFER
    Texture2dMultisample = GL.GL_TEXTURE_2D_MULTISAMPLE
    Texture2dMultisampleArray = GL.GL_TEXTURE_2D_MULTISAMPLE_ARRAY


class CompressedSizedInternalFormat(enum.IntEnum):
    CompressedRed = GL.GL_COMPRESSED_RED
    CompressedRg = GL.GL_COMPRESSED_RG
    CompressedRgb = GL.GL_COMPRESSED_RGB
    CompressedRgba = GL.GL_COMPRESSED_RGBA
    CompressedSrgb = GL.GL_COMPRESSED_SRGB
    CompressedSrgbAlpha = GL.GL_COMPRESSED_SRGB_ALPHA
    CompressedRedRgtc1 = GL.GL_COMPRESSED_RED_RGTC1
    CompressedSignedRedRgtc1 = GL.GL_COMPRESSED_SIGNED_RED_RGTC1
    CompressedRgRgtc2 = GL.GL_COMPRESSED_RG_RGTC2
    CompressedSignedRgRgtc2 = GL.GL_COMPRESSED_SIGNED_RG_RGTC2
    CompressedRgbaBptcUnorm = GL.GL_COMPRESSED_RGBA_BPTC_UNORM
    CompressedSrgbAlphaBptcUnorm = GL.GL_COMPRESSED_SRGB_ALPHA_BPTC_UNORM
    CompressedRgbBptcSignedFloat = GL.GL_COMPRESSED_RGB_BPTC_SIGNED_FLOAT
    CompressedRgbBptcUnsignedFloat = GL.GL_COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT


class ClearMask(enum.IntEnum):
    ColorBufferBit = GL.GL_COLOR_BUFFER_BIT
    DepthBufferBit = GL.GL_DEPTH_BUFFER_BIT
    StencilBufferBit = GL.GL_STENCIL_BUFFER_BIT
    # TODO: Add rest of masks


class PolygonMode(enum.IntEnum):
    Line = GL.GL_LINE
    Fill = GL.GL_FILL
    Point = GL.GL_POINT


class EnableCap:
    Blend = GL.GL_BLEND
    DepthTest = GL.GL_DEPTH_TEST
    CullFace = GL.GL_CULL_FACE
    MultiSample = GL.GL_MULTISAMPLE
    AlphaTest = GL.GL_ALPHA_TEST
    ScissorTest = GL.GL_SCISSOR_TEST


class AlphaOperator:
    Never = GL.GL_NEVER
    Always = GL.GL_ALWAYS
    Less = GL.GL_LESS
    Equal = GL.GL_EQUAL
    Greater = GL.GL_GREATER
    LessOrEqual = GL.GL_LEQUAL
    GreaterOrEqual = GL.GL_GEQUAL
    NotEqual = GL.GL_NOTEQUAL


class BufferUsageFlag:
    StaticDraw = GL.GL_STATIC_DRAW
    DynamicDraw = GL.GL_DYNAMIC_DRAW
    StreamDraw = GL.GL_STREAM_DRAW
# endregion

# region Input


class MouseButtons:
    Left = glfw.MOUSE_BUTTON_LEFT
    Middle = glfw.MOUSE_BUTTON_MIDDLE
    Right = glfw.MOUSE_BUTTON_RIGHT


class KeyMods:
    ModControl = glfw.MOD_CONTROL
    ModShift = glfw.MOD_SHIFT
    ModAlt = glfw.MOD_ALT
    ModSuper = glfw.MOD_SUPER
    ModCapsLock = glfw.MOD_CAPS_LOCK
    ModNumLock = glfw.MOD_NUM_LOCK


class Keys:
    KeyInvalid = glfw.KEY_UNKNOWN

    # special
    KeySpace = glfw.KEY_SPACE
    KeyApostrophe = glfw.KEY_APOSTROPHE
    KeyComma = glfw.KEY_COMMA
    KeyMinus = glfw.KEY_MINUS
    KeyPeriod = glfw.KEY_PERIOD
    KeySlash = glfw.KEY_SLASH
    KeySemicolon = glfw.KEY_SEMICOLON
    KeyLeftBracket = glfw.KEY_LEFT_BRACKET
    KeyRightBracket = glfw.KEY_RIGHT_BRACKET
    KeyBackslash = glfw.KEY_BACKSLASH
    KeyGrave = glfw.KEY_GRAVE_ACCENT
    KeyEscape = glfw.KEY_ESCAPE
    KeyEnter = glfw.KEY_ENTER
    KeyTab = glfw.KEY_TAB
    KeyBackspace = glfw.KEY_BACKSPACE
    KeyInsert = glfw.KEY_INSERT
    KeyDelete = glfw.KEY_DELETE
    KeyPageUp = glfw.KEY_PAGE_UP
    KeyPageDown = glfw.KEY_PAGE_DOWN
    KeyHome = glfw.KEY_HOME
    KeyEnd = glfw.KEY_END
    KeyCapsLock = glfw.KEY_CAPS_LOCK
    KeyScrollLock = glfw.KEY_SCROLL_LOCK
    KeyNumLock = glfw.KEY_NUM_LOCK
    KeyPrintScreen = glfw.KEY_PRINT_SCREEN
    KeyPause = glfw.KEY_PAUSE
    KeyMenu = glfw.KEY_MENU

    # functional
    KeyF1 = glfw.KEY_F1
    KeyF2 = glfw.KEY_F2
    KeyF3 = glfw.KEY_F3
    KeyF4 = glfw.KEY_F4
    KeyF5 = glfw.KEY_F5
    KeyF6 = glfw.KEY_F6
    KeyF7 = glfw.KEY_F7
    KeyF8 = glfw.KEY_F8
    KeyF9 = glfw.KEY_F9
    KeyF10 = glfw.KEY_F10
    KeyF11 = glfw.KEY_F11
    KeyF12 = glfw.KEY_F12

    # modifiers
    KeyLeftShift = glfw.KEY_LEFT_SHIFT
    KeyRightShift = glfw.KEY_RIGHT_SHIFT
    KeyLeftControl = glfw.KEY_LEFT_CONTROL
    KeyRightControl = glfw.KEY_RIGHT_CONTROL
    KeyLeftAlt = glfw.KEY_LEFT_ALT
    KeyRightAlt = glfw.KEY_RIGHT_ALT
    KeyLeftSuper = glfw.KEY_LEFT_SUPER
    KeyRightSuper = glfw.KEY_RIGHT_SUPER

    # arrows
    KeyRight = glfw.KEY_RIGHT
    KeyLeft = glfw.KEY_LEFT
    KeyUp = glfw.KEY_UP
    KeyDown = glfw.KEY_DOWN

    # numerical
    Key0 = glfw.KEY_0
    Key1 = glfw.KEY_1
    Key2 = glfw.KEY_2
    Key3 = glfw.KEY_3
    Key4 = glfw.KEY_4
    Key5 = glfw.KEY_5
    Key6 = glfw.KEY_6
    Key7 = glfw.KEY_7
    Key8 = glfw.KEY_8
    Key9 = glfw.KEY_9

    # alphabetical
    KeyA = glfw.KEY_A
    KeyB = glfw.KEY_B
    KeyC = glfw.KEY_C
    KeyD = glfw.KEY_D
    KeyE = glfw.KEY_E
    KeyF = glfw.KEY_F
    KeyG = glfw.KEY_G
    KeyH = glfw.KEY_H
    KeyI = glfw.KEY_I
    KeyJ = glfw.KEY_J
    KeyK = glfw.KEY_K
    KeyL = glfw.KEY_L
    KeyM = glfw.KEY_M
    KeyN = glfw.KEY_N
    KeyO = glfw.KEY_O
    KeyP = glfw.KEY_P
    KeyQ = glfw.KEY_Q
    KeyR = glfw.KEY_R
    KeyS = glfw.KEY_S
    KeyT = glfw.KEY_T
    KeyU = glfw.KEY_U
    KeyV = glfw.KEY_V
    KeyW = glfw.KEY_W
    KeyX = glfw.KEY_X
    KeyY = glfw.KEY_Y
    KeyZ = glfw.KEY_Z
# endregion
