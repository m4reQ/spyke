import os

os.add_dll_directory(os.path.dirname(os.path.abspath(__file__)))

from spyke import debug

debug.initialize()
