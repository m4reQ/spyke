import enum
import typing as t
from collections.abc import Buffer as SupportsBufferProtocol

from spyke.math import Vector4

class EnableCap(enum.IntEnum):
    BLEND = t.cast(int, ...)
    CLIP_DISTANCE0 = t.cast(int, ...)
    CLIP_DISTANCE1 = t.cast(int, ...)
    CLIP_DISTANCE2 = t.cast(int, ...)
    CLIP_DISTANCE3 = t.cast(int, ...)
    CLIP_DISTANCE4 = t.cast(int, ...)
    CLIP_DISTANCE5 = t.cast(int, ...)
    CLIP_DISTANCE6 = t.cast(int, ...)
    CLIP_DISTANCE7 = t.cast(int, ...)
    COLOR_LOGIC_OP = t.cast(int, ...)
    CULL_FACE = t.cast(int, ...)
    DEBUG_OUTPUT = t.cast(int, ...)
    DEBUG_OUTPUT_SYNCHRONOUS = t.cast(int, ...)
    DEPTH_CLAMP = t.cast(int, ...)
    DEPTH_TEST = t.cast(int, ...)
    DITHER = t.cast(int, ...)
    FRAMEBUFFER_SRGB = t.cast(int, ...)
    LINE_SMOOTH = t.cast(int, ...)
    MULTISAMPLE = t.cast(int, ...)
    POLYGON_OFFSET_FILL = t.cast(int, ...)
    POLYGON_OFFSET_LINE = t.cast(int, ...)
    POLYGON_OFFSET_POINT = t.cast(int, ...)
    POLYGON_SMOOTH = t.cast(int, ...)
    PRIMITIVE_RESTART = t.cast(int, ...)
    PRIMITIVE_RESTART_FIXED_INDEX = t.cast(int, ...)
    RASTERIZER_DISCARD = t.cast(int, ...)
    SAMPLE_ALPHA_TO_COVERAGE = t.cast(int, ...)
    SAMPLE_ALPHA_TO_ONE = t.cast(int, ...)
    SAMPLE_COVERAGE = t.cast(int, ...)
    SAMPLE_SHADING = t.cast(int, ...)
    SAMPLE_MASK = t.cast(int, ...)
    SCISSOR_TEST = t.cast(int, ...)
    STENCIL_TEST = t.cast(int, ...)
    TEXTURE_CUBE_MAP_SEAMLESS = t.cast(int, ...)
    PROGRAM_POINT_SIZE = t.cast(int, ...)

class GLType(enum.IntEnum):
    BYTE = t.cast(int, ...)
    UNSIGNED_BYTE = t.cast(int, ...)
    SHORT = t.cast(int, ...)
    UNSIGNED_SHORT = t.cast(int, ...)
    INT = t.cast(int, ...)
    UNSIGNED_INT = t.cast(int, ...)
    FIXED = t.cast(int, ...)
    HALF_FLOAT = t.cast(int, ...)
    FLOAT = t.cast(int, ...)
    DOUBLE = t.cast(int, ...)

class BufferTarget(enum.IntEnum):
    '''Specifies the target to which the buffer object is bound'''

    ARRAY_BUFFER = t.cast(int, ...)
    '''Vertex attributes'''

    ATOMIC_COUNTER_BUFFER = t.cast(int, ...)
    '''Atomic counter storage'''

    COPY_READ_BUFFER = t.cast(int, ...)
    '''Buffer copy source'''

    COPY_WRITE_BUFFER = t.cast(int, ...)
    '''Buffer copy destination'''

    DISPATCH_INDIRECT_BUFFER = t.cast(int, ...)
    '''Indirect compute dispatch commands'''

    DRAW_INDIRECT_BUFFER = t.cast(int, ...)
    '''Indirect command arguments'''

    ELEMENT_ARRAY_BUFFER = t.cast(int, ...)
    '''Vertex array indices'''

    PIXEL_PACK_BUFFER = t.cast(int, ...)
    '''Pixel read target'''

    PIXEL_UNPACK_BUFFER = t.cast(int, ...)
    '''Texture data source'''

    QUERY_BUFFER = t.cast(int, ...)
    '''Query result buffer'''

    SHADER_STORAGE_BUFFER = t.cast(int, ...)
    '''Read-write storage for shaders'''

    TEXTURE_BUFFER = t.cast(int, ...)
    '''Texture data buffer'''

    TRANSFORM_FEEDBACK_BUFFER = t.cast(int, ...)
    '''Transform feedback buffer'''

    UNIFORM_BUFFER = t.cast(int, ...)
    '''Uniform block storage'''

class BufferBaseTarget(enum.IntEnum):
    '''Specify the target of the bind operation'''

    ATOMIC_COUNTER_BUFFER = t.cast(int, ...)
    '''Atomic counter storage'''

    TRANSFORM_FEEDBACK_BUFFER = t.cast(int, ...)
    '''Transform feedback buffer'''

    UNIFORM_BUFFER = t.cast(int, ...)
    '''Uniform block storage'''

    SHADER_STORAGE_BUFFER = t.cast(int, ...)
    '''Read-write storage for shaders'''

class BufferFlag(enum.IntFlag):
    '''Specifies the intended usage of the buffer's data store.'''

    DYNAMIC_STORAGE_BIT = t.cast(int, ...)
    '''
    The contents of the data store may be updated after creation through calls to glBufferSubData.
    If this bit is not set, the buffer content may not be directly updated by the client.
    The data argument may be used to specify the initial content of the buffer's data store
    regardless of the presence of the GL_DYNAMIC_STORAGE_BIT.
    Regardless of the presence of this bit, buffers may always be updated with server-side
    calls such as glCopyBufferSubData and glClearBufferSubData.
    '''

    MAP_READ_BIT = t.cast(int, ...)
    '''
    The data store may be mapped by the client for read access and a pointer in the client's
    address space obtained that may be read from.
    '''

    MAP_WRITE_BIT = t.cast(int, ...)
    '''
    The data store may be mapped by the client for write access and a pointer in the client's
    address space obtained that may be written through.
    '''

    MAP_PERSISTENT_BIT = t.cast(int, ...)
    '''
    The client may request that the server read from or write to the buffer while it is mapped.
    The client's pointer to the data store remains valid so long as the data store is mapped,
    even during execution of drawing or dispatch commands.
    '''

    MAP_COHERENT_BIT = t.cast(int, ...)
    '''
    Shared access to buffers that are simultaneously mapped for client access
    and are used by the server will be coherent, so long as that mapping is performed
    using glMapBufferRange. That is, data written to the store by either the client or server
    will be immediately visible to the other with no further action taken by the application.
    '''

    CLIENT_STORAGE_BIT = t.cast(int, ...)
    '''
    When all other criteria for the buffer storage allocation are met,
    this bit may be used by an implementation to determine whether to use storage
    that is local to the server or to the client to serve as the backing store for the buffer.
    '''

    NONE = t.cast(int, ...)
    '''No specific buffer flags are applied.'''

class Buffer:
    '''
    A wrapper for OpenGL buffer objects, supporting various storage methods.
    '''

    current_offset: int
    '''Current data offset used when storing new data'''

    @staticmethod
    def unbind(target: BufferTarget) -> None:
        '''
        Unbinds any buffer bound to the `target`, settings its binding to 0.

        :param target: Buffer target which will be unbound.
        '''

    def __init__(self,
                 size: int,
                 flags: BufferFlag,
                 data: SupportsBufferProtocol | None = None) -> None:
        '''
        Creates new buffer with size of `size` bytes. If the data argument is specified, the buffer
        will be populated with the provided data. If the data size is greater than the `size` parameter
        an error will be generated. This function uses `glBufferStorage` API (see: https://registry.khronos.org/OpenGL-Refpages/gl4/html/glBufferStorage.xhtml).
        Buffer constructor checks for rough validity of the `flags` argument, to ensure that operations issued
        during buffer creation will not result in crash. However, it doesn't check for incorrect usage scenarios
        that might generate errors during buffer usage.

        :param size: Size of the buffer to be created. In bytes.
        :param flags: Flags specifying buffer behavior. See `BufferFlag`.
        :param data: Initial buffer data.

        :raises ValueError: If the data is bigger than declared buffer size.
        :raises ValueError: When provided flags would result in invalid buffer.
        '''

    def delete(self) -> None:
        '''
        Deletes the buffer.
        '''

    def bind(self, target: BufferTarget) -> None:
        '''
        Binds buffer to the specified target, using `glBindBuffer`.
        See https://registry.khronos.org/OpenGL-Refpages/gl4/html/glBindBuffer.xhtml.

        :param target: A target to which the buffer should be bound (see: `BufferTarget`).
        '''

    def bind_base(self, target: BufferBaseTarget, index: int, /) -> None:
        '''
        Binds buffer object to an indexed buffer target.
        See https://registry.khronos.org/OpenGL-Refpages/gl4/html/glBindBufferBase.xhtml.

        :param target: A target to which the buffer should be bound (see: `BufferBaseTarget`).
        :param index: Binding index.

        :raises ValueError: If index is negative.
        '''

    @t.overload
    def write(self, data: SupportsBufferProtocol, offset: int = ..., alignment: int = ...) -> None:
        '''
        Stores data inside GPU or the host memory, depending on the settings.
        If the offset is not specified, data will be stored at the current end pointer.
        Warning: For the sake of performance, this function does not check if the buffer is writable. Trying to
        write data to a read-only buffer will most likely result in a crash.

        :param data: An object supporting buffer protocol.
        :param offset: Offset from the buffer beginning, at which to store data. Defaults to buffer end.

        :raises RuntimeError: If trying to store data at provided offset would result in buffer overflow. (data size + offset > buffer size)
        :raises RuntimeError: If the buffer uses mapping and was not mapped prior to the operation.
        '''

    @t.overload
    def write(self, data: int, offset: int = ..., alignment: int = ...) -> None:
        '''
        Stores data inside GPU or the host memory, depending on the settings.
        If the offset is not specified, data will be stored at the current end pointer.
        Warning: For the sake of performance, this function does not check if the buffer is writable. Trying to
        write data to a read-only buffer will most likely result in a crash.

        :param data: An integer value, interpreted as `uint32_t`.
        :param offset: Offset from the buffer beginning, at which to store data. Defaults to buffer end.

        :raises RuntimeError: If trying to store data at provided offset would result in buffer overflow. (offset + sizeof(uint32_t) > buffer size)
        :raises RuntimeError: If the buffer uses mapping and was not mapped prior to the operation.
        '''

    @t.overload
    def write(self, data: float, offset: int = ..., alignment: int = ...) -> None:
        '''
        Stores data inside GPU or the host memory, depending on the settings.
        If the offset is not specified, data will be stored at the current end pointer.
        Warning: For the sake of performance, this function does not check if the buffer is writable. Trying to
        write data to a read-only buffer will most likely result in a crash.

        :param data: A float value, interpreted as `float`.
        :param offset: Offset from the buffer beginning, at which to store data. Defaults to buffer end.

        :raises RuntimeError: If trying to store data at provided offset would result in buffer overflow. (offset + sizeof(float) > buffer size)
        :raises RuntimeError: If the buffer uses mapping and was not mapped prior to the operation.
        '''

    def write_address(self, address: int, size: int, offset: int = ..., alignment: int = ...) -> None:
        '''
        Stores `size` bytes of data, pointed to by `address` inside GPU or host memory, depending on the settings.
        If the offset is not specified, data will be stored at the current end pointer.
        Warning: For the sake of performance, this function does not check if the buffer is writable. Trying to
        write data to a read-only buffer will most likely result in a crash.

        :param data: An integer pointing to the data memory. Interpreted as `void*`.
        :param size: Number of bytes to be copied from `address`.
        :param offset: Offset from the buffer beginning, at which to store data. Defaults to buffer end.

        :raises RuntimeError: If trying to store data at provided offset would result in buffer overflow. (offset + size > buffer size)
        :raises RuntimeError: If the buffer uses mapping and was not mapped prior to the operation.
        :raises ValueError: If address is 0.
        :raises ValueError: If size is negative or greater than buffer size.
        :raises ValueError: If offset is negative or greater than buffer size.
        '''

    def transfer(self) -> int:
        '''
        Transfers host-cached memory to OpenGL.
        Depending on the flags used during buffer creation this function
        might not do anything. The function will also do nothing if there was
        no data stored prior to the call. This function also resets data pointer.
        To ensure consistency, if the buffer uses non-persistent mapping,
        this function will unmap buffer even if no data was stored.

        :returns: An amount of bytes transfered to GPU since last data pointer reset.
        '''

    def reset_data_offset(self) -> None:
        '''
        Resets data pointer without storing data in the buffer. Note that for buffers
        that use mapping, the data is already transferred and this only resets internal
        data pointer. This function will not unmap mapped buffers, to do this use `Buffer.transfer`.
        '''

    def map(self) -> None:
        '''
        If the buffer was configure to use non-persistent mapping, calling this function is required
        before trying to store any data. If the buffer is already mapped or the buffer does not use mapping
        at all, this function does nothing.

        :raises RuntimeError: When OpenGL failed to map the buffer.
        '''

    def read(self, out: SupportsBufferProtocol, size: int = ..., offset: int = ...) -> None:
        '''
        Reads `size` amount of bytes to a `out` writable object, that supports buffer protocol. An offset
        may be specified, defaults to the beginning of the buffer. The `size` parameter might be omitted,
        in which case size of the data to be read will be inferred from the provided object.
        Note: the output object's buffer must be C-contiguous.
        Depending on the flags specified it might be required to call `Buffer.map` before reading.

        :param out: A writable object, that supports buffer protocol, capable of storing `size` bytes.
        :param size: An amount of bytes to be read.
        :param offset: An offset from the beginning of the buffer, defaults to 0.

        :raises RuntimeError: If the size exported by the object's buffer protocol is smaller than declared size.
        :raises RuntimeError: If trying to read from the buffer would cause in buffer underflow (size + offset > buffer size)
        :raises RuntimeError: If the buffer is not readable.
        :raises RuntimeError: If the buffer uses non-persistent mapping and was not mapped before reading.
        :raises ValueError: If the provided object's buffer is not C-contiguous.
        '''

    def can_store_data(self, data_size: int, /) -> bool: ...

    def set_debug_name(self, name: str, /) -> None: ...

    @property
    def id(self) -> int:
        '''OpenGL object ID.'''

    @property
    def size(self) -> int:
        '''Buffer size in bytes.'''

class Sync:
    '''
    A wrapper for OpenGL sync objects.
    '''

    def set(self) -> None:
        '''
        Issues GPU sync that will become signaled after all
        previous GPU commands have finished.
        See https://registry.khronos.org/OpenGL-Refpages/gl4/html/glFenceSync.xhtml for more details.
        '''

    def wait(self, timeout: int = 0) -> bool:
        '''
        Waits for `timeout` milliseconds for the sync object to
        become signaled. If object becomes signaled during this call
        the function returns `True`, otherwise it returns `False`.
        If `timeout` is set to 0 this function waits infinitely.
        If the sync was not previously set, this function returns `True` immediately.

        :param timeout: Timeout in milliseconds for which to wait until sync becomes signaled.
        '''

    def delete(self) -> None:
        '''
        Deletes the sync object.
        '''

    def is_signaled(self) -> bool:
        '''
        Checks if sync is already in a signaled state.
        This function does not wait for any time and can be used
        for efficient polling for sync state.
        '''

    def set_debug_name(self, name: str, /) -> None: ...

class ShaderType(enum.IntEnum):
    '''
    Used to specify type of the created shader.
    '''

    FRAGMENT_SHADER = t.cast(int, ...)
    VERTEX_SHADER = t.cast(int, ...)
    GEOMETRY_SHADER = t.cast(int, ...)
    COMPUTE_SHADER = t.cast(int, ...)
    TESS_CONTROL_SHADER = t.cast(int, ...)
    TESS_EVALUATION_SHADER = t.cast(int, ...)

class ShaderSpecializeInfo:
    '''
    Structure used to specialize SPIR-V shaders loaded from binary.
    '''

    def __init__(self, entry_point: str, constants: list[tuple[int, int]]) -> None:
        '''
        Describes specialization info used by `glSpecializeShader` when loading SPIR-V binary
        shaders. See: https://www.khronos.org/opengl/wiki/SPIR-V/Compilation for more info about
        loading and using SPIR-V shaders in OpenGL.
        '''

        self.entry_point: str
        '''Name of the shader entry point, called during shader invocation.'''

        self.constants: list[tuple[int, int]]
        '''List of specialization constants.'''

class ShaderBinaryFormat(enum.IntEnum):
    SHADER_BINARY_FORMAT_SPIR_V = t.cast(int, ...)

class ShaderStageInfo:
    '''
    A structure describing how to create a shader, that will be later used during shader program linkage.
    Note that this class doesn't create any shaders and just describes how to create them.
    '''

    type: int
    '''Type of the shader to be created.'''

    filepath_or_source: str
    '''Path to the file from which shader code will be loaded or the shader source itself.'''

    binary_format: int
    '''In case of loading shader from binary data, indicates the format of loaded binary.'''

    specialize_info: ShaderSpecializeInfo | None
    '''Specialization info used when loading SPIR-V binary shaders.'''

    @classmethod
    def from_file(cls,
                  type: ShaderType,
                  filepath: str,
                  use_binary: bool = False,
                  specialize_info: ShaderSpecializeInfo | None = None) -> t.Self:
        '''
        Describes shader of type specified by `type` parameter, that is loaded from given filepath.
        If the `use_binary` parameter is set, the file is considered to be containing binary shader code.
        Not all drivers support binary shaders and trying to load binary on machine that doesn't support it
        will result in an error during shader program creation. If a SPIR-V shader is loaded, user has to provide
        specialization info that will be used to properly initialize shader.

        :param type: Type of shader to be created. See: https://registry.khronos.org/OpenGL-Refpages/gl4/html/glCreateShader.xhtml
        :param filepath: A path to the file containing source code or compiled binary.
        :param use_binary: Indicates if the file contains binary data.
        :param specialize_info: Specialization info for SPIR-V shaders. Unused for standard GLSL source shaders.
        '''

    @classmethod
    def from_source(cls, type: ShaderType, source: str) -> t.Self:
        '''
        Describes shader of type specified by `type` parameter, that is created using provided `source`.
        The source is GLSL code that will be compiled during shader program creation.

        :param type: Type of shader to be created. See: https://registry.khronos.org/OpenGL-Refpages/gl4/html/glCreateShader.xhtml
        :param source: GLSL source code used to compile shader.
        '''

    @classmethod
    def from_binary(cls,
                    type: ShaderType,
                    binary: SupportsBufferProtocol,
                    binary_format: ShaderBinaryFormat | int,
                    specialize_info: ShaderSpecializeInfo) -> t.Self: ...

class UniformType(enum.IntEnum):
    '''Used to specify types of the shader program uniform values'''

    FLOAT = t.cast(int, ...)
    DOUBLE = t.cast(int, ...)
    INT = t.cast(int, ...)
    UNSIGNED_INT = t.cast(int, ...)

UniformValue = int | float
class ShaderProgram:
    '''
    A wrapper for OpenGL shader programs, capable of creating binary
    and source shaders as well as configuring them and retrieving informations.
    '''

    @classmethod
    def from_binary(cls, binary: SupportsBufferProtocol, type: int) -> t.Self:
        '''
        Creates new shader program from the specified binary.
        Some OpenGL implementations allow to retrieve and load compiled program binary
        to speed up program creation. Program binary can be retrieved using `ShaderProgram.get_binary`.

        :param binary: Shader program binary to be loaded.
        :param type: Token specifying binary type.

        :raises RuntimeError: If loading shader programs from binary is not supported.
        :raises RuntimeError: If OpenGL failed to create shader program from specified binary.
        '''

    def __init__(self, stages: list[ShaderStageInfo]) -> None:
        '''
        Creates new shader program with the specified list of stages. Each stage is created
        separately either by loading its' binary or compiling it from source. Program is then linked
        together. All shaders created during program linking are automatically cleaned up before this
        function finishes.

        :param stages: A list of shaders to be linked into the program.

        :raises RuntimeError: When compilation of one of the shaders fails.
        :raises RuntimeError: When a program linking fails.
        :raises IOError: When one of the shader source files could not be found.
        '''

    def delete(self) -> None:
        '''
        Deletes the shader program.
        '''

    def use(self) -> None:
        '''
        Installs a program object as part of current rendering state.
        See: https://registry.khronos.org/OpenGL-Refpages/gl4/html/glUseProgram.xhtml.
        '''

    def validate(self) -> None:
        '''
        Validates a program against current OpenGL state.
        See: https://registry.khronos.org/OpenGL-Refpages/gl4/html/glValidateProgram.xhtml.
        '''

    def set_uniform_block_binding(self, name: str, binding: int, /) -> None:
        '''
        Binds uniform block with a given name to a specified binding index.
        See: https://registry.khronos.org/OpenGL-Refpages/gl4/html/glUniformBlockBinding.xhtml.

        :param name: Name of the uniform block to be bound.
        :param binding: Binding index.

        :raises RuntimeError: If uniform block with given name was not found.
        '''

    def set_uniform(self, name: str, value: UniformValue, type: UniformType, /) -> None:
        '''
        Sets program uniform with a specified name, to the given value.
        The value is converted to a specified type before being sent to the program.
        If value is of type `float` it will be interpreted as `double` C type. If value
        is `int` it will be interpreted as `int64_t` (64-bit signed integer) C type.

        :param name: Name of the uniform to be set.
        :param value: A value used to set the uniform.
        :param type: OpenGL type to which the provided value be converted.

        :raises RuntimeError: If uniform with given name could not be found.
        :raises ValueError: If invalid uniform type is specified.
        '''

    @t.overload
    def set_uniform_array(self,
                          name: str,
                          values: SupportsBufferProtocol,
                          type: UniformType) -> None:
        '''
        Sets program array uniform with a specified name using provided values.
        Values are interpreted according to the given `type`. The amount of values is determined
        by the buffer exported by `values` object. This function does not check if provided data is
        correct.

        :param name: Name of the uniform to be set.
        :param values: An object exporting buffer of values to be used.
        :param type: OpenGL type to which the provided values be converted.

        :raises ValueError: If invalid uniform type is specified.
        :raises RuntimeError: If uniform with given name could not be found.
        :raises RuntimeError: If item size calculated from uniform type doesn't match item size of provided buffer.
        '''

    @t.overload
    def set_uniform_array(self,
                          name: str,
                          values: list[UniformValue],
                          type: UniformType) -> None:
        '''
        Sets program array uniform with a specified name using provided values.
        Values are interpreted according to the given `type`.
        This function does not check if provided data is correct.

        :param name: Name of the uniform to be set.
        :param values: A list of values to be used.
        :param type: OpenGL type to which the provided values be converted.
        '''

    @t.overload
    def set_uniform_vec2(self, name: str, type: UniformType, value: SupportsBufferProtocol, /) -> None:
        '''
        Set a `vec2` uniform for the shader program using values from the buffer exported by `value` object.
        Values are converted according to the provided `type`.

        :param name: The name of the uniform variable in the shader program.
        :param value: An object that exports the values buffer.
        :param type: The type of the uniform.

        :raises ValueError: If the buffer exported by `value` object is not 2 items long.
        '''

    @t.overload
    def set_uniform_vec2(self, name: str, type: UniformType, v0: UniformValue, v1: UniformValue, /) -> None:
        '''
        Set a `vec2` uniform for the shader program using provided values.
        Values are converted according to the specified `type`.

        :param name: The name of the uniform variable in the shader program.
        :param v0: First value.
        :param v1: Second value.
        :param type: The type of the uniform.
        '''

    @t.overload
    def set_uniform_vec3(self, name: str, type: UniformType, value: SupportsBufferProtocol, /) -> None:
        '''
        Set a `vec3` uniform for the shader program using values from the buffer exported by `value` object.
        Values are converted according to the provided `type`.

        :param name: The name of the uniform variable in the shader program.
        :param value: An object that exports the values buffer.
        :param type: The type of the uniform.

        :raises ValueError: If the buffer exported by `value` object is not 3 items long.
        '''

    @t.overload
    def set_uniform_vec3(self, name: str, type: UniformType, v0: UniformValue, v1: UniformValue, v2: UniformValue, /) -> None:
        '''
        Set a `vec3` uniform for the shader program using provided values.
        Values are converted according to the specified `type`.

        :param name: The name of the uniform variable in the shader program.
        :param v0: First value.
        :param v1: Second value.
        :param v2: Third value.
        :param type: The type of the uniform.
        '''

    @t.overload
    def set_uniform_vec4(self, name: str, type: UniformType, value: SupportsBufferProtocol, /) -> None:
        '''
        Set a `vec4` uniform for the shader program using values from the buffer exported by `value` object.
        Values are converted according to the provided `type`.

        :param name: The name of the uniform variable in the shader program.
        :param value: An object that exports the values buffer.
        :param type: The type of the uniform.

        :raises ValueError: If the buffer exported by `value` object is not 4 items long.
        '''

    @t.overload
    def set_uniform_vec4(self, name: str, type: UniformType, v0: UniformValue, v1: UniformValue, v2: UniformValue, v3: UniformValue, /) -> None:
        '''
        Set a `vec4` uniform for the shader program using provided values.
        Values are converted according to the specified `type`.

        :param name: The name of the uniform variable in the shader program.
        :param v0: First value.
        :param v1: Second value.
        :param v2: Third value.
        :param v3: Forth value.
        :param type: The type of the uniform.
        '''

    def set_uniform_mat2(self, name: str, type: UniformType, value: SupportsBufferProtocol, transpose: bool, /) -> None:
        '''
        Set a `mat2` uniform for the shader program using values buffer exported by the `value` object.
        Values are converted according to the specified OpenGL uniform type. If `transpose` is set to True
        provided matrix will be transposed prior to sending to the shader program.

        :param name: The name of the uniform variable in the shader program.
        :param value: A value to be set.
        :param type: The type of the uniform.
        :param transpose: Indicates if the matrix should be transposed.

        :raises ValueError: If the buffer exported by `value` object doesn't have required amount of elements.
        '''

    def set_uniform_mat3(self, name: str, type: UniformType, value: SupportsBufferProtocol, transpose: bool, /) -> None:
        '''
        Set a `mat3` uniform for the shader program using values buffer exported by the `value` object.
        Values are converted according to the specified OpenGL uniform type. If `transpose` is set to True
        provided matrix will be transposed prior to sending to the shader program.

        :param name: The name of the uniform variable in the shader program.
        :param value: A value to be set.
        :param type: The type of the uniform.
        :param transpose: Indicates if the matrix should be transposed.

        :raises ValueError: If the buffer exported by `value` object doesn't have required amount of elements.
        '''

    def set_uniform_mat4(self, name: str, type: UniformType, value: SupportsBufferProtocol, transpose: bool, /) -> None:
        '''
        Set a `mat4` uniform for the shader program using values buffer exported by the `value` object.
        Values are converted according to the specified OpenGL uniform type. If `transpose` is set to True
        provided matrix will be transposed prior to sending to the shader program.

        :param name: The name of the uniform variable in the shader program.
        :param value: A value to be set.
        :param type: The type of the uniform.
        :param transpose: Indicates if the matrix should be transposed.

        :raises ValueError: If the buffer exported by `value` object doesn't have required amount of elements.
        '''

    def get_binary(self) -> tuple[bytes, int]:
        '''
        Retrieves shader program binary that can be used next time the program is loaded to decrease load time.
        This function returns tuple containing binary data as well as the token indicating binary format.

        :raises RuntimeError: If shader program binaries are not supported by the current OpenGL implementation.
        '''

    def set_debug_name(self, name: str, /) -> None: ...

    @property
    def id(self) -> int:
        '''OpenGL object id.'''

    @property
    def uniforms(self) -> dict[str, int]:
        '''A dictionary of uniform name to id mapping.'''

    @property
    def attributes(self) -> dict[str, int]:
        '''A dictionary of attribute name to id mapping.'''

class TextureTarget(enum.IntEnum):
    TEXTURE_1D = t.cast(int, ...)
    TEXTURE_2D = t.cast(int, ...)
    TEXTURE_3D = t.cast(int, ...)
    TEXTURE_1D_ARRAY = t.cast(int, ...)
    TEXTURE_2D_ARRAY = t.cast(int, ...)
    TEXTURE_RECTANGLE = t.cast(int, ...)
    TEXTURE_CUBE_MAP = t.cast(int, ...)
    TEXTURE_CUBE_MAP_ARRAY = t.cast(int, ...)
    TEXTURE_BUFFER = t.cast(int, ...)
    TEXTURE_2D_MULTISAMPLE = t.cast(int, ...)
    TEXTURE_2D_MULTISAMPLE_ARRAY = t.cast(int, ...)

class TextureParameter(enum.IntEnum):
    DEPTH_STENCIL_TEXTURE_MODE = t.cast(int, ...)
    TEXTURE_BASE_LEVEL = t.cast(int, ...)
    TEXTURE_BORDER_COLOR = t.cast(int, ...)
    TEXTURE_COMPARE_FUNC = t.cast(int, ...)
    TEXTURE_COMPARE_MODE = t.cast(int, ...)
    TEXTURE_LOD_BIAS = t.cast(int, ...)
    TEXTURE_MIN_FILTER = t.cast(int, ...)
    TEXTURE_MAG_FILTER = t.cast(int, ...)
    TEXTURE_MIN_LOD = t.cast(int, ...)
    TEXTURE_MAX_LOD = t.cast(int, ...)
    TEXTURE_MAX_LEVEL = t.cast(int, ...)
    TEXTURE_SWIZZLE_R = t.cast(int, ...)
    TEXTURE_SWIZZLE_G = t.cast(int, ...)
    TEXTURE_SWIZZLE_B = t.cast(int, ...)
    TEXTURE_SWIZZLE_A = t.cast(int, ...)
    TEXTURE_SWIZZLE_RGBA = t.cast(int, ...)
    TEXTURE_WRAP_S = t.cast(int, ...)
    TEXTURE_WRAP_T = t.cast(int, ...)
    TEXTURE_WRAP_R = t.cast(int, ...)

class MinFilter(enum.IntEnum):
    NEAREST = t.cast(int, ...)
    LINEAR = t.cast(int, ...)
    NEAREST_MIPMAP_NEAREST = t.cast(int, ...)
    LINEAR_MIPMAP_NEAREST = t.cast(int, ...)
    NEAREST_MIPMAP_LINEAR = t.cast(int, ...)
    LINEAR_MIPMAP_LINEAR = t.cast(int, ...)

class MagFilter(enum.IntEnum):
    NEAREST = t.cast(int, ...)
    LINEAR = t.cast(int, ...)

class WrapMode(enum.IntEnum):
    CLAMP_TO_EDGE = t.cast(int, ...)
    CLAMP_TO_BORDER = t.cast(int, ...)
    MIRROR_CLAMP_TO_EDGE = t.cast(int, ...)
    REPEAT = t.cast(int, ...)
    MIRRORED_REPEAT = t.cast(int, ...)

class InternalFormat(enum.IntEnum):
    R8 = t.cast(int, ...)
    R8_SNORM = t.cast(int, ...)
    R16 = t.cast(int, ...)
    R16_SNORM = t.cast(int, ...)
    RG8 = t.cast(int, ...)
    RG8_SNORM = t.cast(int, ...)
    RG16 = t.cast(int, ...)
    RG16_SNORM = t.cast(int, ...)
    R3_G3_B2 = t.cast(int, ...)
    RGB4 = t.cast(int, ...)
    RGB5 = t.cast(int, ...)
    RGB8 = t.cast(int, ...)
    RGB8_SNORM = t.cast(int, ...)
    RGB10 = t.cast(int, ...)
    RGB12 = t.cast(int, ...)
    RGB16 = t.cast(int, ...)
    RGB16_SNORM = t.cast(int, ...)
    RGBA2 = t.cast(int, ...)
    RGBA4 = t.cast(int, ...)
    RGB5_A1 = t.cast(int, ...)
    RGBA8 = t.cast(int, ...)
    RGBA8_SNORM = t.cast(int, ...)
    RGB10_A2 = t.cast(int, ...)
    RGB10_A2UI = t.cast(int, ...)
    RGBA12 = t.cast(int, ...)
    RGBA16 = t.cast(int, ...)
    SRGB8 = t.cast(int, ...)
    SRGB8_ALPHA8 = t.cast(int, ...)
    R16F = t.cast(int, ...)
    RG16F = t.cast(int, ...)
    RGB16F = t.cast(int, ...)
    RGBA16F = t.cast(int, ...)
    R32F = t.cast(int, ...)
    RG32F = t.cast(int, ...)
    RGB32F = t.cast(int, ...)
    RGBA32F = t.cast(int, ...)
    R11F_G11F_B10F = t.cast(int, ...)
    RGB9_E5 = t.cast(int, ...)
    R8I = t.cast(int, ...)
    R8UI = t.cast(int, ...)
    R16I = t.cast(int, ...)
    R16UI = t.cast(int, ...)
    R32I = t.cast(int, ...)
    R32UI = t.cast(int, ...)
    RG8I = t.cast(int, ...)
    RG8UI = t.cast(int, ...)
    RG16I = t.cast(int, ...)
    RG16UI = t.cast(int, ...)
    RG32I = t.cast(int, ...)
    RG32UI = t.cast(int, ...)
    RGB8I = t.cast(int, ...)
    RGB8UI = t.cast(int, ...)
    RGB16I = t.cast(int, ...)
    RGB16UI = t.cast(int, ...)
    RGB32I = t.cast(int, ...)
    RGB32UI = t.cast(int, ...)
    RGBA8I = t.cast(int, ...)
    RGBA8UI = t.cast(int, ...)
    RGBA16I = t.cast(int, ...)
    RGBA16UI = t.cast(int, ...)
    RGBA32I = t.cast(int, ...)
    RGBA32UI = t.cast(int, ...)

class CompressedInternalFormat(enum.IntEnum):
    COMPRESSED_RGB_S3TC_DXT1_EXT = t.cast(int, ...)
    COMPRESSED_RGBA_S3TC_DXT1_EXT = t.cast(int, ...)
    COMPRESSED_RGBA_S3TC_DXT3_EXT = t.cast(int, ...)
    COMPRESSED_RGBA_S3TC_DXT5_EXT = t.cast(int, ...)

class PixelFormat(enum.IntEnum):
    RED = t.cast(int, ...)
    RG = t.cast(int, ...)
    RGB = t.cast(int, ...)
    BGR = t.cast(int, ...)
    RGBA = t.cast(int, ...)
    BGRA = t.cast(int, ...)
    DEPTH_COMPONENT = t.cast(int, ...)
    STENCIL_INDEX = t.cast(int, ...)

class PixelType(enum.IntEnum):
    UNSIGNED_BYTE = t.cast(int, ...)
    BYTE = t.cast(int, ...)
    UNSIGNED_SHORT = t.cast(int, ...)
    SHORT = t.cast(int, ...)
    UNSIGNED_INT = t.cast(int, ...)
    INT = t.cast(int, ...)
    FLOAT = t.cast(int, ...)
    UNSIGNED_BYTE_3_3_2 = t.cast(int, ...)
    UNSIGNED_BYTE_2_3_3_REV = t.cast(int, ...)
    UNSIGNED_SHORT_5_6_5 = t.cast(int, ...)
    UNSIGNED_SHORT_5_6_5_REV = t.cast(int, ...)
    UNSIGNED_SHORT_4_4_4_4 = t.cast(int, ...)
    UNSIGNED_SHORT_4_4_4_4_REV = t.cast(int, ...)
    UNSIGNED_SHORT_5_5_5_1 = t.cast(int, ...)
    UNSIGNED_SHORT_1_5_5_5_REV = t.cast(int, ...)
    UNSIGNED_INT_8_8_8_8 = t.cast(int, ...)
    UNSIGNED_INT_8_8_8_8_REV = t.cast(int, ...)
    UNSIGNED_INT_10_10_10_2 = t.cast(int, ...)
    UNSIGNED_INT_2_10_10_10_REV = t.cast(int, ...)

class TextureSpec:
    '''Structure used for initial configuration when creating textures.'''

    target: int
    '''Type of the texture.'''

    width: int
    '''Texture width.'''

    height: int
    '''Texture height.'''

    depth: int
    '''Number of layers for array textures.'''

    samples: int
    '''Number of samples for multisampled textures.'''

    mipmaps: int
    '''Number of mipmap levels.'''

    internal_format: int
    '''Texture pixel format.'''

    min_filter: int
    '''Filter used for texture minification.'''

    mag_filter: int
    '''Filter used for texture magnification.'''

    wrap_mode: int
    '''Specifies how the texture should fill bigger regions.'''

    def __init__(self,
                 target: TextureTarget,
                 width: int,
                 height: int,
                 internal_format: InternalFormat | CompressedInternalFormat,
                 depth: int = 1,
                 samples: int = 1,
                 mipmaps: int = 1,
                 min_filter: MinFilter = MinFilter.LINEAR,
                 mag_filter: MagFilter = MagFilter.LINEAR,
                 wrap_mode: WrapMode = WrapMode.CLAMP_TO_EDGE) -> None: ...

    @property
    def size(self) -> tuple[int, int, int]:
        '''Size of the texture (width, height, depth).'''

    @property
    def is_multisampled(self) -> bool:
        '''Indicates if texture uses multisampling.'''

class TextureUploadInfo:
    '''Structure used for pixel data uploads, that tells OpenGL how to interpret provided data.'''

    width: int
    '''Width of the uploaded image.'''

    height: int
    '''Height of the uploaded image.'''

    depth: int
    '''Layer depth of the uploaded image.'''

    x_offset: int
    '''X offset into texture to which data is uploaded.'''

    y_offset: int
    '''Y offset into texture to which data is uploaded.'''

    z_offset: int
    '''Depth offset into texture to which data is uploaded.'''

    level: int
    '''A mipmap level to where data will be uploaded.'''

    format: int
    '''Pixel format.'''

    pixel_type: int
    '''Data type of each pixel component.'''

    data_offset: int
    '''Byte offset into provided data buffer.'''

    image_size: int
    '''Pixel data size. Used for compressed data uploads. Ignored otherwise.'''

    generate_mipmap: bool
    '''Indicates if mipmaps should be generated after uploading data.'''

    def __init__(self,
                 format: PixelFormat | CompressedInternalFormat,
                 width: int,
                 height: int,
                 depth: int = 1,
                 x_offset: int = 0,
                 y_offset: int = 0,
                 z_offset: int = 0,
                 level: int = 0,
                 pixel_type: PixelType = PixelType.UNSIGNED_BYTE,
                 image_size: int = 0,
                 data_offset: int = 0,
                 generate_mipmap: bool = True) -> None: ...

    @property
    def is_compressed(self) -> bool:
        '''Indicates if texture upload uses compressed pixel format.'''

class Texture:
    '''Wrapper for OpenGL texture objects. Supports different types of textures.'''

    def __init__(self, spec: TextureSpec, set_parameters: bool = True) -> None: ...

    def delete(self) -> None:
        '''Deletes the OpenGL texture.'''

    def bind(self) -> None:
        '''
        Binds texture to the correct target.
        The target is defined during texture creation and cannot be changed.
        '''

    def bind_to_unit(self, unit: int) -> None:
        '''
        Binds texture to specified texture unit.

        :param unit: Texture unit index to which the texture will be bound.
        '''

    def set_parameter(self, parameter: TextureParameter, value: int) -> None:
        '''
        Sets specified texture parameter to the given value.

        :param parameter: Texture parameter to be changed.
        :param value: Value to be used for the parameter.

        :raises RuntimeError: If the texture target is GL_TEXTURE_BUFFER.
        '''

    def set_texture_buffer(self, buffer: Buffer) -> None:
        '''
        When texture is created using `TEXTURE_BUFFER` target, data must be uploaded
        using `Buffer` object bound to a texture. This function binds whole buffer
        to the current texture. See https://www.khronos.org/opengl/wiki/Buffer_Texture
        for more info.

        :param buffer: A buffer to be bound as a texture storage.

        :raises RuntimeError: If the texture target is not GL_TEXTURE_BUFFER.
        '''

    def upload(self, upload_info: TextureUploadInfo, data: SupportsBufferProtocol | None) -> None:
        '''
        Uploads pixel data to a texture, using settings specified by provided `upload_info`.
        This function might fail in many ways, depending on provided upload info, the texture config
        and the data provided. Note: if calling this function results in a crash, there might be an issue
        with pixel data alignment. In that case use `set_pixel_unpack_alignment` to set
        correct alignment.
        This function cannot be called on textures created with `TEXTURE_BUFFER` target. Doing so will result
        in OpenGL error being generated. To upload data to such textures use `Buffer.store` methods on
        the buffer bound to the texture.
        For the sake of performance, this function only accepts buffers that are C-contiguous.
        If the `data` argument is `None`, the data is assumed to be already placed into bound pixel unpack buffer.

        :param upload_info: Structure containing info about requested data upload.
        :param data: Object exporting buffer, containing raw pixel data or None.

        :raises RuntimeError: When issuing upload with given parameters would result in access violation.
        :raises RuntimeError: If the texture target is GL_TEXTURE_BUFFER.
        :raises ValueError: If the provided data buffer is not C-contiguous.
        :raises NotImplementedError: If the texture target is GL_TEXTURE_CUBE_MAP_ARRAY.
        '''

    def set_debug_name(self, name: str, /) -> None: ...

    @property
    def id(self) -> int:
        '''OpenGL texture object ID.'''

    @property
    def target(self) -> TextureTarget:
        '''Type of the texture.'''

    @property
    def internal_format(self) -> InternalFormat | CompressedInternalFormat:
        '''Texture pixel format.'''

    @property
    def width(self) -> int:
        '''Texture width.'''

    @property
    def height(self) -> int:
        '''Texture height.'''

    @property
    def depth(self) -> int:
        '''Number of layers for array textures. 0 otherwise.'''

    @property
    def mipmaps(self) -> int:
        '''Number of mipmap levels.'''

    @property
    def is_cubemap(self) -> bool:
        '''Indicates if the texture is a cubemap texture.'''

    @property
    def is_array(self) -> bool:
        '''Indicates if texture is an array texture or has multiple layers.'''

    @property
    def is_1d(self) -> bool:
        '''Indicates if texture is 1-dimensional.'''

    @property
    def is_2d(self) -> bool:
        '''Indicates if texture is 2-dimensional.'''

    @property
    def is_3d(self) -> bool:
        '''Indicates if texture is 3-dimensional.'''

class VertexAttribType(enum.IntEnum):
    '''Used to specify vertex attribute type.'''

    FLOAT = t.cast(int, ...)
    HALF_FLOAT = t.cast(int, ...)
    DOUBLE = t.cast(int, ...)
    BYTE = t.cast(int, ...)
    UNSIGNED_BYTE = t.cast(int, ...)
    SHORT = t.cast(int, ...)
    UNSIGNED_SHORT = t.cast(int, ...)
    INT = t.cast(int, ...)
    UNSIGNED_INT = t.cast(int, ...)

class VertexDescriptor:
    attrib_index: int
    type: int
    count: int
    rows: int = 1
    is_normalized: bool = False

    def __init__(self,
                 attrib_index: int,
                 type: VertexAttribType,
                 count: int,
                 rows: int = 1,
                 is_normalized: bool = False) -> None: ...

class VertexInput:
    buffer_id: int
    stride: int
    descriptors: list[VertexDescriptor]
    offset: int = 0
    divisor: int = 0

    def __init__(self,
                 buffer: Buffer | None,
                 stride: int,
                 descriptors: list[VertexDescriptor],
                 offset: int = 0,
                 divisor: int = 0) -> None: ...

class VertexArray:
    def __init__(self, layout: list[VertexInput], element_buffer: Buffer | None = None) -> None: ...

    def delete(self) -> None: ...
    def bind(self) -> None: ...
    def bind_vertex_buffer(self, buffer: Buffer, index: int, stride: int, offset: int = 0, divisor: int = 0) -> None: ...
    def bind_index_buffer(self, buffer: Buffer) -> None: ...
    def set_debug_name(self, name: str, /) -> None: ...

    @property
    def id(self) -> int: ...

class FramebufferAttachmentFormat(enum.IntEnum):
    RGBA8 = t.cast(int, ...)
    RGB8 = t.cast(int, ...)
    RG8 = t.cast(int, ...)
    R8 = t.cast(int, ...)
    RGBA16 = t.cast(int, ...)
    RGB16 = t.cast(int, ...)
    RG16 = t.cast(int, ...)
    R16 = t.cast(int, ...)
    RGBA16F = t.cast(int, ...)
    RGB16F = t.cast(int, ...)
    RG16F = t.cast(int, ...)
    R16F = t.cast(int, ...)
    RGBA32F = t.cast(int, ...)
    RGB32F = t.cast(int, ...)
    RG32F = t.cast(int, ...)
    R32F = t.cast(int, ...)
    RGBA8I = t.cast(int, ...)
    RGB8I = t.cast(int, ...)
    RG8I = t.cast(int, ...)
    R8I = t.cast(int, ...)
    RGBA16I = t.cast(int, ...)
    RGB16I = t.cast(int, ...)
    RG16I = t.cast(int, ...)
    R16I = t.cast(int, ...)
    RGBA32I = t.cast(int, ...)
    RGB32I = t.cast(int, ...)
    RG32I = t.cast(int, ...)
    R32I = t.cast(int, ...)
    RGBA8UI = t.cast(int, ...)
    RGB8UI = t.cast(int, ...)
    RG8UI = t.cast(int, ...)
    R8UI = t.cast(int, ...)
    RGBA16UI = t.cast(int, ...)
    RGB16UI = t.cast(int, ...)
    RG16UI = t.cast(int, ...)
    R16UI = t.cast(int, ...)
    RGBA32UI = t.cast(int, ...)
    RGB32UI = t.cast(int, ...)
    RG32UI = t.cast(int, ...)
    R32UI = t.cast(int, ...)
    RGBA4 = t.cast(int, ...)
    RGB5_A1 = t.cast(int, ...)
    RGB565 = t.cast(int, ...)
    RGB10_A2 = t.cast(int, ...)
    RGB10_A2UI = t.cast(int, ...)
    R11F_G11F_B10F = t.cast(int, ...)
    SRGB8_ALPHA8 = t.cast(int, ...)
    DEPTH_COMPONENT16 = t.cast(int, ...)
    DEPTH_COMPONENT24 = t.cast(int, ...)
    DEPTH_COMPONENT32F = t.cast(int, ...)
    DEPTH24_STENCIL8 = t.cast(int, ...)
    DEPTH32F_STENCIL8 = t.cast(int, ...)
    STENCIL_INDEX8 = t.cast(int, ...)

class FramebufferAttachmentPoint(enum.IntEnum):
    DEPTH_ATTACHMENT = t.cast(int, ...)
    STENCIL_ATTACHMENT = t.cast(int, ...)
    DEPTH_STENCIL_ATTACHMENT = t.cast(int, ...)

class FramebufferAttachment:
    width: int
    height: int
    format: int
    attachment: int
    samples: int
    min_filter: int
    mag_filter: int
    use_renderbuffer: bool
    is_writable: bool

    def __init__(self,
                 width: int,
                 height: int,
                 format: FramebufferAttachmentFormat,
                 attachment: FramebufferAttachmentPoint | int,
                 samples: int = 1,
                 min_filter: MinFilter = MinFilter.NEAREST,
                 mag_filter: MagFilter = MagFilter.NEAREST,
                 use_renderbuffer: bool = False,
                 is_writable: bool = True) -> None: ...

    @property
    def is_resizable(self) -> bool: ...

    @property
    def is_depth_attachment(self) -> bool: ...

    @property
    def is_color_attachment(self) -> bool: ...

    @property
    def is_multisampled(self) -> bool: ...

    @property
    def size(self) -> tuple[int, int]: ...

    @size.setter
    def size(self, value: tuple[int, int]) -> None: ...

class Framebuffer:
    def __init__(self, attachments: list[FramebufferAttachment], width: int, height: int) -> None: ...
    def delete(self) -> None: ...
    def bind(self) -> None: ...
    def unbind(self) -> None: ...
    def resize(self, width: int, height: int, /) -> None: ...
    def get_attachment(self, attachment_point: FramebufferAttachmentPoint | int, /) -> FramebufferAttachment: ...
    def get_attachment_id(self, attachment_point: FramebufferAttachmentPoint | int, /) -> int: ...
    def clear_color_attachment(self, clear_value: SupportsBufferProtocol, draw_buffer: int, value_type: GLType, /) -> None: ...
    def clear_depth_attachment(self, depth_value: float, /) -> None: ...
    def clear_stencil_attachment(self, stencil_value: int, /) -> None: ...
    def clear_depth_stencil_attachment(self, depth_value: float, stencil_value: int, /) -> None: ...
    def set_debug_name(self, name: str, /) -> None: ...

    @property
    def id(self) -> int: ...

    @property
    def width(self) -> int: ...

    @property
    def height(self) -> int: ...

    @property
    def size(self) -> tuple[int, int]: ...

    @property
    def attachments_count(self) -> int: ...

class Barrier(enum.IntFlag):
    VERTEX_ATTRIB_ARRAY_BARRIER_BIT = t.cast(int, ...)
    ELEMENT_ARRAY_BARRIER_BIT = t.cast(int, ...)
    UNIFORM_BARRIER_BIT = t.cast(int, ...)
    TEXTURE_FETCH_BARRIER_BIT = t.cast(int, ...)
    SHADER_IMAGE_ACCESS_BARRIER_BIT = t.cast(int, ...)
    COMMAND_BARRIER_BIT = t.cast(int, ...)
    PIXEL_BUFFER_BARRIER_BIT = t.cast(int, ...)
    TEXTURE_UPDATE_BARRIER_BIT = t.cast(int, ...)
    BUFFER_UPDATE_BARRIER_BIT = t.cast(int, ...)
    CLIENT_MAPPED_BUFFER_BARRIER_BIT = t.cast(int, ...)
    FRAMEBUFFER_BARRIER_BIT = t.cast(int, ...)
    TRANSFORM_FEEDBACK_BARRIER_BIT = t.cast(int, ...)
    ATOMIC_COUNTER_BARRIER_BIT = t.cast(int, ...)
    SHADER_STORAGE_BARRIER_BIT = t.cast(int, ...)
    QUERY_BUFFER_BARRIER_BIT = t.cast(int, ...)
    ALL_BARRIER_BITS = t.cast(int, ...)

class DrawMode(enum.IntEnum):
    POINTS = t.cast(int, ...)
    LINE_STRIP = t.cast(int, ...)
    LINE_LOOP = t.cast(int, ...)
    LINES = t.cast(int, ...)
    LINE_STRIP_ADJACENCY = t.cast(int, ...)
    LINES_ADJACENCY = t.cast(int, ...)
    TRIANGLE_STRIP = t.cast(int, ...)
    TRIANGLE_FAN = t.cast(int, ...)
    TRIANGLES = t.cast(int, ...)
    TRIANGLE_STRIP_ADJACENCY = t.cast(int, ...)
    TRIANGLES_ADJACENCY = t.cast(int, ...)
    PATCHES = t.cast(int, ...)

class ElementsType(enum.IntEnum):
    UNSIGNED_BYTE = t.cast(int, ...)
    UNSIGNED_SHORT = t.cast(int, ...)
    UNSIGNED_INT = t.cast(int, ...)

class ClearMask(enum.IntFlag):
    COLOR_BUFFER_BIT = t.cast(int, ...)
    DEPTH_BUFFER_BIT = t.cast(int, ...)
    STENCIL_BUFFER_BIT = t.cast(int, ...)

class BlendEquation(enum.IntEnum):
    FUNC_ADD = t.cast(int, ...)
    FUNC_SUBTRACT = t.cast(int, ...)
    FUNC_REVERSE_SUBTRACT = t.cast(int, ...)
    MIN = t.cast(int, ...)
    MAX = t.cast(int, ...)

class BlendFactor(enum.IntEnum):
    ZERO = t.cast(int, ...)
    ONE = t.cast(int, ...)
    SRC_COLOR = t.cast(int, ...)
    ONE_MINUS_SRC_COLOR = t.cast(int, ...)
    DST_COLOR = t.cast(int, ...)
    ONE_MINUS_DST_COLOR = t.cast(int, ...)
    SRC_ALPHA = t.cast(int, ...)
    ONE_MINUS_SRC_ALPHA = t.cast(int, ...)
    DST_ALPHA = t.cast(int, ...)
    ONE_MINUS_DST_ALPHA = t.cast(int, ...)
    CONSTANT_COLOR = t.cast(int, ...)
    ONE_MINUS_CONSTANT_COLOR = t.cast(int, ...)
    CONSTANT_ALPHA = t.cast(int, ...)
    ONE_MINUS_CONSTANT_ALPHA = t.cast(int, ...)

class PolygonMode(enum.IntEnum):
    FILL = t.cast(int, ...)
    POINT = t.cast(int, ...)
    LINE = t.cast(int, ...)

class CullFace(enum.IntEnum):
    FRONT = t.cast(int, ...)
    BACK = t.cast(int, ...)
    FRONT_AND_BACK = t.cast(int, ...)

class DebugType(enum.IntEnum):
    DEPRECATED_BEHAVIOR = t.cast(int, ...)
    ERROR = t.cast(int, ...)
    MARKER = t.cast(int, ...)
    OTHER = t.cast(int, ...)
    PERFORMANCE = t.cast(int, ...)
    POP_GROUP = t.cast(int, ...)
    PORTABILITY = t.cast(int, ...)
    PUSH_GROUP = t.cast(int, ...)
    UNDEFINED_BEHAVIOR = t.cast(int, ...)

class DebugSeverity(enum.IntEnum):
    HIGH = t.cast(int, ...)
    LOW = t.cast(int, ...)
    MEDIUM = t.cast(int, ...)
    NOTIFICATION = t.cast(int, ...)

class DebugSource(enum.IntEnum):
    API = t.cast(int, ...)
    APPLICATION = t.cast(int, ...)
    OTHER = t.cast(int, ...)
    SHADER_COMPILER = t.cast(int, ...)
    THIRD_PARTY = t.cast(int, ...)
    WINDOW_SYSTEM = t.cast(int, ...)

class FrontFace(enum.IntEnum):
    CW = t.cast(int, ...)
    CCW = t.cast(int, ...)

class TextureFormatParameter(enum.IntEnum):
    INTERNALFORMAT_RED_SIZE = t.cast(int, ...)
    INTERNALFORMAT_GREEN_SIZE = t.cast(int, ...)
    INTERNALFORMAT_BLUE_SIZE = t.cast(int, ...)
    INTERNALFORMAT_ALPHA_SIZE = t.cast(int, ...)
    INTERNALFORMAT_DEPTH_SIZE = t.cast(int, ...)
    INTERNALFORMAT_STENCIL_SIZE = t.cast(int, ...)
    INTERNALFORMAT_SHARED_SIZE = t.cast(int, ...)

DebugCallback = t.Callable[[int, int, int, int, str], t.Any]
OpenGLObject = Texture | Buffer | ShaderProgram | VertexArray | Framebuffer | Sync

def draw_arrays(mode: DrawMode, first: int, count: int, /) -> None: ...
def draw_arrays_instanced(mode: DrawMode, first: int, count: int, instance_count: int, /) -> None: ...
def draw_arrays_instanced_base_instance(mode: DrawMode, first: int, count: int, instance_count: int, base_count: int, /) -> None: ...
def draw_arrays_indirect(mode: DrawMode, /) -> None: ...
def multi_draw_arrays_indirect(mode: DrawMode, draw_count: int, stride: int, /) -> None: ...

def draw_elements(mode: DrawMode, count: int, type: ElementsType, offset: int = 0) -> None: ...
def draw_elements_base_vertex(mode: DrawMode, count: int, type: ElementsType, base_vertex: int, offset: int = 0) -> None: ...
def draw_elements_instanced(mode: DrawMode, count: int, type: ElementsType, prim_count: int, /) -> None: ...
def draw_elements_instanced_base_instance(mode: DrawMode, count: int, type: ElementsType, instance_count: int, base_instance: int, /) -> None: ...
def draw_elements_instanced_base_vertex(mode: DrawMode, count: int, type: ElementsType, instance_count: int, base_vertex: int, /) -> None: ...
def draw_elements_instanced_base_vertex_base_instance(mode: DrawMode, count: int, type: ElementsType, instance_count: int, base_vertex: int, base_instance: int, /) -> None: ...
def draw_elements_indirect(mode: DrawMode, type: ElementsType, /) -> None: ...
def multi_draw_elements_indirect(mode: DrawMode, type: ElementsType, draw_count: int, stride: int, /) -> None: ...

def clear(mask: ClearMask, /) -> None:
    '''
    Wrapper for `glClear`.
    See: https://registry.khronos.org/OpenGL-Refpages/gl4/html/glClear.xhtml

    :param mask: Masks that indicate the buffers to be cleared.
    '''

def memory_barrier(barrier: Barrier, /) -> None:
    '''
    Wrapper for `glMemoryBarrier`.
    See: https://registry.khronos.org/OpenGL-Refpages/gl4/html/glMemoryBarrier.xhtml.

    :param barrier: Specifies the barriers to insert.
    '''

def memory_barrier_by_region(barrier: Barrier, /) -> None:
    '''
    Wrapper for `glMemoryBarrierByRegion`.
    See: https://registry.khronos.org/OpenGL-Refpages/gl4/html/glMemoryBarrier.xhtml.

    :param barrier: Specifies the barriers to insert.
    '''

def flush() -> None:
    '''
    Wrapper for `glFlush`.
    See: https://registry.khronos.org/OpenGL-Refpages/gl4/html/glFlush.xhtml.
    '''

def finish() -> None:
    '''
    Wrapper for `glFinish`.
    See: https://registry.khronos.org/OpenGL-Refpages/gl4/html/glFinish.xhtml.
    '''

def enable(enable_cap: EnableCap, /) -> None:
    '''
    Wrapper for `glEnable`.
    See: https://registry.khronos.org/OpenGL-Refpages/gl4/html/glEnable.xhtml.

    :param enable_cap: Specifies a symbolic constant indicating a GL capability.
    '''

def disable(enable_cap: EnableCap, /) -> None:
    '''
    Wrapper for `glDisable`.
    See: https://registry.khronos.org/OpenGL-Refpages/gl4/html/glDisable.xhtml.

    :param enable_cap: Specifies a symbolic constant indicating a GL capability.
    '''

def blend_func(src: BlendFactor, dst: BlendFactor, /) -> None: ...
def blend_func_separate(src_rgb: BlendFactor, dst_rgb: BlendFactor, src_alpha: BlendFactor, dst_alpha: BlendFactor, /) -> None: ...
def blend_equation(equation: BlendEquation, /) -> None: ...

@t.overload
def clear_color(r: float, g: float, b: float, a: float, /) -> None: ...

@t.overload
def clear_color(color: SupportsBufferProtocol, /) -> None: ...

def scissor(x: int, y: int, width: int, height: int, /) -> None: ...
def viewport(x: int, y: int, width: int, height: int, /) -> None: ...
def polygon_mode(face: CullFace, mode: PolygonMode, /) -> None: ...
def debug_message_callback(callback: DebugCallback, /) -> None: ...
def debug_message_insert(source: DebugSource, type: DebugType, severity: DebugSeverity, id: int, message: str, /) -> None: ...
def set_object_name(obj: OpenGLObject, name: str, /) -> None: ...
def depth_mask(value: bool, /) -> None: ...
def cull_face(face: CullFace, /) -> None: ...
def front_face(face: FrontFace, /) -> None: ...
def color_mask(r: bool, g: bool, b: bool, a: bool, /) -> None: ...
def get_internal_format(format: InternalFormat | CompressedInternalFormat, target: TextureTarget, param: TextureFormatParameter, /) -> int: ...

def bind_texture_id(id: int, unit: int, /) -> None: ...

def bind_textures(textures: list[Texture], first: int = 0) -> None:
    '''
    Binds a list of textures to consecutive texture units, starting from `first`.

    :param textures: List of textures to be bound. Must be at most 32.
    :param first: A texture unit number to start at.

    :raises RuntimeError: If amount of specified textures exceeds 32.
    '''

def bind_texture_ids(textures: list[int], first: int = 0) -> None:
    '''
    Same as `bind_textures` but accepts list of texture object IDs instead of
    texture objects.

    :param textures: List of texture object IDs to be bound. Must not exceed 32.
    :param first: A texture unit number to start at.

    :raises RuntimeError: If amount of specified texture IDs exceeds 32.
    '''

def set_pixel_pack_alignment(alignment: t.Literal[1, 2, 4, 8], /) -> None:
    '''
    A wrapper for `glPixelStorei(GL_PACK_ALIGNMENT)`.
    See: https://registry.khronos.org/OpenGL-Refpages/gl4/html/glPixelStore.xhtml.

    :param alignment: Byte alignment of the retrieved data.
    '''

def set_pixel_unpack_alignment(alignment: t.Literal[1, 2, 4, 8], /) -> None:
    '''
    A wrapper for `glPixelStorei(GL_UNPACK_ALIGNMENT)`.
    See: https://registry.khronos.org/OpenGL-Refpages/gl4/html/glPixelStore.xhtml.

    :param alignment: Byte alignment of the stored data.
    '''

def initialize() -> None:
    '''
    **Internal Function**\n
    Loads OpenGL function pointers.

    :raises RuntimeError: If loading OpenGL bindings fails.
    '''

# def shutdown() -> None: ...
# def process_texture_uploads() -> None: ...
# def clear(r: float, g: float, b: float, a: float, clear_depth: bool, /) -> None: ...
# def begin_texture_upload(texture_index: int, data: SupportsBufferProtocol, /) -> int: ...
# def add_texture_upload_info(upload: int,
#                             width: int,
#                             height: int,
#                             depth: int,
#                             compressed_image_size: int,
#                             x_offset: int,
#                             y_offset: int,
#                             z_offset: int,
#                             level: int,
#                             pixel_format: int,
#                             pixel_type: int,
#                             data_offset: int, /) -> int: ...
