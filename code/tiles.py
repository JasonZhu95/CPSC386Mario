import pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.image = pygame.Surface((size, size)) # square tile
        self.image.fill('grey')
        self.rect = self.image.get_rect(topleft = pos)

    def update(self, x_shift): #shifts the tile with x_shift value
        self.rect.x += x_shift
