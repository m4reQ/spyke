import enum
from OpenGL import GL
from OpenGL.GL.EXT import texture_compression_s3tc

class _SizedInternalFormat(enum.IntEnum):
    pass


class _CompressedInternalFormat(_SizedInternalFormat):
    pass


class _TextureFormat(enum.IntEnum):
    pass


class HintMode(enum.IntEnum):
    Fastest = GL.GL_FASTEST
    Nicest = GL.GL_NICEST
    DontCare = GL.GL_DONT_CARE


class Hint(enum.IntEnum):
    FogHint = GL.GL_FOG_HINT
    FragmentShaderDerivativeHint = GL.GL_FRAGMENT_SHADER_DERIVATIVE_HINT
    GenerateMipmapHint = GL.GL_GENERATE_MIPMAP_HINT
    LineSmoothHint = GL.GL_LINE_SMOOTH_HINT
    PerspectiveCorrectionHint = GL.GL_PERSPECTIVE_CORRECTION_HINT
    PointSmoothHint = GL.GL_POINT_SMOOTH_HINT
    PolygonSmoothHint = GL.GL_POLYGON_SMOOTH_HINT
    TextureCompressionHint = GL.GL_TEXTURE_COMPRESSION_HINT
    MultisampleFilterNvHint = 0x8534


class NvidiaIntegerName(enum.IntEnum):
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


class PixelType(enum.IntEnum):
    UnsignedByte = GL.GL_UNSIGNED_BYTE
    Byte = GL.GL_BYTE
    UnsignedShort = GL.GL_UNSIGNED_SHORT
    Short = GL.GL_SHORT
    UnsignedInt = GL.GL_UNSIGNED_INT
    Int = GL.GL_INT
    Float = GL.GL_FLOAT
    UnsignedByte332 = GL.GL_UNSIGNED_BYTE_3_3_2
    UnsignedByte233Rev = GL.GL_UNSIGNED_BYTE_2_3_3_REV
    UnsignedShort565 = GL.GL_UNSIGNED_SHORT_5_6_5
    UnsignedShort565Rev = GL.GL_UNSIGNED_SHORT_5_6_5_REV
    UnsignedShort4444 = GL.GL_UNSIGNED_SHORT_4_4_4_4
    UnsignedShort4444Rev = GL.GL_UNSIGNED_SHORT_4_4_4_4_REV
    UnsignedShort5551 = GL.GL_UNSIGNED_SHORT_5_5_5_1
    UnsignedShort1555Rev = GL.GL_UNSIGNED_SHORT_1_5_5_5_REV
    UnsignedInt8888 = GL.GL_UNSIGNED_INT_8_8_8_8
    UnsignedInt8888Rev = GL.GL_UNSIGNED_INT_8_8_8_8_REV
    UnsignedInt1010102 = GL.GL_UNSIGNED_INT_10_10_10_2
    UnsignedInt2101010Rev = GL.GL_UNSIGNED_INT_2_10_10_10_REV


class MinFilter(enum.IntEnum):
    Nearest = GL.GL_NEAREST
    Linear = GL.GL_LINEAR
    NearestMipmapNearest = GL.GL_NEAREST_MIPMAP_NEAREST
    NearestMipmapLinear = GL.GL_NEAREST_MIPMAP_LINEAR
    LinearMipmapNearest = GL.GL_LINEAR_MIPMAP_NEAREST
    LinearMipmapLinear = GL.GL_LINEAR_MIPMAP_LINEAR


class MagFilter(enum.IntEnum):
    Nearest = GL.GL_NEAREST
    Linear = GL.GL_LINEAR


class AttachmentPoint(enum.IntEnum):
    ColorAttachment = GL.GL_COLOR_ATTACHMENT0
    DepthAttachment = GL.GL_DEPTH_ATTACHMENT
    StencilAttachment = GL.GL_STENCIL_ATTACHMENT
    DepthStencilAttachment = GL.GL_DEPTH_STENCIL_ATTACHMENT


class WrapMode(enum.IntEnum):
    Repeat = GL.GL_REPEAT
    MirroredRepeat = GL.GL_MIRRORED_REPEAT
    ClampToEdge = GL.GL_CLAMP_TO_EDGE
    MirrorClampToEdge = GL.GL_MIRROR_CLAMP_TO_EDGE
    ClampToBorder = GL.GL_CLAMP_TO_BORDER


class PrimitiveMode(enum.IntEnum):
    Triangles = GL.GL_TRIANGLES
    Points = GL.GL_POINTS
    LineStrip = GL.GL_LINE_STRIP
    LineLoop = GL.GL_LINE_LOOP
    Lines = GL.GL_LINES
    LineStripAdjacency = GL.GL_LINE_STRIP_ADJACENCY
    LinesAdjacency = GL.GL_LINES_ADJACENCY
    TriangleStrip = GL.GL_TRIANGLE_STRIP
    TriangleFan = GL.GL_TRIANGLE_FAN
    TriangleStripAdjacency = GL.GL_TRIANGLE_STRIP_ADJACENCY
    TrianglesAdjacency = GL.GL_TRIANGLES_ADJACENCY
    Patches = GL.GL_PATCHES


class BlendFactor(enum.IntEnum):
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


class DebugSeverity(enum.IntEnum):
    High = GL.GL_DEBUG_SEVERITY_HIGH
    Medium = GL.GL_DEBUG_SEVERITY_MEDIUM
    Low = GL.GL_DEBUG_SEVERITY_LOW
    Notification = GL.GL_DEBUG_SEVERITY_NOTIFICATION


class DebugSource(enum.IntEnum):
    Api = GL.GL_DEBUG_SOURCE_API
    WindowSystem = GL.GL_DEBUG_SOURCE_WINDOW_SYSTEM
    ShaderCompiler = GL.GL_DEBUG_SOURCE_SHADER_COMPILER
    ThirdParty = GL.GL_DEBUG_SOURCE_THIRD_PARTY
    Application = GL.GL_DEBUG_SOURCE_APPLICATION
    Other = GL.GL_DEBUG_SOURCE_OTHER


class DebugType(enum.IntEnum):
    Error = GL.GL_DEBUG_TYPE_ERROR
    DeprecatedBehaviour = GL.GL_DEBUG_TYPE_DEPRECATED_BEHAVIOR
    UndefinedBehaviour = GL.GL_DEBUG_TYPE_UNDEFINED_BEHAVIOR
    Portability = GL.GL_DEBUG_TYPE_PORTABILITY
    Performance = GL.GL_DEBUG_TYPE_PERFORMANCE
    Marker = GL.GL_DEBUG_TYPE_MARKER
    PushGroup = GL.GL_DEBUG_TYPE_PUSH_GROUP
    PopGroup = GL.GL_DEBUG_TYPE_POP_GROUP
    Other = GL.GL_DEBUG_TYPE_OTHER


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
    BaseLevel = GL.GL_TEXTURE_BASE_LEVEL
    BorderColor = GL.GL_TEXTURE_BORDER_COLOR
    CompareFunc = GL.GL_TEXTURE_COMPARE_FUNC
    CompareMode = GL.GL_TEXTURE_COMPARE_MODE
    LodBias = GL.GL_TEXTURE_LOD_BIAS
    MinFilter = GL.GL_TEXTURE_MIN_FILTER
    MagFilter = GL.GL_TEXTURE_MAG_FILTER
    MinLod = GL.GL_TEXTURE_MIN_LOD
    MaxLod = GL.GL_TEXTURE_MAX_LOD
    MaxLevel = GL.GL_TEXTURE_MAX_LEVEL
    SwizzleR = GL.GL_TEXTURE_SWIZZLE_R
    SwizzleG = GL.GL_TEXTURE_SWIZZLE_G
    SwizzleB = GL.GL_TEXTURE_SWIZZLE_B
    SwizzleA = GL.GL_TEXTURE_SWIZZLE_A
    SwizzleRgba = GL.GL_TEXTURE_SWIZZLE_RGBA
    WrapS = GL.GL_TEXTURE_WRAP_S
    WrapT = GL.GL_TEXTURE_WRAP_T
    WrapR = GL.GL_TEXTURE_WRAP_R


class TextureFormat(_TextureFormat):
    Red = GL.GL_RED
    Rg = GL.GL_RG
    Rgb = GL.GL_RGB
    Bgr = GL.GL_BGR
    Rgba = GL.GL_RGBA
    Bgra = GL.GL_BGRA
    DepthComponent = GL.GL_DEPTH_COMPONENT
    StencilIndex = GL.GL_STENCIL_INDEX


class SizedInternalFormat(_SizedInternalFormat):
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


class S3tcCompressedInternalFormat(_CompressedInternalFormat, _TextureFormat):
    CompressedRgbS3tcDxt1 = texture_compression_s3tc.GL_COMPRESSED_RGB_S3TC_DXT1_EXT
    CompressedRgbaS3tcDxt1 = texture_compression_s3tc.GL_COMPRESSED_RGBA_S3TC_DXT1_EXT
    CompressedRgbaS3tcDxt3 = texture_compression_s3tc.GL_COMPRESSED_RGBA_S3TC_DXT3_EXT
    CompressedRgbaS3tcDxt5 = texture_compression_s3tc.GL_COMPRESSED_RGBA_S3TC_DXT5_EXT


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
    TessEvaluationShader = GL.GL_TESS_EVALUATION_SHADER
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


class ClearMask(enum.IntEnum):
    ColorBufferBit = GL.GL_COLOR_BUFFER_BIT
    DepthBufferBit = GL.GL_DEPTH_BUFFER_BIT
    StencilBufferBit = GL.GL_STENCIL_BUFFER_BIT
    # TODO: Add rest of masks


class PolygonMode(enum.IntEnum):
    Line = GL.GL_LINE
    Fill = GL.GL_FILL
    Point = GL.GL_POINT