import enum

class CameraType(enum.Enum):
    Orthographic = enum.auto()
    Perspective = enum.auto()


class Vendor(enum.Enum):
    Nvidia = enum.auto()
    Intel = enum.auto()
    Amd = enum.auto()
    WindowsSoftware = enum.auto()
    Unknown = enum.auto()