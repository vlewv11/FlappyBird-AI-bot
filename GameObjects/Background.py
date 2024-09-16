import os
import pygame
import config


class Background:
    SPEED = 0.5
    CHUNKS = 4

    def __init__(self):
        self.bg_sprite = None
        self.load_sprite()
        self.chunk_width = self.bg_sprite.get_width()
        self.y = 0
        self._chunks = []
        for x in range(self.CHUNKS):
            self._chunks.append([self.bg_sprite, x * self.chunk_width])

    def load_sprite(self):
        self.bg_sprite = pygame.transform.scale(pygame.image.load(os.path.join(config.TEXTURES_DIR, "background-day.png")).convert_alpha(), (480, 700))

    def get_last_chunk_offset(self):
        offset = 0
        for chunk in self._chunks:
            if chunk[1] > offset:
                offset = chunk[1]
        return offset

    def draw(self, screen):
        for chunk in self._chunks:
            screen.blit(chunk[0], (chunk[1], self.y))
