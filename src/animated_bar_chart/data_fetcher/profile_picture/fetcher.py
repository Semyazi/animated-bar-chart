import logging
import os
from io import BytesIO

import requests
from PIL import Image

from animated_bar_chart.data_fetcher.profile_picture.social_media_fetcher import \
    get_social_media_urls
from animated_bar_chart.data_fetcher.profile_picture.twitch_fetcher import \
    get_twitch_pfp_urls
from animated_bar_chart.data_fetcher.profile_picture.youtube_fetcher import \
    get_youtube_pfp_urls
from animated_bar_chart.utils.cache_utils import ProfilePictureUrlCache
from animated_bar_chart.utils.io_utils import create_dirs


async def get_profile_picture_urls(src_ids, cache: ProfilePictureUrlCache):
	social_media_dict = {
		"twitch": {},
		"youtube": {}
	}

	for src_id in src_ids:
		for sm, url in (await get_social_media_urls(src_id)).items():
			# If we already have the profile picture url of this user on this social media platform, we can skip them.
			if cache.has_pfp_url(src_id, sm):
				continue
			
			social_media_dict[sm][src_id] = url

	logging.info("Getting twitch profile picture urls...")
	social_media_dict["twitch"] = await get_twitch_pfp_urls(social_media_dict["twitch"])

	logging.info("Getting youtube profile picture urls...")
	social_media_dict["youtube"] = await get_youtube_pfp_urls(social_media_dict["youtube"])

	for social_media_platform, pfp_urls in social_media_dict.items():	
		for src_id, pfp_url in pfp_urls.items():
			cache.save_pfp_url(src_id, social_media_platform, pfp_url)

	cache.save()

def download_pfps(src_ids, cache: ProfilePictureUrlCache, priority=("twitch", "youtube")):
	for src_id in src_ids:
		# Attempt downloading the speedrun.com profile picture.
		if _save_pfp_url(src_id, f"https://www.speedrun.com/userasset/{src_id}/image"):
			continue

		for social_media_platform in priority:
			if not cache.has_pfp_url(src_id, social_media_platform):
				continue

			# We only need one profile picture, so we can break out of the loop as soon as one url works.
			if _save_pfp_url(src_id, cache.get_pfp_url(src_id, social_media_platform)):
				break

def _save_pfp_url(src_id, pfp_url):
	try:
		pfp = Image.open(BytesIO(requests.get(pfp_url).content))

		return _save_pfp(src_id, pfp)

	except:
		return False

def _save_pfp(src_id, pfp):
	if pfp.size[0] != pfp.size[1]:
		return False

	filepath = os.path.join(os.environ["PFP_PATH"], f"{src_id}.png")

	create_dirs(filepath)
	pfp.save(filepath)

	return True