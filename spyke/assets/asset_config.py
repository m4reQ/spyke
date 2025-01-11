import dataclasses
import typing as t


@dataclasses.dataclass
class AssetConfig:
    @classmethod
    def default(cls) -> t.Self:
        return cls()
