from datetime import date

from animated_bar_chart.utils.date_utils import datetime_to_date


class DateDisplay:
	def __init__(self, date_font, cols):
		self.date_font = date_font
		self.cols = cols

	def render(self, datetime):
		date_obj = min(datetime_to_date(datetime), date.today())
		text = date_obj.strftime("%Y, %b %d")

		surf = self.date_font.render(text, True, self.cols["text"])

		return surf