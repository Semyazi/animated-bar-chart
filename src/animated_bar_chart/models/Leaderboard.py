import json
import os
from datetime import date, timedelta

from animated_bar_chart.models.Runner import Runner
from animated_bar_chart.models.Speedrun import Speedrun
from animated_bar_chart.utils.date_utils import (date_to_datetime,
                                                 date_utcfromtimestamp)
from animated_bar_chart.utils.interpolation_utils import (
    PreloadedCosineInterpolation, optimize_data)


class Leaderboard:
	def __init__(self, runners, top_ranks):
		self.runners = runners
		self.top_ranks = top_ranks

	def _get_start(self):
		# Find the earliest run submitted.
		self.start_timestamp = float("inf")

		for runner in self.runners.values():
			for run in runner.speedruns:
				self.start_timestamp = min(run.timestamp, self.start_timestamp)

	def _compute_ranks(self):
		# Calculate the rank of every runner.
		# TODO: Optimize this garbage with a priority queue.
		current_date = date_utcfromtimestamp(self.start_timestamp)
		stop_date = date.today()

		while current_date <= stop_date:
			current_datetime = current_datetime = date_to_datetime(current_date)

			runners = list(self.runners.values())
			runners.sort(key=lambda runner: runner.get_pb_duration(current_datetime))

			for rank, runner in enumerate(runners):
				# If the runner has no submitted run at this time, their PB duration will be infinity and they will have no rank.
				if runner.get_pb_duration(current_datetime) == float("inf"):
					#print("my pb duration is inf", runner.src_id, runner.name, runner.speedruns)
					continue

				# This is done so that if a runner does not appear in the top 10, for example, their bar will appear just off screen as the next bar that is not visible. Keep in mind that in this case, the ranks go from 0-9, so rank 10 would be off screen.
				rank = min(rank, self.top_ranks)

				runner.ranks.append({"date": date_to_datetime(current_date), "rank": rank})

			current_date += timedelta(days=1)

		# Remove duplicate rank information for faster interpolation.
		for runner in self.runners.values():
			runner.ranks = optimize_data(runner.ranks, lambda rank: rank["rank"])
		
	def compute(self):
		self._get_start()
		self._compute_ranks()

	def load_runners(self):
		for runner in self.runners.values():
			runner.load_pfp()

		Runner.load_flags(self.runners)

	def _get_top_pbs(self, date):
		# Note: These PBs are not guarenteed to be sorted.
		top_pbs = []

		for runner in self.runners.values():
			if runner.get_rank(date) < self.top_ranks:
				top_pbs.append(runner.get_pb_duration(date))

		return top_pbs

	def compute_shortest_and_longest_speedruns(self, window_radius):
		current_date = date_utcfromtimestamp(self.start_timestamp)
		stop_date = date.today()

		defaults = []
		shortest_speedruns = []
		longest_speedruns = []

		while current_date <= stop_date:
			current_datetime = date_to_datetime(current_date)
			pbs = self._get_top_pbs(current_datetime)

			# The first time there are more than two runners on the leaderboard, use them as the defaults.
			if len(defaults) == 0 and len(pbs) >= 2 and min(pbs) != max(pbs):
				defaults.append(min(pbs))
				defaults.append(max(pbs))

			if len(defaults) == 2:
				shortest_speedruns.append({"date": current_datetime, "duration": min(pbs)})
				longest_speedruns.append({"date": current_datetime, "duration": max(pbs)})

			current_date += timedelta(days=1)

		get_time = lambda datum: datum["date"]
		get_value = lambda datum: datum["duration"]

		self.first_shortest_speedrun, self.first_longest_speedrun = defaults

		self.shortest_speedrun_interp = PreloadedCosineInterpolation(shortest_speedruns, window_radius, get_time, get_value, defaults[0])
		self.longest_speedrun_interp = PreloadedCosineInterpolation(longest_speedruns, window_radius, get_time, get_value, defaults[1])

	@staticmethod
	def get_runner_best_rank(runner):
		ranks = (rank["rank"] for rank in runner.ranks)
		return float("inf") if len(runner.ranks) == 0 else min(ranks)

	@staticmethod
	def load(top_ranks):
		filepath = os.environ["RUNNERS_PATH"]
		raw_data = json.load(open(filepath))
		runners = {}

		for runner_data in raw_data:
			src_id = runner_data["src_id"]
			runner_data["speedruns"] = [Speedrun(**speedrun) for speedrun in runner_data["speedruns"]]
			runners[src_id] = Runner(**runner_data)

		leaderboard = Leaderboard(runners, top_ranks)
		leaderboard.compute()
		leaderboard.load_runners()

		return leaderboard