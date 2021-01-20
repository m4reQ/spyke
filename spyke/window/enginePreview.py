from OpenGL import GL
import ctypes
from PIL import Image
import numpy
from pathlib import Path
import os
import gc
from ..loaders import dds_loader

VBO = None
VAO = None
TEXTURE = None
SHADER = None

vertexData = [
    -1.0, -1.0, 0.0, 0.0, 1.0,
    -1.0, 1.0, 0.0,  0.0, 0.0,
    1.0, 1.0, 0.0,   1.0, 0.0,

    1.0, 1.0, 0.0,   1.0, 0.0,
    1.0, -1.0, 0.0,  1.0, 1.0,
    -1.0, -1.0, 0.0, 0.0, 1.0]

_filepath = os.path.join(Path(__file__).parent.parent.parent, "branding/spykeLogoFill.dds")
with open(_filepath, mode = "rb") as f:
    tex = dds_loader.DDSTexture()
    tex.load(_filepath)
    
    print(tex.data)
    texData = numpy.fromstring(f.read(), dtype = numpy.uint8)

vertSource = """
#version 450 core
layout(location = 0) in vec3 aPosition;
layout(location = 1) in vec2 aTexCoord;

out vec2 vTexCoord;

void main() {
    vTexCoord = aTexCoord;
    gl_Position = vec4(aPosition, 1.0f);
}
"""

fragSource = """
#version 450 core
in vec2 vTexCoord;

uniform sampler2D uTexture;

out vec4 Color;

void main() {
    Color = texture(uTexture, vTexCoord);
}
"""

def __SetupShader():
    global SHADER

    SHADER = GL.glCreateProgram()

    vert = GL.glCreateShader(GL.GL_VERTEX_SHADER)
    GL.glShaderSource(vert, vertSource)
    GL.glCompileShader(vert)
    GL.glAttachShader(SHADER, vert)

    frag = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
    GL.glShaderSource(frag, fragSource)
    GL.glCompileShader(frag)
    GL.glAttachShader(SHADER, frag)

    GL.glLinkProgram(SHADER)
    GL.glValidateProgram(SHADER)

    GL.glDetachShader(SHADER, vert)
    GL.glDetachShader(SHADER, frag)

    GL.glDeleteShader(vert)
    GL.glDeleteShader(frag)

def __SetupVbo():
    global VBO

    VBO = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, VBO)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, len(vertexData) * ctypes.sizeof(ctypes.c_float), numpy.asarray(vertexData, dtype = numpy.float32), GL.GL_STATIC_DRAW)

def __SetupVao():
    global VAO

    vertexSize = (3 + 2) * ctypes.sizeof(ctypes.c_float)

    VAO = GL.glGenVertexArrays(1)
    GL.glBindVertexArray(VAO)

    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, VBO)

    GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, vertexSize, ctypes.c_void_p(0))
    GL.glEnableVertexAttribArray(0)

    GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, False, vertexSize, ctypes.c_void_p(3 * ctypes.sizeof(ctypes.c_float)))
    GL.glEnableVertexAttribArray(1)

def __SetupTexture():
    global TEXTURE

    TEXTURE = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, TEXTURE)
    #GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)

    #imageSize = 8 * (1024 / 4) * (1024 / 4)

    GL.glCompressedTexImage2D(GL.GL_TEXTURE_2D, 0, 0x83F3, 1024, 1024, 0, texData)
    GL.glTexParameter(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    GL.glTexParameter(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)

def CleanupPreview():
    global vertexData, texData, vertSource, fragSource

    GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    GL.glDeleteProgram(SHADER)
    GL.glDeleteBuffers(1, [VBO])
    GL.glDeleteVertexArrays(1, [VAO])
    GL.glDeleteTextures(1, [TEXTURE])

    del vertexData
    del texData
    del vertSource
    del fragSource

    gc.collect()

def RenderPreview():
    global VBO, VAO, TEXTURE, SHADER
    
    __SetupShader()
    __SetupVbo()
    __SetupVao()
    __SetupTexture()
    
    GL.glUseProgram(SHADER)
    GL.glBindVertexArray(VAO)
    GL.glBindTexture(GL.GL_TEXTURE_2D, TEXTURE)

    GL.glClear(GL.GL_COLOR_BUFFER_BIT)
    GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)

    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)