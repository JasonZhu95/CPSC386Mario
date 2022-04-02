import pygame
from settings import screen_width, screen_height
from game_data import levels

class InfoScreen:
    def __init__(self, level, surface, create_level, win):
        # setup
        self.display_surface = surface
        self.current_level = level
        self.create_level = create_level
        self.win = win

        self.level_text = pygame.Rect((20, 50), (50, 100))
        self.time = pygame.time.get_ticks()

        # level display
        if not win:
            self.font = pygame.font.Font(None, 40)
            self.text_surf = self.font.render("", True, 'White')
            self.text_rect = self.text_surf.get_rect(center=(screen_width / 2, screen_height / 2))

            self.prompt_text_surf = self.font.render("Press Space to Start Game", True, 'White')
            self.prompt_text_rect = self.text_surf.get_rect(center=(screen_width / 2 - 150, screen_height / 2 + 300))
        else:
            self.font = pygame.font.Font(None, 40)
            self.text_surf = self.font.render("", True, 'White')
            self.text_rect = self.text_surf.get_rect(center=(screen_width / 2, screen_height / 2))

            self.prompt_text_surf = self.font.render("You Won!", True, 'White')
            self.prompt_text_rect = self.text_surf.get_rect(center=(screen_width / 2 - 150, screen_height / 2 + 300))

    def input(self):
        if pygame.time.get_ticks() - self.time > 2000:
            self.create_level(self.current_level)

    def run(self):
        self.input()
        pygame.draw.rect(self.display_surface, 'Red', self.level_text)
        self.display_surface.blit(self.text_surf, self.text_rect)
        self.display_surface.blit(self.prompt_text_surf, self.prompt_text_rect)