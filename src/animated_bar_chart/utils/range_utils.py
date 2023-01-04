from decimal import Decimal


# Note, this range function includes stop.
def drange(start, stop, step):
	start = Decimal(start)
	step_decimal = Decimal(step)

	while start <= stop:
		yield float(start)
		start += step_decimal