import dataclasses

from spyke.graphics.textures import TextureSpec, TextureUploadData


@dataclasses.dataclass
class ImageLoadingData:
    specification: TextureSpec
    upload_data: list[TextureUploadData] = dataclasses.field(default_factory=list)
