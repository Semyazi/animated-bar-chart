import base64
import json
import time

from animated_bar_chart.utils.async_utils import json_request


async def get_data(game_info):
	# Download every page of data.
	pages = [await _get_page(game_info, 1)]
	total_pages = pages[0]["pagination"]["pages"]

	for page in range(2, total_pages+1):
		pages.append(await _get_page(game_info, page))

	return pages

def _create_query(game_info, page):
	query = {"params": {}, "page": page, "vary": int(time.time())}
	query["params"] |= game_info
	query["params"] |= {"timer": 0, "regionIds": [], "platformIds": [], "video": 0, "obsolete": 1}

	return query

def _create_url(query):
	query_encoded = json.dumps(query, separators=(',', ':')).encode('ascii')
	query_encoded = base64.b64encode(query_encoded).rstrip(b"=").decode()

	return f"https://www.speedrun.com/api/v2/GetGameLeaderboard?_r={query_encoded}"

async def _get_page(game_info, page):
	query = _create_query(game_info, page)
	url = _create_url(query)

	return (await json_request(url))["leaderboard"]