import math
from datetime import date, timedelta
from operator import itemgetter

import pygame
import pygame.gfxdraw

from animated_bar_chart.graphics.Bar import Bar
from animated_bar_chart.graphics.Tickmark import Tickmark
from animated_bar_chart.models import Leaderboard, Runner
from animated_bar_chart.utils.date_utils import (date_to_datetime,
                                                 date_utcfromtimestamp)
from animated_bar_chart.utils.font_utils import create_relative_fonts
from animated_bar_chart.utils.formatting_utils import format_duration
from animated_bar_chart.utils.interpolation_utils import (CosineInterpolation,
                                                          lerp)
from animated_bar_chart.utils.tickmark_utils import compute_tickmark_range


class AnimatedBarChart:
	def __init__(self, size, leaderboard: Leaderboard, interp_windows, bar_config, tickmark_config, font_config, cols):
		self.width, self.height = size
		self.cols = cols

		self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
		self.image = self.image.convert_alpha()
		
		self.leaderboard = leaderboard
		self.top_ranks = self.leaderboard.top_ranks

		self.bar_config = bar_config
		self.tickmark_config = tickmark_config

		bar_fill, max_pfp_size, top_padding = itemgetter("bar_fill", "max_pfp_size", "top_padding")(self.bar_config)

		self.bar_height = self.height / (self.top_ranks + bar_fill * (max_pfp_size + top_padding - 1))
		self.bar_filled_height = self.bar_height * self.bar_config["bar_fill"]
		

		""" ^ derivation
		h = total height available
		r = top ranks
		m = wr pfp multiplier
		p = bar fill proportion
		t = top padding multiplier for the WR for however many weeks or days text

		h1 = height per standard bar
		h2 = height per top bar

		(r-1)(h1) + h2 = h

		h2 = h1*p*m + h1*p*t + h1(1-p)

		(r-1)(h1) + h2 = h
		(r-1)(h1) + h1*p*m + h1*p*t + h1(1-p) = h
		[h1][(r-1) + p*m + p*t + (1-p)] = h
		[h1][r-1 + p*m + p*t + 1-p] = h
		[h1][r + p*m + p*t - p] = h
		h1 = h / (r + p*m + p*t - p)
		h1 = h / (r + p(m+t-1))
		"""

		# Create fonts
		self.fonts = create_relative_fonts(font_config, self.bar_filled_height)

		# Create interpolation
		rank_time = lambda rank: rank["date"]
		rank_value = lambda rank: rank["rank"]
		self.rank_interpolation = CosineInterpolation(interp_windows["rank"], rank_time, rank_value, self.top_ranks)

		# Create a bar for every runner
		self.bars = []
		duration_interp = CosineInterpolation(interp_windows["duration"], Runner.speedrun_timestamp_key, Runner.speedrun_duration_key)
		pb_interp = CosineInterpolation(interp_windows["pb"], Runner.speedrun_timestamp_key_dict, Runner.speedrun_index_key_dict, 0)

		for runner in self.leaderboard.runners.values():
			#runner: Runner, width, height, fonts, cols, duration_interp: CosineInterpolation, pb_interp: CosineInterpolation, bar_config
			bar = Bar(runner, self.width, self.bar_height, self.fonts, self.cols, duration_interp, pb_interp, self.bar_config)
			self.bar_x = bar.bar_x
			self.bar_max_height = bar.max_height
			self.bars.append(bar)

		self.bar_span = self.width - self.bar_x
		self.bar_min_length = self.bar_span * self.bar_config["min_length"]
		self.bar_max_length = self.bar_span * self.bar_config["max_length"]

		self.compute_tickmarks(interp_windows["tickmark"])

	def _calculate_scale_and_offset(self, shortest_speedrun, longest_speedrun):
		"""
		pixels_length(duration) = scale * duration + offset
		"""

		# pixels_length(shortest_duration) = scale * shortest_duration + offset
		# bar_min_length = scale * shortest_duration + offset
		# offset = min_bar_length - scale * shortest_duration

		scale = (self.bar_max_length - self.bar_min_length) / (longest_speedrun - shortest_speedrun)
		offset = self.bar_min_length - (scale * shortest_speedrun)

		return scale, offset

	def _compute_scale_and_offset(self, date):
		shortest_speedrun = self.leaderboard.shortest_speedrun_interp.interpolate(date)
		longest_speedrun = self.leaderboard.longest_speedrun_interp.interpolate(date)

		return self._calculate_scale_and_offset(shortest_speedrun, longest_speedrun)

	# Calculate the length of a bar from the duration of its speedrun.
	def calculate_length(self, duration, scale, offset):
		return (scale * duration) + offset

	# Calculate the duration of a speedrun from the length of its bar.
	def calculate_duration(self, length, scale, offset):
		return (length - offset) / scale

	def compute_tickmarks(self, window_radius):
		self.tickmark_config["start"] = self.tickmark_config["start"] * self.bar_span
		self.tickmark_config["stop"] = self.tickmark_config["stop"] * self.bar_span

		self.tickmarks = {}

		# Add in the initial tickmarks.
		shortest_speedrun = self.leaderboard.first_shortest_speedrun
		longest_speedrun = self.leaderboard.first_longest_speedrun
		scale, offset = self._calculate_scale_and_offset(shortest_speedrun, longest_speedrun)

		# Calculate what the shortest and longest speedruns would be if they were directly on the left and right edges.
		shortest_speedrun = self.calculate_duration(self.tickmark_config["start"], scale, offset)
		longest_speedrun = self.calculate_duration(self.tickmark_config["stop"], scale, offset)

		for tickmark_duration in compute_tickmark_range(shortest_speedrun, longest_speedrun, self.tickmark_config["increments"], self.tickmark_config["min"]):
			self.tickmarks[tickmark_duration] = Tickmark(window_radius, 1)

		# Add in every other tickmark necessary.
		current_date = date_utcfromtimestamp(self.leaderboard.start_timestamp)
		stop_date = date.today()

		while current_date <= stop_date:
			current_datetime = current_datetime = date_to_datetime(current_date)

			scale, offset = self._compute_scale_and_offset(current_datetime)
			shortest_speedrun = self.calculate_duration(self.tickmark_config["start"], scale, offset)
			longest_speedrun = self.calculate_duration(self.tickmark_config["stop"], scale, offset)

			visible_tickmarks = set()

			for tickmark_duration in compute_tickmark_range(shortest_speedrun, longest_speedrun, self.tickmark_config["increments"], self.tickmark_config["min"]):
				if tickmark_duration not in self.tickmarks:
					self.tickmarks[tickmark_duration] = Tickmark(window_radius, 0)

				visible_tickmarks.add(tickmark_duration)

			for duration, tickmark in self.tickmarks.items():
				if duration in visible_tickmarks:
					tickmark.add_visibility(current_datetime, 1)

				else:
					tickmark.add_visibility(current_datetime, 0)

			current_date += timedelta(days=1)

		for tickmark in self.tickmarks.values():
			tickmark.optimize_data()

	def render_tickmarks(self, date, scale, offset):
		for duration, tickmark in self.tickmarks.items():
			if duration <= 0:
				continue

			visibility = tickmark.get_visibility(date)
			if visibility == 0:
				continue

			alpha = math.floor(255 * visibility)

			# Tickmark line
			tickmark_rect = pygame.Rect(0, 0, self.tickmark_config["width"], self.height)
			tickmark_rect.centerx = self.bar_x + self.calculate_length(duration, scale, offset)
			tickmark_rect.top = lerp(0, self.bar_max_height - self.bar_height, self.tickmark_config["top"])

			col = pygame.Color(*self.cols["tickmark"], alpha)
			pygame.gfxdraw.box(self.image, tickmark_rect, col)

			# Tickmark text
			text = format_duration(duration, 0)
			surf = self.fonts["tickmark"].render(text, True, col)
			surf.set_alpha(alpha)

			rect = surf.get_rect()
			rect.centerx = tickmark_rect.centerx
			rect.left = max(self.bar_x, rect.left)
			rect.bottom = tickmark_rect.top

			self.image.blit(surf, rect)

	def render(self, date):
		self.image.fill((*self.cols["bg"], 0))

		scale, offset = self._compute_scale_and_offset(date)

		self.render_tickmarks(date, scale, offset)

		blit_sequence = []

		for bar in self.bars:
			rank = self.rank_interpolation.interpolate(date, bar.runner.ranks)
			if rank >= self.top_ranks:
				continue

			bar.render(date, rank, scale, offset)

			top_y = bar.max_height
			bottom_y = self.height
			
			bar.rect.bottom = lerp(top_y, bottom_y, rank / (self.top_ranks-1))

			blit_sequence.append((bar.image, bar.rect))

		self.image.blits(blit_sequence)