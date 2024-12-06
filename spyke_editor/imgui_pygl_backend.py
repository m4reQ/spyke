import glm
import imgui
from imgui.integrations.base import BaseOpenGLRenderer

from pygl import buffers, commands, rendering, shaders, textures, vertex_array
from spyke import debug

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

class PYGLBackend(BaseOpenGLRenderer):
    def __init__(self) -> None:
        super().__init__()

        self._shader: shaders.Shader
        self._vertex_array: vertex_array.VertexArray
        self._vertex_buffer: buffers.Buffer
        self._index_buffer: buffers.Buffer
        self._font_texture_obj: textures.Texture

    @debug.profiled('editor', 'imgui')
    def render(self, draw_data):
        fb_width = int(self.io.display_size[0] * self.io.display_fb_scale[0])
        fb_height = int(self.io.display_size[1] * self.io.display_fb_scale[1])

        if fb_width <= 0 or fb_height <= 0:
            return

        draw_data.scale_clip_rects(*self.io.display_fb_scale)

        # TODO Properly restore those settings later
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

        commands.viewport(0, 0, fb_width, fb_height)
        l = draw_data.display_pos[0]
        r = draw_data.display_pos[0] + draw_data.display_size[0]
        t = draw_data.display_pos[1]
        b = draw_data.display_pos[1] + draw_data.display_size[1]

        projection = glm.mat4(
            2.0 / (r - l), 0.0, 0.0, 0.0,
            0.0, 2.0 / (t - b), 0.0, 0.0,
            0.0, 0.0, -1.0, 0.0,
            (r + l) / (l - r), (t + b) / (b - t), 0.0, 1.0)
        self._shader.set_uniform_mat4('uProjMtx', projection)

        self._shader.use()
        self._vertex_array.bind()

        clip_off = draw_data.display_pos
        clip_scale = draw_data.frame_buffer_scale

        for draw_commands in draw_data.commands_lists:
            idx_buffer_offset = 0

            self._vertex_buffer.store_address(draw_commands.vtx_buffer_data, draw_commands.vtx_buffer_size * imgui.VERTEX_SIZE)
            self._vertex_buffer.transfer()

            self._index_buffer.store_address(draw_commands.idx_buffer_data, draw_commands.idx_buffer_size * imgui.INDEX_SIZE)
            self._index_buffer.transfer()

            for cmd in draw_commands.commands:
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

                element_type = rendering.ElementsType.UNSIGNED_SHORT if imgui.INDEX_SIZE == 2 else rendering.ElementsType.UNSIGNED_INT
                rendering.draw_elements(
                    rendering.DrawMode.TRIANGLES,
                    cmd.elem_count,
                    element_type)

                idx_buffer_offset += cmd.elem_count * imgui.INDEX_SIZE

    @debug.profiled('editor', 'imgui')
    def refresh_font_texture(self):
        width, height, pixels = self.io.fonts.get_tex_data_as_rgba32()

        if self._font_texture is not None:
            self._font_texture_obj.delete()

        self._font_texture_obj = textures.Texture(
            textures.TextureSpec(
                textures.TextureTarget.TEXTURE_2D,
                width,
                height,
                textures.InternalFormat.RGBA8))
        self._font_texture_obj.upload(
            textures.UploadInfo(textures.PixelFormat.RGBA, width, height),
            pixels)

        self._font_texture = self._font_texture_obj.id
        self.io.fonts.texture_id = self._font_texture
        self.io.fonts.clear_tex_data()

    @debug.profiled('editor', 'imgui')
    def _create_device_objects(self):
        stages = [
            shaders.ShaderStage(shaders.ShaderType.VERTEX_SHADER, _VERTEX_SHADER_SRC, True),
            shaders.ShaderStage(shaders.ShaderType.FRAGMENT_SHADER, _FRAGMENT_SHADER_SRC, True)]
        self._shader = shaders.Shader(stages)

        # TODO Size
        self._vertex_buffer = buffers.Buffer(256 * 1024, buffers.BufferFlags.DYNAMIC_STORAGE_BIT)
        self._index_buffer = buffers.Buffer(256 * 1024, buffers.BufferFlags.DYNAMIC_STORAGE_BIT)

        layout = [
            vertex_array.VertexInput(
                buffer=self._vertex_buffer,
                stride=imgui.VERTEX_SIZE,
                descriptors=[
                    vertex_array.VertexDescriptor(self._shader.resources['Position'], vertex_array.AttribType.FLOAT, 2),
                    vertex_array.VertexDescriptor(self._shader.resources['UV'], vertex_array.AttribType.FLOAT, 2),
                    vertex_array.VertexDescriptor(self._shader.resources['Color'], vertex_array.AttribType.UNSIGNED_BYTE, 4, is_normalized=True)])]
        self._vertex_array = vertex_array.VertexArray(layout, self._index_buffer)

    def _invalidate_device_objects(self):
        self._shader.delete()
        self._vertex_array.delete()
        self._vertex_buffer.delete()
        self._index_buffer.delete()

        self.io.fonts.texture_id = 0
        self._font_texture = 0
