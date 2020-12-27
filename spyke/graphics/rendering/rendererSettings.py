from ...utils import Static

class RendererSettings(Static):
    MaxQuadsCount = 300
    """
    Max quads count that can be renderer within one batch.
    This value has to be the same as value in the value that coresponds
    to transformation matrices count declared in the shader.
    """