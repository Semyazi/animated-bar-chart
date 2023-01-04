from datetime import datetime, timedelta


class Timer:
	def __init__(self, start_date: datetime, stop_date: datetime, frames_per_day):
		self.start_date = start_date
		self.stop_date = stop_date

		self.frames_per_day = frames_per_day
		self.days_per_frame = 1 / self.frames_per_day

	def get_date(self, frame):
		return self.start_date + timedelta(days=frame * self.days_per_frame)

	def finished(self, frame):
		return self.get_date(frame) >= self.stop_date