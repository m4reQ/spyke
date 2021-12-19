from .gl import GLObject

from OpenGL import GL

_WAIT_TIMEOUT_NS = 1000

class Sync(GLObject):
    def __init__(self):
        super().__init__()
        self._id = GL.GLint(0)
    
    def LockBuffer(self):
        if self._id:
            self.delete()
        
        self._id = GL.glFenceSync(GL.GL_SYNC_GPU_COMMANDS_COMPLETE, 0)
    
    def WaitBuffer(self):
        if self._id:
            while True:
                waitRet = GL.glClientWaitSync(self._id, GL.GL_SYNC_FLUSH_COMMANDS_BIT, _WAIT_TIMEOUT_NS)
                if waitRet == GL.GL_ALREADY_SIGNALED or waitRet == GL.GL_CONDITION_SATISFIED:
                    return
    
    def delete(self) -> None:
        GL.glDeleteSync(self._id)
        self._id = GL.GLint(0)