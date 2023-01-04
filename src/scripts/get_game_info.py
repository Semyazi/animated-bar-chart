import json
import os

from animated_bar_chart.data_fetcher.api_helper import choose_game_info
from animated_bar_chart.utils.io_utils import create_dirs


def main():
	game_info = choose_game_info()
	filepath = os.environ["GAME_INFO_PATH"]

	create_dirs(filepath)
	
	with open(filepath, "w") as file:
		json.dump(game_info, file)