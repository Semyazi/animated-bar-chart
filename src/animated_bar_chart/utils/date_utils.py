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

def str_to_date(s, delimiter="/"):
	y, m, d = (int(x) for x in s.split(delimiter))
	return date(y, m, d)

def date_to_timestamp(date):
	return datetime.timestamp(date_to_datetime(date))

def str_to_timestamp(s, delimiter="/"):
	return date_to_timestamp(str_to_date(s, delimiter))