import dataclasses
import typing as t

import numpy as np
from pygl.textures import TextureSpec, UploadInfo


@dataclasses.dataclass
class ImageLoadData:
    specification: TextureSpec
    upload_infos: list[UploadInfo]
    upload_data: np.ndarray
    unpack_alignment: t.Literal[1, 2, 4, 8] = 4
