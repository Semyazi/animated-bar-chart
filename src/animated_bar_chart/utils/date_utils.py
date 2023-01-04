from datetime import date, datetime, timezone


def date_utcfromtimestamp(timestamp):
	dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)

	return datetime_to_date(dt)

def date_to_datetime(date_obj: date):
	return datetime(date_obj.year, date_obj.month, date_obj.day)

def datetime_utcfromtimestamp(timestamp):
	return date_to_datetime(date_utcfromtimestamp(timestamp))

def datetime_to_date(dt):
	return date(dt.year, dt.month, dt.day)