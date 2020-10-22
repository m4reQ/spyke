def EnsureString(string):
	if isinstance(string, str):
		return string
	
	return string.decode("ASCII")