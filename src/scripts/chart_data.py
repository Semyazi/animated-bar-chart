import os
from datetime import date, timedelta

import pygame

from animated_bar_chart.graphics import Renderer, Timer
from animated_bar_chart.models import Leaderboard
from animated_bar_chart.utils.date_utils import (date_to_datetime,
                                                 date_utcfromtimestamp,
                                                 datetime_utcfromtimestamp)

pygame.init()
pygame.freetype.set_default_resolution(256)

# Feel free to edit these constants.
RENDERER_CONFIG = {
	"size": (1920, 1080),
	"fps": 60,
	"crf": 18,
	"output": "animated-bar-chart.mp4",
	"record": True
}

TIMER_CONFIG = {}
TIMER_CONFIG["animation_length"] = 180 # how long you want the animation to be in seconds (this overrides days_per_second if you set it)
TIMER_CONFIG["days_per_second"] = 15 # days of the animation per real second
TIMER_CONFIG["start_offset"] = 2 # number of seconds before the first speedrun was submitted to start the animation
TIMER_CONFIG["stop_offset"] = 5 # number of seconds to wait at the end before stopping the animation

# These control the speed of the cosine interpolation and are measured in seconds.
INTERP_WINDOWS = {
	"rank": 0.35,
	"scale": 1.5,
	"duration": 0.42,
	"pb": 0.5,
	"tickmark": 0.5
}

COLS = {
	"bg": (0, 0, 0),
	"text": (255, 255, 255),
	"tickmark": (77, 77, 77),
	"min_brightness": 20,
	"max_brightness": 75
}

# Most of these will be multiplied by the bar fill height.
BAR_CONFIG = {
	"bar_fill": 0.6,
	"min_pfp_size": 1,
	"max_pfp_size": 2.5,
	"top_padding": 1.57,
	"comment_top_padding": 0.1,
	"name_left_padding": 0.06,
	"name_right_padding": 0.2,
	"duration_left_padding": 0.12,
	"pfp_right_padding": 0.16,
	"flag_height": 0.45,
	"chevron_width": 0.18,
	"min_length": 0.2, # 0-1, 0 meaning no length, 1 meaning max length
	"max_length": 0.8, # 0-1, 0 meaning no length, 1 meaning max length
}

TICKMARK_CONFIG = {
	"increments": (0.2, 0.25, 0.5, 1, 5, 10, 15, 30, 60, 120, 300, 600, 1200, 3000, 3600, 7200),
	"min": 4, # the fewest number of tickmarks allowed at once
	"width": 4,
	"top": 0.85, # 0-1, 0 being at the top of the WR pfp, 1 being at the top of the highest bar
	"start": 0.01, # 0-1, this represents where the tickmarks start, 0 being at the right of the chevron, and 1 being at the end of the right side of the screen
	"stop": 1 # 0-1, this represents where the tickmarks end, 0 being at the right of the chevron, and 1 being at the end of the right side of the screen
}

FONT_CONFIG = {
	"name": { "monospaced": False, "relative_size": 0.9 },
	"comment": { "monospaced": False, "relative_size": 0.5 },
	"duration_hms": { "monospaced": True, "relative_size": 1 },
	"duration_ms": { "monospaced": True, "relative_size": 0.6 },
	"tickmark": { "monospaced": True, "relative_size": 1 },
	"wr_duration": { "monospaced": False, "relative_size": 1 },
	"date": { "monospaced": True, "relative_size": 0.045 }
}

DATE_CONFIG = {
	"x": 0.98, #0-1, 0 representing the left of the screen, 1 representing the right of the screen
	"y": 0.005 #0-1, 0 representing the top of the screen, 1 representing the bottom of the screen
}

TOP_RANKS = int(os.environ["TOP_RANKS"])

def main():
	global INTERP_WINDOWS
	
	leaderboard = Leaderboard.load(TOP_RANKS)

	if TIMER_CONFIG.get("animation_length"):
		real_start_date = date_utcfromtimestamp(leaderboard.start_timestamp)
		real_stop_date = date.today()

		TIMER_CONFIG["days_per_second"] = ((real_stop_date - real_start_date).days + 1) / TIMER_CONFIG["animation_length"]

	TIMER_CONFIG["start_offset"] = timedelta(days=TIMER_CONFIG["start_offset"] * TIMER_CONFIG["days_per_second"])
	TIMER_CONFIG["stop_offset"] = timedelta(days=TIMER_CONFIG["stop_offset"] * TIMER_CONFIG["days_per_second"])

	start_date = datetime_utcfromtimestamp(leaderboard.start_timestamp) - TIMER_CONFIG["start_offset"]
	stop_date = date_to_datetime(date.today()) + TIMER_CONFIG["stop_offset"]

	TIMER_CONFIG["frames_per_day"] = RENDERER_CONFIG["fps"] / TIMER_CONFIG["days_per_second"]
	timer = Timer(start_date, stop_date, TIMER_CONFIG["frames_per_day"])

	# Scale the interpolation windows based on the number of days per second.
	INTERP_WINDOWS = {k: timedelta(days=s * TIMER_CONFIG["days_per_second"]) for k, s in INTERP_WINDOWS.items()}
	leaderboard.compute_shortest_and_longest_speedruns(INTERP_WINDOWS["scale"])

	renderer = Renderer(RENDERER_CONFIG, timer, leaderboard, INTERP_WINDOWS, COLS, BAR_CONFIG, TICKMARK_CONFIG, FONT_CONFIG, DATE_CONFIG)
	renderer.render_video()
