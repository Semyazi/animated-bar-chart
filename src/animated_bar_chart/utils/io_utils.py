import os


def create_dirs(filepath):
	os.makedirs(os.path.dirname(filepath), exist_ok=True)