def multiply_dict(dictionary, multiplier):
	return {k: multiplier*v for k, v in dictionary.items()}

def subdict(dictionary, key_whitelist):
	return {k: v for k, v in dictionary.items() if k in key_whitelist}

def multiply_subdict(dictionary, key_whitelist, multiplier):
	return multiply_dict(subdict(dictionary, key_whitelist), multiplier)