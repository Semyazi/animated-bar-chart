from animated_bar_chart.utils.async_utils import json_request


async def get_social_media_urls(src_id, social_media_whitelist=("twitch", "youtube")):
	url = f"https://www.speedrun.com/api/v1/users/{src_id}"
	data = await json_request(url)

	if data.get("status") == 404: return {}
	data = data["data"]

	social_medias = {}

	for social_media in social_media_whitelist:
		if data[social_media]:
			social_medias[social_media] = data[social_media]["uri"]

	return social_medias