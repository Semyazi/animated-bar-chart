import math
from bisect import bisect_left, bisect_right


# Antiderivative of the function f(x) = 1 - cos(2pix)
# NOTE: This function was designed such that its integral from 0 -> 1 is 1.
def cos_antiderivative(x):
	return x - (math.sin(math.tau * x) / math.tau)

# Brings x within the range of [minimum, maximum]
def clamp(x, minimum, maximum):
	return max(min(x, maximum), minimum)

# This class interpolates between values by assigning each of them a portion of a rescaled cosine graph between 0 -> 1, and using the integral of that portion as a weight.
class CosineInterpolation:
	__slots__ = ("_window_radius", "_get_time", "_get_value", "_default_value")

	def __init__(self, window_radius, get_time, get_value, default_value=None):
		self._window_radius = window_radius

		self._get_time = get_time
		self._get_value = get_value

		self._default_value = default_value

	def _interpolate_time(self, time, start_time, stop_time):
		# Interpolate time from between start_time - stop_time to between 0 - 1.
		return (time - start_time) / (stop_time - start_time)

	def _get_first_datum_index(self, time, data):
		# Find the first datum index before or equal to the time.
		return bisect_right(data, time, key=self._get_time) - 1
	
	def _get_last_datum_index(self, time, data):
		# Find the index of the greatest time less than time.
		return bisect_left(data, time, key=self._get_time) - 1

	def _get_default_value(self, data):
		return self._get_value(data[0]) if self._default_value == None else self._default_value

	def interpolate(self, time, data):
		total_value = 0

		# Find the data points that matter.
		start_time = time - self._window_radius
		stop_time = time + self._window_radius

		# Find the range of data that is within our window.
		first_datum_idx = self._get_first_datum_index(start_time, data)
		last_datum_idx = self._get_last_datum_index(stop_time, data)

		# Loop over data within range.
		prior_antiderivative = 0

		for i in range(first_datum_idx, last_datum_idx + 1):
			datum = data[i]

			t_next = 1
			if i < last_datum_idx:
				t_next = self._interpolate_time(self._get_time(data[i + 1]), start_time, stop_time)

			# Get value
			if i == -1:
				datum_value = self._get_default_value(data)
			else:
				datum_value = self._get_value(datum)

			antiderivative = cos_antiderivative(t_next)

			# Apply the fundamental theorem of calculus.
			weight = antiderivative - prior_antiderivative
			total_value += datum_value * weight

			prior_antiderivative = antiderivative

		# Since the integral from 0 -> 1 is 1, we do not need to modify the output.
		return total_value

class PreloadedCosineInterpolation(CosineInterpolation):
	__slots__ = ("_window_radius", "_get_time", "_get_value", "_default_value", "_data")

	def __init__(self, data, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._data = data

	def interpolate(self, time):
		return super().interpolate(time, self._data)

# Linearly interpolate from a to b, using c.
def lerp(a, b, c):
	return a + (c * (b-a))

# This function optimizes a list of data for faster interpolation.
def optimize_data(data: list, get_value):
	new_data = []
	prev_value = None

	for datum in data:
		value = get_value(datum)

		if value != prev_value:
			new_data.append(datum)
			prev_value = value

	return new_data
