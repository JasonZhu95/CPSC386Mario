import pygame
from support import import_folder, import_tiled_layout

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.image = pygame.Surface((size, size))  # square tile
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift): #shifts the tile with x_shift value
        self.rect.x += x_shift

# Basic tile that has no features
class StaticTile(Tile):
    def __init__(self, pos, size, surface):
        super().__init__(pos, size)
        self.image = surface

class AnimatedTile(Tile):
    def __init__(self, pos, size, path):
        super().__init__(pos, size)
        self.frames = import_folder(path)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

    def animate(self):
        self.frame_index += 0.15
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, x_shift):
        self.animate()
        self.rect.x += x_shift





