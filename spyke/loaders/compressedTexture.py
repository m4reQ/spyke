import ctypes
import numpy

DWORD = ctypes.sizeof(ctypes.c_ulong)
INT = ctypes.sizeof(ctypes.c_int)
UINT = ctypes.sizeof(ctypes.c_uint)

"""
resources used:
https://docs.microsoft.com/pl-pl/windows/win32/direct3ddds/dds-header
https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dx-graphics-dds-pguide

file structure:

DWORD magicNumber (validation key)
DDS_HEADER header (main file header!)
{
    DWORD size (size of structure, not important, always 124)
    DWORD flags (flags that describe the file, idk what exactly)
    DWORD height (height in pixels)
    DWORD width (width in pixels)
    DWORD pitch (pitch or number of bytes per scan line)
    DWORD depth (depth of texture, used if volume texture)
    DWORD mipmaps (mipmaps count)
    DWORD[11] reserved (unused)
    DDS_PIXELFORMAT format (dds pixel format)
    {
        DWORD size (size of structure, always 32 bytes)
        DWORD flags (type of surface data)
        DWORD fourCC (character code, used to describe what type of compression is used)
        DWORD rgbBitCount (number of bits in RGB, can include alpha as well)
        DWORD rBitMask (mask for reading red color data)
        DWORD gBitMask (mask for reading green color data)
        DWORD bBitMask (mask for reading blue color data)
        DWORD aBitMask (mask for reading alpha color data)
    }
    DWORD caps (complexity of texture, always at least 0x1000)
    DWORD caps2 (used if loading volume texture or cubemap)
    DWORD caps3 (unused)
    DWORD caps4 (unused)
    DWORD reserved2 (unused)
}
DDS_HEADER_DXT10 headerDxt10 (additional resource arrays header)
{
    DWORD(enum) dxgiFormat (format of pixel data)
    DWORD(enum) dimension (specifies texture 1D, 2D or 3D)
    UINT miscFlag (tells if file is cubemap)
    UINT arrSize (tells size of array when using cubemap or 3D texture)
    UINT miscFlags (specifies other alpha options, not very important)
}
BYTE[] data (main texture data)
BYTE[] additionalData (additional informations about mipmaps etc.)
"""

class CompressedTexData(object):
    def __init__(self):
        self._data = None
        self.width = 0
        self.height = 0
        self.mipmaps = 0

def __LoadDDS(filepath: str):
    try:
        f = open(filepath, "rb")
    except FileNotFoundError:
        raise RuntimeError(f"Cannot find texture file named '{filepath}'.")

    magicNumber = f.read(DWORD)

    if magicNumber != 0x20534444:
        raise RuntimeError(f"File '{filepath}' is not a valid DDS image.")

    f.read(DWORD) #size

    flags = f.read(DWORD)

    height = int(f.read(DWORD))
    width = int(f.read(DWORD))

    pitch = f.read(DWORD)
    depth = f.read(DWORD)
    mipmaps = f.read(DWORD)

    f.read(DWORD * 11) #reserved

    #pixel format
    characterCode = f.read(DWORD)

    rBitCount = int(f.read(DWORD))
    gBitCount = int(f.read(DWORD))
    bBitCount = int(f.read(DWORD))
    aBitCount = int(f.read(DWORD))

    complexity = f.read(DWORD)
    #handle here loading of volume texture or cubemap (for now raise exception)

    f.read(DWORD * 4) #unused values

    #dxt header (for now skipping)
    f.read(DWORD * 2 + UINT * 3)

    texDataMain = f.read()

    f.close()

def __LoadDDS(filepath: str):
    try:
        f = open(filepath, "rb")
    except FileNotFoundError:
        raise RuntimeError(f"Cannot find texture file named '{filepath}'.")

    magicNumber = f.read(DWORD)

    if magicNumber != 0x20534444:
        raise RuntimeError(f"File '{filepath}' is not a valid DDS image.")

    header = numpy.fromstring(f.read(124), dtype="I1")