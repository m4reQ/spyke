import os
import sys

import setuptools
from setuptools.command.build_ext import build_ext

GLAD_WGL_SOURCE = 'vendor/glad/src/wgl.c'
GLAD_GL_SOURCE = 'vendor/glad/src/gl.c'
GLAD_INCLUDE_DIR = 'vendor/glad/include'

STB_SOURCE = 'vendor/stb/impl.c'
STB_INCLUDE_DIR = 'vendor/stb'

class SpykeBuildExt(build_ext):
    def __init__(self, dist):
        super().__init__(dist)

        self.debug = os.path.splitext(os.path.basename(sys.executable))[0] == 'python_d'

setuptools.setup(
    ext_modules=[
        setuptools.Extension(
            name='spyke.graphics.window',
            sources=[
                'src_c/spyke/window/window.c',
                'src_c/spyke/window/windowSettings.c',
                'src_c/spyke/window/windowEvents.c',
                'src_c/spyke/api.c',
                'src_c/spyke/enum.c',
                GLAD_WGL_SOURCE],
            extra_compile_args=['/std:c17', '/W4', '/permissive-'],
            libraries=['gdi32', 'user32', 'opengl32'],
            include_dirs=[GLAD_INCLUDE_DIR]),
        setuptools.Extension(
            name='spyke.events',
            sources=[
                'src_c/spyke/events/events.c',
                'src_c/spyke/api.c',
                'src_c/spyke/enum.c',
                STB_SOURCE],
            extra_compile_args=['/std:c17', '/W4', '/permissive-'],
            include_dirs=[STB_INCLUDE_DIR])],
    cmdclass={'build_ext': SpykeBuildExt})
