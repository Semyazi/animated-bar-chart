import math
from datetime import datetime

import pygame
import pygame.gfxdraw

from animated_bar_chart.models import Runner
from animated_bar_chart.utils.date_utils import (date_to_datetime,
                                                 datetime_utcfromtimestamp)
from animated_bar_chart.utils.font_utils import get_centery
from animated_bar_chart.utils.formatting_utils import (format_days,
                                                       format_duration)
from animated_bar_chart.utils.interpolation_utils import (CosineInterpolation,
                                                          clamp, lerp)
from animated_bar_chart.utils.misc_utils import multiply_subdict


class Bar:
	CHEVRON_SCALING_FACTOR = 64

	def __init__(self, runner: Runner, width, height, fonts, cols, duration_interp: CosineInterpolation, pb_interp: CosineInterpolation, bar_config):
		self.runner = runner

		self.width = width
		self.height = height # Just including the bar and the comment.

		self.fonts = fonts

		self.cols = cols.copy()
		self._calculate_primary_col()

		self.bar_config = bar_config

		bar_fill = self.bar_config["bar_fill"]
		self.bar_fill_height = bar_fill * self.height # Just includes the part of the bar that gets filled.

		self.sizes = multiply_subdict(bar_config, ("min_pfp_size", "max_pfp_size", "top_padding", "comment_top_padding", "name_left_padding", "name_right_padding", "duration_left_padding", "pfp_right_padding", "flag_height", "chevron_width"), self.bar_fill_height)

		self.bar_x = self.sizes["max_pfp_size"] + self.sizes["pfp_right_padding"] + self.sizes["chevron_width"]
		self.bar_span = self.width - self.bar_x

		self.max_height = self.sizes["max_pfp_size"] + self.sizes["top_padding"] + (self.height - self.bar_fill_height)

		#self.max_height = (self.wr_pfp_multiplier * self.bar_fill_proportion * self.height) + (self.height * (1-self.bar_fill_proportion)) + self.top_padding
		self.bar_empty_height = self.height - self.bar_fill_height

		self.duration_interp = duration_interp
		self.pb_interp = pb_interp

		# Scale the runner's profile picture.
		self.pfp = pygame.transform.smoothscale(self.runner.pfp.convert_alpha(), 2*(self.sizes["min_pfp_size"],)) if self.runner.pfp else None

		# Scale the runner's flag.
		if self.runner.flag:
			aspect_ratio = self.runner.flag.get_width() / self.runner.flag.get_height()
			h = self.sizes["flag_height"]
			w = h * aspect_ratio

			self.flag = pygame.transform.smoothscale(self.runner.flag.convert_alpha(), (w, h))

		else:
			self.flag = None

		# Calculate bar coordinates.
		self.bar_top = self.max_height - self.height
		self.bar_bottom = self.bar_top + self.bar_fill_height - 1
		#self.bar_center = lerp(self.bar_top, self.bar_bottom, 0.5)
		
		self.bar_radius = self.bar_fill_height / 2

		self.create_chevron()

		self.image = pygame.Surface((self.width, self.max_height), pygame.SRCALPHA)
		self.image = self.image.convert_alpha()

		self.rect = self.image.get_rect()

	def _calculate_primary_col(self):
		self.cols["primary"] = pygame.Color(self.runner.col)
		
		hsla = list(self.cols["primary"].hsla)
		hsla[2] = clamp(hsla[2], self.cols["min_brightness"], self.cols["max_brightness"])

		self.cols["primary"].hsla = hsla

	def calculate_bar_length(self, date, scale, offset):
		pb_duration_interp = self.duration_interp.interpolate(date, self.runner.speedruns)
		bar_length = (scale * pb_duration_interp) + offset
		bar_length = round(bar_length)

		return bar_length

	def render_pfp(self, rank):
		if not self.pfp:
			return

		pfp_size = lerp(self.sizes["max_pfp_size"], self.sizes["min_pfp_size"], rank)
		pfp_size = clamp(pfp_size, self.sizes["min_pfp_size"], self.sizes["max_pfp_size"])
		
		pfp_rect = pygame.Rect(0, 0, pfp_size, pfp_size)
		pfp_rect.bottomright = (self.sizes["max_pfp_size"], self.bar_bottom)

		if pfp_size == self.sizes["min_pfp_size"]:
			pfp = self.pfp

		else:
			pfp = pygame.transform.smoothscale(self.runner.pfp.convert_alpha(), (pfp_size, pfp_size))

		self.image.blit(pfp, pfp_rect)

	def create_chevron(self):
		actual_size = (self.sizes["chevron_width"], self.bar_fill_height)
		scaled_size = (actual_size[0] * self.CHEVRON_SCALING_FACTOR, actual_size[1] * self.CHEVRON_SCALING_FACTOR)

		surf = pygame.Surface(scaled_size)
		rect = surf.get_rect()

		points = (
			(rect.right, rect.top),
			(rect.left, lerp(rect.top, rect.bottom, 0.25)),
			(rect.right, lerp(rect.top, rect.bottom, 0.5)),
			(rect.left, lerp(rect.top, rect.bottom, 0.75)),
			(rect.right, rect.bottom),
		)

		pygame.gfxdraw.filled_polygon(surf, points, self.cols["primary"])
		pygame.gfxdraw.aapolygon(surf, points, self.cols["primary"])

		self.chevron_surf = pygame.transform.smoothscale(surf, actual_size)
		self.chevron_rect = self.chevron_surf.get_rect()
		self.chevron_rect.top = self.bar_top
		self.chevron_rect.right = self.bar_x

	def render_chevron(self):
		self.image.blit(self.chevron_surf, self.chevron_rect)

	def render_bar(self, date, scale, offset):
		bar_length = self.calculate_bar_length(date, scale, offset)
		bar_length = max(0, bar_length)
		
		bar_rect = pygame.Rect(self.bar_x, self.bar_top, bar_length, self.bar_fill_height)

		pygame.gfxdraw.box(self.image, bar_rect, self.cols["primary"])

		return bar_length

	def render_name_and_flag(self):
		surf = self.fonts["name"].render(self.runner.name, True, self.cols["text"])
		name_rect = surf.get_rect()
		name_rect.top = self.bar_top
		name_rect.left = self.bar_x + self.sizes["name_left_padding"]
		# move the top down by the distance between the centre of the font and the centre of the bar
		name_rect.top += self.bar_radius - get_centery(self.fonts["name"])

		self.image.blit(surf, name_rect)

		if not self.flag:
			return

		flag_rect = self.flag.get_rect()
		flag_rect.left = name_rect.right + self.sizes["name_right_padding"]
		flag_rect.bottom = name_rect.top + self.fonts["name"].get_ascent()

		self.image.blit(self.flag, flag_rect)

	def render_pb(self, date, bar_length):
		pb_duration = self.runner.get_pb_duration(date)

		duration_text = format_duration(pb_duration)

		hms, ms = duration_text.split(".")
		ms = "." + ms

		# Render the hours, minutes, and seconds part.
		hms_surf = self.fonts["duration_hms"].render(hms, True, self.cols["text"])

		hms_rect = hms_surf.get_rect()
		hms_rect.left = self.bar_x + bar_length + self.sizes["duration_left_padding"]
		hms_rect.top = self.bar_top
		hms_rect.top += self.bar_radius - get_centery(self.fonts["duration_hms"])

		self.image.blit(hms_surf, hms_rect)

		# Render the milliseconds.
		ms_surf = self.fonts["duration_ms"].render(ms, True, self.cols["text"])

		ms_rect = ms_surf.get_rect()
		ms_rect.left = hms_rect.right
		ms_rect.top = hms_rect.top
		ms_rect.top += self.fonts["duration_hms"].get_ascent() - self.fonts["duration_ms"].get_ascent()

		self.image.blit(ms_surf, ms_rect)

		# Render the comment.
		pb_index = self.pb_interp.interpolate(date, self.runner.pb_indices)

		self.render_comment(self.image, math.floor(pb_index), 1 - (pb_index % 1))
		self.render_comment(self.image, math.ceil(pb_index), pb_index % 1)

	def render_comment(self, bar, index, opacity):
		if opacity == 0:
			return
		
		comment = self.runner.speedruns[index].comment

		if not comment:
			return
		
		surf = self.fonts["comment"].render(comment, True, self.cols["primary"])
		surf.set_alpha(255 * opacity)

		rect = surf.get_rect()
		rect.left = self.bar_x
		rect.top = self.bar_bottom + self.sizes["comment_top_padding"]

		bar.blit(surf, rect)

	def render_wr_duration(self, date):
		if self.runner.get_rank(date) > 0:
			return

		wr_start = self.runner.get_rank_obj(date)["date"]
		wr_stop = min(date, date_to_datetime(datetime.now()))

		wr_days = (wr_stop - wr_start).days + 1 # Add 1 to include the current day.
		wr_duration = format_days(wr_days)

		text = f"WR for {wr_duration}"
		surf = self.fonts["wr_duration"].render(text, True, self.cols["text"])

		rect = surf.get_rect()
		rect.left = 0
		rect.bottom = self.max_height - self.sizes["max_pfp_size"] - self.bar_empty_height

		self.image.blit(surf, rect)

	def render(self, date, rank, scale, offset):
		self.image.fill((*self.cols["bg"], 0))

		bar_length = self.render_bar(date, scale, offset)
		self.render_pfp(rank)
		self.render_chevron()
		self.render_name_and_flag()
		self.render_pb(date, bar_length)
		self.render_wr_duration(date)