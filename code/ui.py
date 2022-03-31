import pygame

class UI:
    def __init__(self, surface):

        self.display_surface = surface

        self.coin = pygame.image.load('../graphics/UI/coin_ui.png').convert_alpha()
        self.coin_rect = self.coin.get_rect(topleft=(600, 40))
        self.font = pygame.font.Font(None, 30)

    def show_coins(self, amount):
        self.display_surface.blit(self.coin, self.coin_rect)
        coin_amount_surf = self.font.render('x' + str(amount), False, '#33323d')
        coin_amount_rect = coin_amount_surf.get_rect(midleft=(self.coin_rect.right, self.coin_rect.centery))
        self.display_surface.blit(coin_amount_surf, coin_amount_rect)




