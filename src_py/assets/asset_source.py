import dataclasses
import enum
import os
import typing as t


class AssetSourceType(enum.IntEnum):
    STANDALONE = enum.auto()
    PACKED = enum.auto()
    INTERNAL = enum.auto()

@dataclasses.dataclass
class AssetSource:
    filepath: str
    type: AssetSourceType = AssetSourceType.STANDALONE

    @classmethod
    def from_filepath(cls, filepath: str) -> t.Self:
        return cls(filepath)

    @classmethod
    def from_data(cls) -> t.Self:
        return cls('', AssetSourceType.INTERNAL)
