import math

from animated_bar_chart.utils.range_utils import drange


# Start is the smallest duration that is still visible and stop is the largest duration that is still visible.
def calculate_tickmarks(start, stop, tickmark_increment):
    return math.floor(stop / tickmark_increment) - math.ceil(start / tickmark_increment) + 1

def calculate_first_tickmark(start, tickmark_increment):
	return math.ceil(start / tickmark_increment) * tickmark_increment

def calculate_last_tickmark(stop, tickmark_increment):
	return math.floor(stop / tickmark_increment) * tickmark_increment

def calculate_ideal_tickmark_increment(start, stop, tickmark_increments, min_tickmarks):
	for tickmark_increment in reversed(tickmark_increments):
		if calculate_tickmarks(start, stop, tickmark_increment) >= min_tickmarks:
			return tickmark_increment

	# If no tickmarks fit, just return the smallest one.
	return tickmark_increments[0]

def compute_tickmark_range(start, stop, tickmark_increments, min_tickmarks):
	ideal_tickmark_increment = calculate_ideal_tickmark_increment(start, stop, tickmark_increments, min_tickmarks)
	first_tickmark = calculate_first_tickmark(start, ideal_tickmark_increment)
	last_tickmark = calculate_last_tickmark(stop, ideal_tickmark_increment)

	return drange(first_tickmark, last_tickmark, ideal_tickmark_increment)