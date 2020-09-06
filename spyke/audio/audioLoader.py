from .soundData import SoundData
from .audioUtils import FORMAT_MAP
from ..debug import Log, LogLevel

import wave
import time

def LoadSound(filepath: str):
	start = time.perf_counter()

	wavObj = wave.open(filepath, "rb")

	data = SoundData()
	data.ChannelsCount = wavObj.getnchannels()
	data.BitRate = wavObj.getsampwidth() * 8
	data.SampleRate = wavObj.getframerate()
	data.Format = FORMAT_MAP[(data.ChannelsCount, data.BitRate)]

	data.Data = wavObj.readframes(wavObj.getnframes())
	data.Length = len(data.Data)
	data.LengthSeconds = wavObj.getnframes() / data.SampleRate

	wavObj.close()

	Log(f"Sound file '{filepath}' loaded in {time.perf_counter() - start} seconds.", LogLevel.Info)

	return data