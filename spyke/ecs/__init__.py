from .esper import Processor
from .esper import World as Scene

class Entity(object):
    def __init__(self):
        raise NotImplementedError("Cannot instantiate abstract class.")