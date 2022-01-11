from spyke.enums import NvidiaIntegerName, StringName, Vendor
from spyke import debug

from typing import List, Tuple
import glfw
from OpenGL import GL


class RendererInfo:
    __slots__ = (
        'window_width',
        'window_height',
        'framebuffer_width',
        'framebuffer_height',
        'window_position_x',
        'window_position_y',
        'glfw_version',
        'refresh_rate',
        'vsync',
        'renderer',
        'version',
        'glsl_version',
        'vendor',
        'video_memory_available',
        'extensions'
    )

    def __init__(self):
        self.window_width: int = 0
        self.window_height: int = 0
        self.framebuffer_width: int = 0
        self.framebuffer_height: int = 0
        self.window_position_x: int = 0
        self.window_position_y: int = 0
        self.glfw_version: str = ''
        self.refresh_rate: float = 0.0
        self.vsync: bool = False
        self.renderer: str = ''
        self.version: str = ''
        self.glsl_version: str = ''
        self.vendor: Vendor = Vendor.Unknown
        # TODO: `video_memory_available` shouldn't be accessible if vendor
        # doesn't support querying this information
        self.video_memory_available: int = -1
        self.extensions: List[str] = []

    def _get(self, handle) -> None:
        self.glfw_version = '.'.join(str(x) for x in glfw.get_version())
        self.window_position_x, self.window_position_y = glfw.get_window_pos(
            handle)
        self.window_width, self.window_height = glfw.get_framebuffer_size(
            handle)

        vidmode = glfw.get_video_mode(glfw.get_primary_monitor())
        self.refresh_rate = vidmode.refresh_rate

        self.renderer = self._get_string(StringName.Renderer)
        self.version = self._get_string(StringName.Version)
        self.glsl_version = self._get_string(StringName.ShadingLanguageVersion)

        vendor = self._get_string(StringName.Vendor).lower()
        if 'nvidia' in vendor:
            self.vendor = Vendor.Nvidia
        elif 'intel' in vendor:
            self.vendor = Vendor.Intel
        elif 'ati' in vendor:
            self.vendor = Vendor.Amd
        elif 'microsoft' in vendor:
            self.vendor = Vendor.WindowsSoftware

        if self.vendor == Vendor.Nvidia:
            self.video_memory_available = GL.glGetIntegerv(
                NvidiaIntegerName.GpuMemInfoTotalAvailable)

        extCount = GL.glGetInteger(GL.GL_NUM_EXTENSIONS)
        for i in range(extCount):
            ext_name = GL.glGetStringi(
                GL.GL_EXTENSIONS, i).decode('ascii').lower()
            self.extensions.append(ext_name)

        debug.log_info('Renderer informations retrieved.')

    def _get_string(self, name: StringName) -> str:
        return GL.glGetString(name).decode('ascii')

    @property
    def window_size(self) -> Tuple[int, int]:
        return (self.window_width, self.window_height)

    @property
    def framebuffer_size(self) -> Tuple[int, int]:
        return (self.framebuffer_width, self.framebuffer_height)

    @property
    def window_position(self) -> Tuple[int, int]:
        return (self.window_position_x, self.window_position_y)

    def extension_present(self, ext_name: str) -> bool:
        return ext_name.lower() in self.extensions
