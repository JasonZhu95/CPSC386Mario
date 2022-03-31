import pygame, sys
from settings import *
from level import Level
from info_screen import InfoScreen
from ui import UI




class Game:
    def __init__(self):
        self.max_health = 3
        self.cur_health = 1
        self.coins = 0

        # overworld creation
        self.info_screen = InfoScreen(0, screen, self.create_level)
        self.status = 'info_screen'

        # ui
        self.ui = UI(screen)

    def create_level(self, current_level):
        self.level = Level(current_level, screen, self.create_info_screen, self.update_coins)
        self.status = 'level'

    def create_info_screen(self, current_level):
        self.info_screen = InfoScreen(current_level, screen, self.create_level)
        self.status = 'info_screen'

    def update_coins(self, amount):
        self.coins += amount

    def run(self):
        if self.status == 'info_screen':
            self.info_screen.run()
        else:
            self.level.run()
            self.ui.show_coins(self.coins)

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
game = Game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('grey')
    game.run()

    pygame.display.update()
    clock.tick(60)