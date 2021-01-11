SPACE_SUBSTITUTE = "%32"

def SecureSpaces(string: str):
	return string.replace(" ", SPACE_SUBSTITUTE)

def RestoreSpaces(string: str):
	return string.replace(SPACE_SUBSTITUTE, " ")

def EnsureString(string):
	if isinstance(string, str):
		return string
	
	return string.decode("ASCII")