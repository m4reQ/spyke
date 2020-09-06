import openal

FORMAT_MAP = {
	(1, 8): openal.AL_FORMAT_MONO8,
	(2, 8): openal.AL_FORMAT_STEREO8,
	(1, 16): openal.AL_FORMAT_MONO16,
	(2, 16): openal.AL_FORMAT_STEREO16}