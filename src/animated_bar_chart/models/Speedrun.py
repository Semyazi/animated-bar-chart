class Speedrun:
	__slots__ = ("duration", "comment", "timestamp")

	def __init__(self, duration, comment, timestamp):
		self.duration = duration
		self.comment = comment
		self.timestamp = timestamp

	def to_object(self):
		return {k: self.__getattribute__(k) for k in self.__slots__}