import os
from io import BytesIO

import requests
from PIL import Image

from animated_bar_chart.utils.io_utils import create_dirs


def download_country_flags(country_codes):
	for country_code in country_codes:
		flag_url = _get_flag_url(country_code)
		flag = Image.open(BytesIO(requests.get(flag_url).content))

		filepath = os.path.join(os.environ["FLAG_PATH"], f"{country_code}.png")
		create_dirs(filepath)
		flag.save(filepath)

def _get_flag_url(country_code):
	return f"https://www.speedrun.com/images/flags/{country_code}.png"