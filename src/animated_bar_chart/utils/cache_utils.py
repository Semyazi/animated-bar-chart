import json
import os

from animated_bar_chart.utils.io_utils import create_dirs


class Cache:
	def __init__(self, filepath, save_every=15):
		self._filepath = filepath

		if not self.load():
			self._data = {}

		self._save_cntr = 0
		self._save_every = save_every

	def load(self):
		try:
			with open(self._filepath) as file:
				self._data = json.load(file)
				return True
		
		except FileNotFoundError:
			return False

	def save(self):
		create_dirs(self._filepath)

		with open(self._filepath, "w") as file:
			json.dump(self._data, file)

	def __getitem__(self, key):
		return self._data[key]

	def __setitem__(self, key, value):
		self._data[key] = value
		self._save_cntr += 1

		if self._save_cntr % self._save_every == 0:
			self.save()

	def __contains__(self, key):
		return key in self._data

# Simple JSON cache for storing social media/profile picture urls to save network requests.
class ProfilePictureUrlCache(Cache):
	def __init__(self, save_every=30):
		super().__init__(os.environ["PFP_CACHE_PATH"], save_every)

	def save_pfp_url(self, src_id, social_media_platform, pfp_url):
		if pfp_url == None:
			return
		
		self[f"{src_id}:{social_media_platform}"] = pfp_url

	def get_pfp_url(self, src_id, social_media_platform):
		return self[f"{src_id}:{social_media_platform}"]

	def has_pfp_url(self, src_id, social_media_platform):
		return f"{src_id}:{social_media_platform}" in self