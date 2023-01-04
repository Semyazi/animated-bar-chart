from animated_bar_chart.utils.interpolation_utils import (CosineInterpolation,
                                                          optimize_data)


class Tickmark:
	__slots__ = ("_visibility_history", "_interp")
	date_key = lambda datum: datum["date"]
	visibility_key = lambda datum: datum["visibility"]

	def __init__(self, window_radius, default_value):
		self._visibility_history = []
		self._interp = CosineInterpolation(window_radius, Tickmark.date_key, Tickmark.visibility_key, default_value)

	def add_visibility(self, date, visibility):
		self._visibility_history.append({"date": date, "visibility": visibility})

	def get_visibility(self, date):
		return self._interp.interpolate(date, self._visibility_history)

	def optimize_data(self):
		self._visibility_history = optimize_data(self._visibility_history, Tickmark.visibility_key)