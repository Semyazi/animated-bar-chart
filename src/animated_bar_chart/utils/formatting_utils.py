import math


def format_duration(duration, decimal_places=3):
	inp = duration
	if duration == float("inf"):
		return "."

	minutes, seconds = divmod(duration, 60)
	hours, minutes = divmod(minutes, 60)
	seconds, duration = divmod(seconds, 1)

	hours = math.floor(hours)
	minutes = math.floor(minutes)
	seconds = math.floor(seconds)

	if decimal_places == 0:
		decimals = ""

	else:
		decimals = "." + str(math.floor(round(duration, decimal_places)
									* (10 ** decimal_places))).rjust(decimal_places, "0")

	if hours:
		result = f"{hours}:{minutes:02}:{seconds:02}{decimals}"

	elif minutes:
		result = f"{minutes}:{seconds:02}{decimals}"

	elif seconds:
		result = f"{seconds}{decimals}"

	# Truncate leading zeroes.
	return result.lstrip("0")

def format_days(days):
	weeks = days // 7
	days = days % 7
	weeks_text = "weeks" if weeks > 1 else "week"

	if weeks > 0:
		duration = f"{weeks} {weeks_text}, {days}d"

	else:
		duration = f"{days}d"

	return f"{duration}"