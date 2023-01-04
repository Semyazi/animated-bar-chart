import inquirer


class Option:
	__slots__ = ("_idx", "_value")

	def __init__(self, idx, value):
		self._idx = idx
		self._value = value

	def __repr__(self):
		return self._value


def choose_from_list(query, options):
	opts = [Option(i, opt) for i, opt in enumerate(options)]

	q = inquirer.List(None, query, opts)
	return inquirer.prompt((q,))[None]._idx
