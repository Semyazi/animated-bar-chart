from animated_bar_chart.graphics.AnimatedBarChart import AnimatedBarChart
from animated_bar_chart.graphics.BaseRenderer import BaseRenderer
from animated_bar_chart.graphics.DateDisplay import DateDisplay
from animated_bar_chart.graphics.Timer import Timer
from animated_bar_chart.models import Leaderboard
from animated_bar_chart.utils.font_utils import create_relative_font
from animated_bar_chart.utils.interpolation_utils import lerp


class Renderer(BaseRenderer):
	def __init__(self, renderer_config, timer: Timer, leaderboard: Leaderboard, interp_windows, cols, bar_config, tickmark_config, font_config, date_config):
		super().__init__(**renderer_config)
		self.size = renderer_config["size"]

		self.date_config = date_config

		self.timer = timer
		self.cols = cols
		self.animated_bar_chart = AnimatedBarChart(self.size, leaderboard, interp_windows, bar_config, tickmark_config, font_config, self.cols)

		date_font = create_relative_font(font_config["date"], self.size[0]) # Proportional to the width
		self.date_display = DateDisplay(date_font, self.cols)

	def render_frame(self, frame):
		if self.timer.finished(frame):
			return False
		
		date = self.timer.get_date(frame)

		self.animated_bar_chart.render(date)

		self._screen.fill(self.cols["bg"])
		self._screen.blit(self.animated_bar_chart.image, (0, 0))

		date_surf = self.date_display.render(date)
		date_rect = date_surf.get_rect()

		date_rect.right = lerp(date_rect.width, self.size[0], self.date_config["x"])
		date_rect.bottom = lerp(date_rect.height, self.size[1], self.date_config["y"])

		self._screen.blit(date_surf, date_rect)

		return True