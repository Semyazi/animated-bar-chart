import json
import logging
import os

from animated_bar_chart.data_fetcher.country_flags.fetcher import \
    download_country_flags
from animated_bar_chart.data_fetcher.profile_picture.fetcher import (
    download_pfps, get_profile_picture_urls)
from animated_bar_chart.data_fetcher.src_fetcher import get_data
from animated_bar_chart.models.Leaderboard import Leaderboard
from animated_bar_chart.models.Runner import Runner
from animated_bar_chart.models.Speedrun import Speedrun
from animated_bar_chart.utils.cache_utils import ProfilePictureUrlCache
from animated_bar_chart.utils.col_utils import get_image_col, id_to_col
from animated_bar_chart.utils.preprocessing_utils import preprocess_comment


class SrcPreprocessor:
	DURATION_PRIORITY = ("igt", "time", "timeWithLoads")

	def __init__(self, game_info, top_ranks, col="color1Id", col_type="dark_col"):
		self.game_info = game_info # Game id, category id, values
		self.top_ranks = top_ranks # How many top runners should we keep track of (how many bars)
		self.col = col # either "color1Id" or "color2Id"
		self.col_type = col_type # either "dark_col" or "light_col"

		self.pfp_cache = ProfilePictureUrlCache()

	@staticmethod
	def get_speedrun_timestamp(run):
		"""
		if "dateSubmitted" not in run:
			# The time is sometimes unreliable, so we need two data points.
			return None

		if int(abs(run["dateSubmitted"] - run["date"]) / 86400) <= SrcPreprocessor.MAX_DAY_WAIT:
			return run["date"]
		"""
		return run.get("date", None)
	
	async def fetch(self):
		self.raw_data = await get_data(self.game_info)

	def _get_runner(self, run):
		if len(run["playerIds"]) == 0:
			return None
		
		if len(run["playerIds"]) > 1:
			raise Exception("This project only works for single player games.", run["playerIds"])

		return run["playerIds"][0]

	def _get_duration(self, run):
		for timing_method in self.DURATION_PRIORITY:
			if timing_method in run:
				return run[timing_method]

		raise Exception("A speedrun was found that does not have any timing information whatsoever.", run)

	def get_runners(self):
		self.runners = {}

		for player in self.raw_data[0]["players"]:
			src_id = player["id"]
			name = player["name"]
			src_col = id_to_col(player[self.col], self.col_type) if self.col in player else None

			country_code = player.get("areaId", "")[:2]
			country_code = country_code if len(country_code) == 2 else None

			self.runners[src_id] = Runner(src_id, name, src_col, country_code)

		# Get all of the speedruns
		for page in self.raw_data:
			for run in page["runs"]:
				runner = self._get_runner(run)
				if not runner:
					continue

				duration = self._get_duration(run)
				comment = preprocess_comment(run.get("comment", ""))
				timestamp = run.get("date", None)

				self.runners[runner].speedruns.append(Speedrun(duration, comment, timestamp))

		for runner in self.runners.values():
			runner.preprocess_speedruns()

	def filter_runners(self):
		# Only keep runners that appear in the top top_ranks at least once.
		self.leaderboard = Leaderboard(self.runners, self.top_ranks)
		self.leaderboard.compute()

		top_runner_ids = set()

		for runner in self.runners.values():
			# If the top_ranks is 10, then the possible ranks are 0-9, and we only want runners whose best rank is at most 9.
			if self.leaderboard.get_runner_best_rank(runner) < self.top_ranks:
				top_runner_ids.add(runner.src_id)

		# Filter out the runners that do not appear in the top ranks.
		self.runners = {k:v for k,v in self.runners.items() if k in top_runner_ids}

	async def get_runners_profile_picture_urls(self):
		await get_profile_picture_urls(self.runners.keys(), self.pfp_cache)

	def download_runners_profile_pictures(self):
		download_pfps(self.runners.keys(), self.pfp_cache)

	def download_country_flags(self):
		country_codes = set()

		for runner in self.runners.values():
			if runner.country_code:
				country_codes.add(runner.country_code)

		download_country_flags(country_codes)

	def get_pfp_cols(self):
		for runner in self.runners.values():
			filepath = os.path.join(os.environ["PFP_PATH"], f"{runner.src_id}.png")

			if os.path.exists(filepath):
				runner.pfp_col = get_image_col(filepath)

	async def collect_data(self):
		logging.info("Getting speedrun.com data...")
		await self.fetch()

		logging.info("Parsing speedrun.com data...")
		self.get_runners()

		logging.info(f"Removing runners that didn't make the top {self.top_ranks}...")
		self.filter_runners()

		logging.info("Getting runners' profile picture urls...")
		await self.get_runners_profile_picture_urls()

		logging.info("Downloading runners' profile pictures...")
		self.download_runners_profile_pictures()

		logging.info("Downloading runners' country flags...")
		self.download_country_flags()

		logging.info("Extracting runners' profile picture cols...")
		self.get_pfp_cols()

	def save_data(self):
		logging.info("Saving data...")
		with open(os.environ["RUNNERS_PATH"], "w") as file:
			json.dump([runner.to_object() for runner in self.runners.values()], file)