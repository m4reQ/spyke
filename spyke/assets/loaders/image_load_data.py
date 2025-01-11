import dataclasses

import numpy as np

from pygl.textures import TextureSpec, UploadInfo


@dataclasses.dataclass
class ImageLoadData:
    specification: TextureSpec
    upload_infos: list[UploadInfo]
    upload_data: np.ndarray
