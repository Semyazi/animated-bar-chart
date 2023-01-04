import io
from subprocess import PIPE, Popen

import pygame


class Recorder:
    def __init__(self, fps, crf, output):
        self._p = Popen(['ffmpeg', '-y', '-f', 'image2pipe', '-vcodec', 'bmp', '-r', str(fps), '-i',
                        '-', '-an', '-vcodec', 'h264', '-pix_fmt', 'yuv420p', '-crf', str(crf), output], stdin=PIPE)

    def record_frame(self, surface):
        with io.BytesIO() as output:
            pygame.image.save(surface, output, 'BMP')
            contents = output.getvalue()
            self._p.stdin.write(contents)

    def save(self):
        self._p.stdin.close()
        self._p.wait()