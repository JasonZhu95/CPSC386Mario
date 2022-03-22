import pygame
from tiles import Tile
from settings import tile_size, screen_width
from player import Player
from particles import ParticleEffect
from support import import_csv_layout

class Level:
    def __init__(self, level_data, surface):

        # Setting up Level
        self.display_surface = surface
        self.setup_level(level_data)
        self.world_shift = 0
        self.current_x = 0

        #player
        self.player = pygame.sprite.GroupSingle()

        # Dust Setup
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        terrain_layout = import_csv_layout(level_data['platforms'])
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'platforms')


    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout): #loop through the csv to get values of each entry
            for col_index, col in enumerate(row):
                if col != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'platforms':
                        sprite = Tile((x, y), tile_size)
                        sprite_group.add(sprite)
        return sprite_group

    def run(self):
        self.terrain_sprites.draw(self.display_surface)
        self.terrain_sprites.update(-5)

    def create_jump_particles(self, pos):
        if self.player.sprite.facing_direction:
            pos -= pygame.math.Vector2(10, 5)
        else:
            pos += pygame.math.Vector2(10, -5)
        jump_particle_sprite = ParticleEffect(pos, 'jump')
        self.dust_sprite.add(jump_particle_sprite)

    def get_player_on_ground(self):
        if self.player.sprite.touching_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.touching_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_direction:
                offset = pygame.math.Vector2(10, 15)
            else:
                offset = pygame.math.Vector2(-10, 15)
            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset, 'land')
            self.dust_sprite.add(fall_dust_particle)

    def setup_level(self, layout):
        self.tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()

        for row_index,row in enumerate(layout):
            for col_index,cell in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size

                if cell == 'X':
                    tile = Tile((x,y), tile_size)
                    self.tiles.add(tile)
                if cell == 'P':
                    player_sprite = Player((x,y), self.display_surface, self.create_jump_particles)
                    self.player.add(player_sprite)



    # def scroll_x(self):
    #     player = self.player.sprite
    #     player_x = player.rect.centerx
    #     direction_x = player.direction.x
    #
    #     if player_x < screen_width / 4 and direction_x < 0:
    #         self.world_shift = 8
    #         player.speed = 0
    #     elif player_x > screen_width - (screen_width / 4) and direction_x > 0:
    #         self.world_shift = -8
    #         player.speed = 0
    #     else:
    #         self.world_shift = 0
    #         player.speed = 8
    #
    # def horizontal_movement_collision(self):
    #     player = self.player.sprite
    #     player.rect.x += player.direction.x * player.speed
    #
    #     for sprite in self.tiles.sprites():
    #         if sprite.rect.colliderect(player.rect):
    #             if player.direction.x < 0:
    #                 player.rect.left = sprite.rect.right
    #                 player.touching_left = True
    #                 self.current_x = player.rect.left
    #             elif player.direction.x > 0:
    #                 player.rect.right = sprite.rect.left
    #                 player.touching_right = True
    #                 self.current_x = player.rect.right
    #
    #     if player.touching_left and (player.rect.left < self.current_x or player.direction.x >= 0):
    #         player.touching_left = False
    #     if player.touching_right and (player.rect.right > self.current_x or player.direction.x <= 0):
    #         player.touching_right = False
    #
    # def vertical_movement_collision(self):
    #     player = self.player.sprite
    #     player.apply_gravity()
    #
    #     for sprite in self.tiles.sprites():
    #         if sprite.rect.colliderect(player.rect):
    #             if player.direction.y > 0:
    #                 player.rect.bottom = sprite.rect.top
    #                 player.direction.y = 0
    #                 player.touching_ground = True
    #             elif player.direction.y < 0:
    #                 player.rect.top = sprite.rect.bottom
    #                 player.direction.y = 0
    #                 player.touching_ceiling = True
    #
    #     if player.touching_ground and player.direction.y < 0 or player.direction.y > 1:
    #         player.touching_ground = False
    #     if player.touching_ceiling and player.direction.y > 0:
    #         player.touching_ceiling = False
    #
    # def draw(self):
    #     # Dust Particles
    #     self.dust_sprite.update(self.world_shift)
    #     self.dust_sprite.draw(self.display_surface)
    #
    #     # Level tiles
    #     self.tiles.update(self.world_shift)
    #     self.tiles.draw(self.display_surface)
    #     self.scroll_x()
    #
    #     # Player
    #     self.player.update()
    #     self.horizontal_movement_collision()
    #     self.get_player_on_ground()
    #     self.vertical_movement_collision()
    #     self.create_landing_dust()
    #     self.player.draw(self.display_surface)