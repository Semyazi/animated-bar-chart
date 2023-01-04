import pygame

from animated_bar_chart.graphics.Recorder import Recorder


class BaseRenderer:
	def __init__(self, size, output="animated-bar-chart.mp4", fps=60, crf=18, record=True):
		self._size = size
		self._fps = fps

		self._recorder = Recorder(self._fps, crf, output) if record else None
		self._screen = pygame.display.set_mode(self._size)
		self._clock = pygame.time.Clock()

	def render_frame(self, frame):
		return True

	def record_frame(self):
		if self._recorder:
			self._recorder.record_frame(self._screen)

	def _save_recording(self):
		if self._recorder:
			self._recorder.save()

	def render_video(self):
		frame = 0
		running = True

		while running:
			self._clock.tick(self._fps)

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
					break

			running = min(self.render_frame(frame), running)			
			self.record_frame()

			pygame.display.update()
			frame += 1

		self._save_recording()