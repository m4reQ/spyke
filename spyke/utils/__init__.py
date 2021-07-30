from .functional import *
from .compat import *
from .converters import *
from .time import Delayer

def CreateQuadIndices(quadsCount: int) -> list:
    data = []

    offset = 0
    i = 0
    while i < quadsCount:
        data.extend([
            0 + offset,
            1 + offset,
            2 + offset,
            2 + offset,
            3 + offset,
            0 + offset])
        
        offset += 4
        i += 1
    
    return data