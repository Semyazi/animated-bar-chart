import os

from requests.models import PreparedRequest

from animated_bar_chart.utils.async_utils import json_request, rate_limit


async def get_youtube_pfp_urls(name_urls):
	rpm = int(os.getenv("YOUTUBE_RPM"))
	name_urls = name_urls.items()

	awaitables = [_get_youtube_pfp_url(url) for _, url in name_urls]
	results = await rate_limit(awaitables, rpm)

	return {name: results[i] for i, (name, _) in enumerate(name_urls)}

async def _get_youtube_pfp_url(youtube_url):
	api_url = _get_youtube_api_url(youtube_url)

	if not api_url:
		return None

	results = await json_request(api_url)
	items = results.get("items", [])

	if len(items) > 0:
		return items[0]["snippet"]["thumbnails"]["high"]["url"]

def _get_youtube_api_url(youtube_url):
	youtube_url = youtube_url[24:]
	params = {
		"key": os.environ["YOUTUBE_API_KEY"],
		"part": "snippet",
		"maxResults": 1
	}

	if youtube_url.startswith("channel"):
		params["id"] = youtube_url[8:]

	elif youtube_url.startswith("user"):
		params["forUsername"] = youtube_url[5:]

	else:
		return None

	req = PreparedRequest()
	req.prepare_url("https://youtube.googleapis.com/youtube/v3/channels?", params)

	return req.url