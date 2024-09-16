import os
import pygame
import config


class Floor:
    HEIGHT = 112  # Desired height of the floor
    CHUNKS = 3

    def __init__(self, screen_height):
        self.y = screen_height - self.HEIGHT
        self.chunk_width = 0
        self.floor_sprite = None
        self._chunks = []

        self.load_sprite()
        self.initialize_chunks()

    def load_sprite(self):
        # Load and scale the floor sprite
        self.floor_sprite = pygame.transform.scale2x(pygame.image.load(os.path.join(config.TEXTURES_DIR, "base.png")).convert_alpha())
        self.chunk_width = self.floor_sprite.get_width()

    def initialize_chunks(self):
        # Initialize the chunks with positions
        self._chunks = [[self.floor_sprite, i * self.chunk_width] for i in range(self.CHUNKS)]

    def draw(self, screen):
        # Draw each chunk at its current position
        for chunk in self._chunks:
            screen.blit(chunk[0], (chunk[1], self.y))
