import asyncio
import json
import os

from animated_bar_chart.data_fetcher.src_preprocessor import SrcPreprocessor


def main():
	with open(os.environ["GAME_INFO_PATH"]) as file:
		game_info = json.load(file)

	top_ranks = int(os.environ["TOP_RANKS"])

	src_preprocessor = SrcPreprocessor(game_info, top_ranks)

	asyncio.run(src_preprocessor.collect_data())
	src_preprocessor.save_data()