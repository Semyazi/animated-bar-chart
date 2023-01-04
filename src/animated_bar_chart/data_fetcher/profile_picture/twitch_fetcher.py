import os

import aiohttp

from animated_bar_chart.utils.async_utils import rate_limit


async def get_twitch_pfp_urls(name_urls):
	src_id_to_name = { src_id: _convert_twitch_url_to_name(url) for src_id, url in name_urls.items() }
	pfp_urls_by_name = await _get_twitch_pfp_urls_by_name(list(src_id_to_name.values()))

	return { src_id: pfp_urls_by_name[name] if name in pfp_urls_by_name else None for src_id, name in src_id_to_name.items() }

# API Documentation: https://dev.twitch.tv/docs/api/reference#get-users
async def _get_twitch_pfp_urls_by_name(names):
	group_size = int(os.getenv("TWITCH_MAX_USERS_PER_REQUEST"))

	access_token = await _get_access_token()

	names_to_pfp = {}
	awaitables = []

	for i in range(0, len(names), group_size):
		name_group = names[i: i+group_size]
		awaitables.append(_get_twitch_pfp_urls_group(name_group, access_token))

	for urls in await rate_limit(awaitables, int(os.getenv("TWITCH_RPM"))):
		names_to_pfp = names_to_pfp | urls

	return names_to_pfp

# Get an access token from the twitch API.
async def _get_access_token():
	headers = {"Content-Type": "application/x-www-form-urlencoded"}
	auth = {"client_id": os.getenv("TWITCH_CLIENT_ID"), "client_secret": os.getenv("TWITCH_CLIENT_SECRET"), "grant_type": "client_credentials"}

	async with aiohttp.ClientSession(headers=headers) as sess:
		async with sess.post("https://id.twitch.tv/oauth2/token", data=auth) as res:
			return await res.json()

# Convert a list of names into a dictionary of names -> profile picture urls (in one request).
async def _get_twitch_pfp_urls_group(names, token):
	assert len(names) <= int(os.getenv("TWITCH_MAX_USERS_PER_REQUEST"))
	assert token["token_type"] == "bearer"

	url = "https://api.twitch.tv/helix/users?"
	url += "&".join((f"login={name}" for name in names))

	access_token = token["access_token"]
	auth = {
		"Authorization": f"Bearer {access_token}",
		"Client-Id": os.getenv("TWITCH_CLIENT_ID")
	}

	async with aiohttp.ClientSession(headers=auth) as sess:
		async with sess.get(url) as res:
			data = (await res.json())["data"]

	results = { datum["login"].lower(): datum["profile_image_url"] for datum in data }

	return { name: results[name.lower()] for name in names if name.lower() in results }

def _convert_twitch_url_to_name(url):
	return url[22:]