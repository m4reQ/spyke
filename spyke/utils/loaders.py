from PIL import Image
import numpy as np
from spyke.exceptions import GraphicsException


def get_image_data(img: Image.Image) -> np.ndarray:
    img.load()

    encoder = Image._getencoder(img.mode, 'raw', img.mode)
    encoder.setimage(img.im)

    shape, typestr = Image._conv_type_shape(img)
    data = np.empty(shape, dtype=np.dtype(typestr))
    mem = data.data.cast('B', (data.data.nbytes,))

    bufsize, s, offset = 65536, 0, 0
    while not s:
        _, s, d = encoder.encode(bufsize)
        mem[offset:offset + len(d)] = d
        offset += len(d)
    if s < 0:
        raise GraphicsException(f'Encoder error: {s}')

    return data
