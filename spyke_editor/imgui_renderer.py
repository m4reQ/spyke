import imgui

from pygl import (buffers, commands, context, math, rendering, shaders,
                  textures, vertex_array)
from spyke import debug

_VERTEX_BUFFER_SIZE = imgui.VERTEX_SIZE * 64 * 1024
_INDEX_BUFFER_SIZE = imgui.INDEX_SIZE * 64 * 1024
_DRAW_ELEMENT_TYPE = rendering.ElementsType.UNSIGNED_SHORT if imgui.INDEX_SIZE == 2 else rendering.ElementsType.UNSIGNED_INT
_VERTEX_SHADER_SRC = '''
#version 450 core

layout(location = 0) in vec2 Position;
layout(location = 1) in vec2 UV;
layout(location = 2) in vec4 Color;

out vec2 Frag_UV;
out vec4 Frag_Color;

uniform mat4 uProjMtx;

void main() {
    Frag_UV = UV;
    Frag_Color = Color;

    gl_Position = uProjMtx * vec4(Position, 0, 1);
}
'''
_FRAGMENT_SHADER_SRC = '''
#version 450 core

in vec2 Frag_UV;
in vec4 Frag_Color;

layout(location = 0) out vec4 Out_Color;

layout(binding = 0) uniform sampler2D uTexture;

void main() {
    Out_Color = Frag_Color * texture(uTexture, Frag_UV.st);
}
'''

@debug.profiled('editor', 'imgui')
def initialize() -> None:
    _create_shader()
    _create_buffers()
    _create_vertex_array()
    _create_font_texture()

@debug.profiled('editor', 'imgui')
def shutdown() -> None:
    _shader.delete()
    _vertex_array.delete()
    _vertex_buffer.delete()
    _index_buffer.delete()
    _font_texture.delete()

@debug.profiled('editor', 'imgui')
def render(draw_data) -> None:
    io = imgui.get_io()
    fb_width = int(io.display_size[0] * io.display_fb_scale[0])
    fb_height = int(io.display_size[1] * io.display_fb_scale[1])

    draw_data.scale_clip_rects(*io.display_fb_scale)

    _setup_gl_state(fb_width, fb_height)
    _shader.set_uniform_mat4('uProjMtx', _calculate_gui_projection(draw_data.display_pos, draw_data.display_size))
    _shader.use()
    _vertex_array.bind()

    clip_off = draw_data.display_pos
    clip_scale = draw_data.frame_buffer_scale

    command_list_offsets = list[tuple[int, int]]()
    current_vertex_offset = 0
    current_index_offset = 0

    # with debug.profiled_scope('map_buffers'):
    #     _vertex_buffer.map()
    #     _index_buffer.map()

    with debug.profiled_scope('prepare_command_lists'):
        for commands_list in draw_data.commands_lists:
            _vertex_buffer.store_address(commands_list.vtx_buffer_data, commands_list.vtx_buffer_size * imgui.VERTEX_SIZE)
            _index_buffer.store_address(commands_list.idx_buffer_data, commands_list.idx_buffer_size * imgui.INDEX_SIZE)

            command_list_offsets.append((current_vertex_offset, current_index_offset))

            current_vertex_offset += commands_list.vtx_buffer_size
            current_index_offset += commands_list.idx_buffer_size

    with debug.profiled_scope('transfer_render_data'):
        _vertex_buffer.transfer()
        _index_buffer.transfer()

    for (vtx_offset, idx_offset), commands_list in zip(command_list_offsets, draw_data.commands_lists):
        list_idx_offset = 0

        for cmd in commands_list.commands:
            with debug.profiled_scope('render_command'):
                clip_min_x = int((cmd.clip_rect.x - clip_off.x) * clip_scale.x)
                clip_min_y = int((cmd.clip_rect.y - clip_off.y) * clip_scale.y)
                clip_max_x = int((cmd.clip_rect.z - clip_off.x) * clip_scale.x)
                clip_max_y = int((cmd.clip_rect.w - clip_off.y) * clip_scale.y)

                if clip_max_x <= clip_min_x or clip_max_y <= clip_min_y:
                    continue

                commands.scissor(
                    clip_min_x,
                    fb_height - clip_max_y,
                    clip_max_x - clip_min_x,
                    clip_max_y - clip_min_y)
                textures.bind_texture_ids([cmd.texture_id])
                rendering.draw_elements_base_vertex(
                    rendering.DrawMode.TRIANGLES,
                    cmd.elem_count,
                    _DRAW_ELEMENT_TYPE,
                    vtx_offset,
                    list_idx_offset + idx_offset * imgui.INDEX_SIZE)

                list_idx_offset += cmd.elem_count * imgui.INDEX_SIZE

@debug.profiled('editor', 'imgui')
def _setup_gl_state(width: int, height: int) -> None:
    commands.enable(commands.EnableCap.BLEND)
    commands.enable(commands.EnableCap.SCISSOR_TEST)
    commands.disable(commands.EnableCap.CULL_FACE)
    commands.disable(commands.EnableCap.DEPTH_TEST)
    commands.disable(commands.EnableCap.STENCIL_TEST)
    commands.disable(commands.EnableCap.PRIMITIVE_RESTART)
    commands.blend_equation(commands.BlendEquation.FUNC_ADD)
    commands.blend_func_separate(
        commands.BlendFactor.SRC_ALPHA,
        commands.BlendFactor.ONE_MINUS_SRC_ALPHA,
        commands.BlendFactor.ONE,
        commands.BlendFactor.ONE_MINUS_SRC_ALPHA)
    commands.polygon_mode(commands.CullFace.FRONT_AND_BACK, commands.PolygonMode.FILL)

    commands.viewport(0, 0, width, height)

@debug.profiled('editor', 'imgui')
def _calculate_gui_projection(display_pos: tuple[int, int], display_size: tuple[int, int]) -> math.Matrix4:
    return math.Matrix4.ortho(
        display_pos[0],
        display_pos[0] + display_size[0],
        display_pos[1] + display_size[1],
        display_pos[1])

@debug.profiled('editor', 'imgui')
def _create_shader() -> None:
    global _shader

    _shader = shaders.Shader([
        shaders.ShaderStage(shaders.ShaderType.VERTEX_SHADER, _VERTEX_SHADER_SRC, True),
        shaders.ShaderStage(shaders.ShaderType.FRAGMENT_SHADER, _FRAGMENT_SHADER_SRC, True)])

@debug.profiled('editor', 'imgui')
def _create_buffers() -> None:
    global _vertex_buffer, _index_buffer

    _vertex_buffer = buffers.Buffer(_VERTEX_BUFFER_SIZE, buffers.BufferFlags.DYNAMIC_STORAGE_BIT)
    _index_buffer = buffers.Buffer(_INDEX_BUFFER_SIZE, buffers.BufferFlags.DYNAMIC_STORAGE_BIT)

@debug.profiled('editor', 'imgui')
def _create_vertex_array() -> None:
    global _vertex_array

    _vertex_array = vertex_array.VertexArray([
        vertex_array.VertexInput(
            buffer=_vertex_buffer,
            stride=imgui.VERTEX_SIZE,
            descriptors=[
                vertex_array.VertexDescriptor(_shader.resources['Position'], vertex_array.AttribType.FLOAT, 2),
                vertex_array.VertexDescriptor(_shader.resources['UV'], vertex_array.AttribType.FLOAT, 2),
                vertex_array.VertexDescriptor(_shader.resources['Color'], vertex_array.AttribType.UNSIGNED_BYTE, 4, is_normalized=True)])],
        _index_buffer)

@debug.profiled('editor', 'imgui')
def _create_font_texture() -> None:
    global _font_texture

    io = imgui.get_io()
    width, height, pixels = io.fonts.get_tex_data_as_rgba32()

    _font_texture = textures.Texture(
        textures.TextureSpec(
            textures.TextureTarget.TEXTURE_2D,
            width,
            height,
            textures.InternalFormat.RGBA8))
    _font_texture.upload(
        textures.UploadInfo(textures.PixelFormat.RGBA, width, height, generate_mipmap=False),
        pixels)

    io.fonts.texture_id = _font_texture.id

_shader: shaders.Shader
_vertex_array: vertex_array.VertexArray
_vertex_buffer: buffers.Buffer
_index_buffer: buffers.Buffer
_font_texture: textures.Texture
