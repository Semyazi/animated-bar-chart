import bisect
import os
import random

import pygame

from animated_bar_chart.utils.date_utils import datetime_utcfromtimestamp


class Runner:
	__slots__ = ("src_id", "name", "src_col", "pfp_col", "country_code", "speedruns", "_pb_indices", "ranks", "pfp", "flag", "_col")
	__saveable__ = ("src_id", "name", "src_col", "pfp_col", "country_code", "speedruns")

	speedrun_timestamp_key = lambda speedrun: datetime_utcfromtimestamp(speedrun.timestamp)
	speedrun_timestamp_key_dict = lambda speedrun: datetime_utcfromtimestamp(speedrun["timestamp"])
	speedrun_duration_key = lambda speedrun: speedrun.duration
	speedrun_index_key_dict = lambda speedrun: speedrun["index"]
	rank_date_key = lambda rank: rank["date"]
	
	def __init__(self, src_id, name, src_col, country_code, pfp_col=None, speedruns=[]):
		self.src_id = src_id
		self.name = name
		self.src_col = src_col
		self.pfp = None
		self.flag = None
		self.pfp_col = pfp_col
		self.country_code = country_code
		self._col = None

		self.speedruns = speedruns.copy()
		self._pb_indices = None
		self.ranks = []

	def to_object(self):
		speedrun_objects = [speedrun.to_object() for speedrun in self.speedruns]

		return {
			k: (speedrun_objects if k == "speedruns" else self.__getattribute__(k)) for k in self.__saveable__
		}

	def preprocess_speedruns(self):
		# Make sure that all of the speedruns are sorted from earliest to latest, and that only PBs are stored.

		self.speedruns = list(filter(lambda speedrun: speedrun.timestamp, self.speedruns))

		self.speedruns.sort(key=lambda speedrun: speedrun.timestamp)
		speedruns = self.speedruns
		self.speedruns = []

		current_pb = float("inf")

		for speedrun in speedruns:
			if speedrun.duration < current_pb:
				self.speedruns.append(speedrun)
				current_pb = speedrun.duration
		
	def get_pb(self, date):
		# Get the runner's personal best run at the date.
		idx = bisect.bisect_right(self.speedruns, date, key=Runner.speedrun_timestamp_key) - 1
		return None if idx < 0 else self.speedruns[idx]

	def get_pb_duration(self, date):
		speedrun = self.get_pb(date)
		return speedrun.duration if speedrun else float("inf")

	def get_rank_obj(self, date):
		# Get the runner's rank object at the date.
		idx = bisect.bisect_right(self.ranks, date, key=Runner.rank_date_key) - 1
		return None if idx < 0 else self.ranks[idx]

	def get_rank(self, date):
		# Get the runner's rank at the date.
		rank_obj = self.get_rank_obj(date)
		return float("inf") if not rank_obj else rank_obj["rank"]

	def load_pfp(self):
		filepath = os.path.join(os.environ["PFP_PATH"], f"{self.src_id}.png")

		if os.path.exists(filepath):
			self.pfp = pygame.image.load(filepath)

	@property
	def col(self):
		if self._col:
			return self._col

		if self.pfp_col:
			self._col = self.pfp_col

		elif self.src_col:
			self._col = self.src_col

		else:
			self._col = [random.randint(0, 255) for _ in range(3)]

		return self._col

	@property
	def pb_indices(self):
		if self._pb_indices:
			return self._pb_indices

		self._pb_indices = [{"timestamp": speedrun.timestamp, "index": i} for i, speedrun in enumerate(self.speedruns)]
		return self._pb_indices

	@staticmethod
	def load_flags(runners):
		country_code_to_flag = {}

		for runner in runners.values():
			cc = runner.country_code

			if cc and cc not in country_code_to_flag:
				filepath = os.path.join(os.environ["FLAG_PATH"], f"{cc}.png")
				country_code_to_flag[cc] = pygame.image.load(filepath)			

			if cc:
				runner.flag = country_code_to_flag[cc]