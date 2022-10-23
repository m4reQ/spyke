import enum

from OpenGL import GL


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

class ShaderType(enum.IntEnum):
    ComputeShader = GL.GL_COMPUTE_SHADER
    VertexShader = GL.GL_VERTEX_SHADER
    TessControlShader = GL.GL_TESS_CONTROL_SHADER
    TessEvaluationShader = GL.GL_TESS_EVALUATION_SHADER
    GeometryShader = GL.GL_GEOMETRY_SHADER
    FragmentShader = GL.GL_FRAGMENT_SHADER

class ClearMask(enum.IntEnum):
    ColorBufferBit = GL.GL_COLOR_BUFFER_BIT
    DepthBufferBit = GL.GL_DEPTH_BUFFER_BIT
    StencilBufferBit = GL.GL_STENCIL_BUFFER_BIT
    AccumBufferBit = GL.GL_ACCUM_BUFFER_BIT

class PolygonMode(enum.IntEnum):
    Line = GL.GL_LINE
    Fill = GL.GL_FILL
    Point = GL.GL_POINT

class BufferTarget(enum.IntEnum):
    _None = 0
    ArrayBuffer = GL.GL_ARRAY_BUFFER
    ElementArrayBuffer = GL.GL_ELEMENT_ARRAY_BUFFER
    CopyReadBuffer = GL.GL_COPY_READ_BUFFER
    CopyWriteBuffer = GL.GL_COPY_WRITE_BUFFER
    PixelUnpackBuffer = GL.GL_PIXEL_UNPACK_BUFFER
    PixelPackBuffer = GL.GL_PIXEL_PACK_BUFFER
    QueryBuffer = GL.GL_QUERY_BUFFER
    TextureBuffer = GL.GL_TEXTURE_BUFFER
    TransformFeedbackBuffer = GL.GL_TRANSFORM_FEEDBACK_BUFFER
    UniformBuffer = GL.GL_UNIFORM_BUFFER
    DrawIndirectBuffer = GL.GL_DRAW_INDIRECT_BUFFER
    AtomicCounterBuffer = GL.GL_ATOMIC_COUNTER_BUFFER
    DispatchIndirectBuffer = GL.GL_DISPATCH_INDIRECT_BUFFER
    ShaderStorageBuffer = GL.GL_SHADER_STORAGE_BUFFER

class BufferStorageFlags(enum.IntEnum):
    _None = 0
    DynamicStorageBit = GL.GL_DYNAMIC_STORAGE_BIT
    MapReadBit = GL.GL_MAP_READ_BIT
    MapWriteBit = GL.GL_MAP_WRITE_BIT
    MapPersistentBit = GL.GL_MAP_PERSISTENT_BIT
    MapCoherentBit = GL.GL_MAP_COHERENT_BIT
    ClientStorageBit = GL.GL_CLIENT_STORAGE_BIT

class TextureFormat(enum.IntEnum):
    Red = GL.GL_RED
    Rg = GL.GL_RG
    Rgb = GL.GL_RGB
    Bgr = GL.GL_BGR
    Rgba = GL.GL_RGBA
    Bgra = GL.GL_BGRA
    DepthComponent = GL.GL_DEPTH_COMPONENT
    StencilIndex = GL.GL_STENCIL_INDEX

class ProgramInterface(enum.IntEnum):
    ActiveResources = GL.GL_ACTIVE_RESOURCES
    MaxNameLength = GL.GL_MAX_NAME_LENGTH
    MaxNumActiveVariables = GL.GL_MAX_NUM_ACTIVE_VARIABLES
    MaxNumCompatibleSubRoutines = GL.GL_MAX_NUM_COMPATIBLE_SUBROUTINES
