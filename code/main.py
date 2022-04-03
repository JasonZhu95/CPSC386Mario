import pygame, sys
from settings import *
from level import Level
from info_screen import InfoScreen
from ui import UI
import time

class Game:
    def __init__(self):
        self.max_health = 3
        self.cur_health = 1
        self.coins = 0
        self.score = 0
        self.font = pygame.font.SysFont(None, 40)
        self.high_score = 0
        self.time_left = 400
        self.start_time = time.time()

        # Audio
        self.level_bg_music = pygame.mixer.Sound('../audio/level_music.mp3')
        self.hit_sound = pygame.mixer.Sound('../audio/effects/die.wav')

        # overworld creation
        self.info_screen = InfoScreen(0, screen, self.create_level, win=False)
        self.status = 'info_screen'

        # ui
        self.ui = UI(screen)

    def draw_score(self, surface):
        txt1 = self.font.render('Mario', True, (255, 255, 255))
        surface.blit(txt1, (10, 10))
        txt2 = self.font.render(str(self.score), True, (255, 255, 255))
        surface.blit(txt2, (10, 30))

    def draw_high_score(self, surface):
        txt1 = self.font.render('Current High Score: ' + str(self.high_score), True, (255, 255, 255))
        surface.blit(txt1, (screen_width / 2 - 150, screen_height / 2))

    def draw_level_count(self, surface):
        txt1 = self.font.render('Level', True, (255, 255, 255))
        surface.blit(txt1, (2*(screen_width / 4), 10))
        txt2 = self.font.render('1-1', True, (255, 255, 255))
        surface.blit(txt2, (2*(screen_width / 4) + 10, 30))

    def draw_time(self, surface):
        txt1 = self.font.render('Time', True, (255, 255, 255))
        surface.blit(txt1, (3*(screen_width / 4), 10))
        txt2 = self.font.render(str(self.time_left), True, (255, 255, 255))
        surface.blit(txt2, (3*(screen_width / 4) + 10, 30))

    def update_time(self):
        if time.time() > self.start_time + 1:
            self.time_left -= 1
            self.start_time = time.time()

    def increment_score(self, amount):
        self.score += amount

    def return_score(self):
        return self.score

    def reset_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
        self.score = 0

    def create_level(self, current_level, exited_portal = False):
        self.level_bg_music.stop()
        self.level = Level(current_level, screen, self.create_info_screen, self.update_coins, self.update_health, self.cur_health, self.increment_score, self.check_game_over, self.create_level, exited_portal)
        self.status = 'level'
        self.level_bg_music.play(loops=-1)

    def create_info_screen(self, current_level, win=False):
        self.level_bg_music.stop()
        self.info_screen = InfoScreen(current_level, screen, self.create_level, win=win)
        self.status = 'info_screen'

    def update_coins(self, amount):
        self.coins += amount

    def update_health(self, amount):
        self.cur_health += amount
        print("health is " + str(self.cur_health))

    def check_game_over(self):
        if self.cur_health <= 0:
            self.level_bg_music.stop()
            self.hit_sound.play()
            self.cur_health = 1
            self.coins = 0
            self.reset_score()
            self.info_screen = InfoScreen(0, screen, self.create_level, win=False)
            self.status = 'info_screen'

    def run(self):
        if self.status == 'info_screen':
            self.info_screen.run()
            self.draw_high_score(screen)
        else:
            self.level.run()
            self.ui.show_coins(self.coins)
            self.check_game_over()
            self.draw_score(screen)
            self.draw_level_count(screen)
            self.update_time()
            self.draw_time(screen)



# Pygame setup
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height), flags= pygame.SCALED)
clock = pygame.time.Clock()
game = Game()
blue = pygame.Color("#6185f8")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(blue)
    game.run()

    pygame.display.update()
    clock.tick(60)