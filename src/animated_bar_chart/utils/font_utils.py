import math
import os

import pygame


def _create_default_font(size):
	return pygame.font.SysFont(pygame.font.get_default_font(), math.floor(size))

def create_font(size):
	try:
		return pygame.font.Font(os.environ["FONT_PATH"], math.floor(size))

	except:
		return _create_default_font(size)
		
def create_monospaced_font(size):
	try:
		return pygame.font.Font(os.environ["MONOSPACED_FONT_PATH"], math.floor(size))

	except:
		return _create_default_font(size)

def get_centery(font):
	return font.get_ascent() / 2

def create_relative_font(font_config, multiplier):
	monospaced = font_config["monospaced"]
	relative_size = font_config["relative_size"]

	func = create_monospaced_font if monospaced else create_font
	return func(multiplier * relative_size)

def create_relative_fonts(font_config, multiplier):
	return { font_name: create_relative_font(font_cfg, multiplier) for font_name, font_cfg in font_config.items()}