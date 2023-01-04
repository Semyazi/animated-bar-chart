from dotenv import load_dotenv

load_dotenv()

import argparse
import logging

import scripts.chart_data
import scripts.fetch_data
import scripts.get_game_info

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(
	prog="Animated Bar Chart",
	description="Utilities for creating animated bar charts from speedrun.com data."
)

parser.add_argument(
	"run_type",
	choices=["get_game_info", "fetch_data", "chart_data"]
)

args = parser.parse_args()
run_type = args.run_type

if run_type == "get_game_info":
	scripts.get_game_info.main()

elif run_type == "fetch_data":
	scripts.fetch_data.main()

elif run_type == "chart_data":
	scripts.chart_data.main()