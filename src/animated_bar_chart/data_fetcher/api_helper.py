import srcomapi.datatypes as dt
from srcomapi import SpeedrunCom

from animated_bar_chart.utils.input_utils import choose_from_list

api = SpeedrunCom()


def choose_game_info():
	game_info = {}

	# Choose a game.
	games = api.search(dt.Game, {"name": input("What is the name of the game: ")})
	game_names = map(lambda game: game.name, games)
	game = games[choose_from_list("Please select a game", game_names)]
	game_info["gameId"] = game.id

	# Choose a category.
	num_of_categories = len(game.categories)

	# Remove any categories that are not strictly single player.
	for i, cat in enumerate(reversed(game.categories.copy())):
		players = cat.data["players"]
		if players["type"] != "exactly" or players["value"] != 1:
			del game.categories[num_of_categories - 1 - i]

	if len(game.categories) == 0:
		print("There are no single player categories.")
		return

	category_names = []

	for cat in game.categories:
		cat_type = cat.data["type"]

		if cat_type == "per-game":
			cat_type = "Full-game"

		elif cat_type == "per-level":
			cat_type = "Individual Level"

		else:
			cat_type = "Unknown type"

		category_names.append(f"{cat.name} ({cat_type})")

	category = game.categories[choose_from_list("Please choose a category", category_names)]
	game_info["categoryId"] = category.id

	if category.data["type"] == "per-level":
		# Choose a level.
		level_names = [level.name for level in game.levels]

		level = game.levels[choose_from_list("Please choose a level", level_names)]
		game_info["levelId"] = level.id

	# Choose variable restrictions.
	variable_restrictions = {}

	for var in category.variables:
		if not var.data["mandatory"]:
			continue

		var_name = var.data["name"]
		var_id = var.data["id"]

		choice_ids = [x for x in var.data["values"]["choices"].keys()]
		choice_names = [var.data["values"]["choices"][x] for x in choice_ids]

		choice_ids.insert(0, None)
		choice_names.insert(0, "Does not matter")

		choice = choice_ids[choose_from_list(f"Please choose an option for {var_name}", choice_names)]
		
		if choice != None:
			variable_restrictions[var_id] = choice

	game_info["values"] = []

	for var, val in variable_restrictions.items():
		game_info["values"].append({ "variableId": var, "valueIds": [val] })

	return game_info