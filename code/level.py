import pygame
from tiles import Tile, StaticTile
from settings import tile_size, screen_width, screen_height
from player import Player
from particles import ParticleEffect
from support import import_csv_layout, import_tiled_layout
from game_data import levels
from enemy import Enemy


class Level:
        def __init__(self, current_level, surface, create_info_screen, update_coins, update_health, cur_health):

            # Setting up Level
            self.display_surface = surface
            self.world_shift = 0
            self.current_x = None

            # Audio Setup
            self.coin_sound = pygame.mixer.Sound('../audio/effects/coin.wav')
            self.stomp_sound = pygame.mixer.Sound('../audio/effects/stomp.wav')
            self.hit_sound = pygame.mixer.Sound('../audio/effects/die.wav')
            self.mushroom_sound = pygame.mixer.Sound('../audio/effects/powerup.wav')
            self.flower_sound = pygame.mixer.Sound('../audio/effects/powerup.wav')

            self.current_level = current_level
            level_data = levels[self.current_level]
            level_content = level_data['content']
            self.next_level = level_data['unlock']
            self.create_info_screen = create_info_screen

            # ui
            self.update_coins = update_coins

            # level display
            self.font = pygame.font.Font(None, 40)
            self.text_surf = self.font.render(level_content, True, 'White')
            self.text_rect = self.text_surf.get_rect(center=(screen_width/2, screen_height/2))

            # goal
            self.goal = pygame.sprite.GroupSingle()

            # player
            self.player = pygame.sprite.GroupSingle()
            player_layout = import_csv_layout(level_data['player'])
            self.player_setup(player_layout, update_health, cur_health)

            # Dust Setup
            self.dust_sprite = pygame.sprite.GroupSingle()
            self.player_on_ground = False

            # explosion
            self.explosion_sprites = pygame.sprite.Group()

            # Setup the terrain
            terrain_layout = import_csv_layout(level_data['platforms'])
            self.terrain_sprites = self.create_tile_group(terrain_layout, 'platforms')

            #setup enemies
            enemy_layout = import_csv_layout(level_data['enemies'])
            self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemies')

            #constraints
            constraint_layout = import_csv_layout(level_data['constraints'])
            self.constraint_sprites = self.create_tile_group(constraint_layout, 'constraints')

            #coins
            coins_layout = import_csv_layout(level_data['coins'])
            self.coins = self.create_tile_group(coins_layout, 'coins')

            # flower
            flower_layout = import_csv_layout(level_data['flower'])
            self.flowers = self.create_tile_group(flower_layout, 'flower')

            # mushroom
            mushroom_layout = import_csv_layout(level_data['mushroom'])
            self.mushrooms = self.create_tile_group(mushroom_layout, 'mushroom')

        def run(self):

            self.enemy_wall_collision()
            self.display_surface.blit(self.text_surf, self.text_rect)

            # dust
            self.dust_sprite.update(self.world_shift)
            self.dust_sprite.draw(self.display_surface)

            # platforms
            self.terrain_sprites.draw(self.display_surface)
            self.terrain_sprites.update(self.world_shift)

            # enemy and constraints
            self.enemy_sprites.update(self.world_shift)
            self.enemy_sprites.draw(self.display_surface)
            self.constraint_sprites.update(self.world_shift)

            # explosion
            self.explosion_sprites.update(self.world_shift)
            self.explosion_sprites.draw(self.display_surface)

            #coins
            self.coins.update(self.world_shift)
            self.coins.draw(self.display_surface)

            # mushroom
            self.mushrooms.update(self.world_shift)
            self.mushrooms.draw(self.display_surface)

            # flower
            self.flowers.update(self.world_shift)
            self.flowers.draw(self.display_surface)

            # player
            self.player.update()
            self.check_death()
            self.check_win()
            self.horizontal_movement_collision()
            self.get_player_on_ground()
            self.vertical_movement_collision()
            self.create_landing_dust()
            self.scroll_x()
            self.player.draw(self.display_surface)
            self.check_coin_collision()
            self.check_enemy_collision()

            # goal
            self.goal.update(self.world_shift)
            self.goal.draw(self.display_surface)

        def player_setup(self, layout, update_health, cur_health):
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if col == '0':
                        sprite = Player((x, y), self.display_surface, self.create_jump_particles, update_health, cur_health)
                        self.player.add(sprite)

                    if col == '1':
                        goal_surface = pygame.image.load('../graphics/character/setup_tiles.png')
                        sprite = StaticTile((x, y), tile_size,  goal_surface)
                        self.goal.add(sprite)

        def create_tile_group(self, layout, type):
            sprite_group = pygame.sprite.Group()

            for row_index, row in enumerate(layout):  # loop through the csv to get values of each entry
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * tile_size
                        y = row_index * tile_size

                        if type == 'platforms':
                            # each index in the list is going to have an id based on tiled
                            platform_tile_list = import_tiled_layout('../graphics/terrain/terrain_tiles.png')
                            tile_surface = platform_tile_list[int(col)]  # get the tile for the current column value
                            sprite = StaticTile((x, y), tile_size, tile_surface)
                            sprite_group.add(sprite)

                        if type == 'enemies':
                            sprite = Enemy((x, y), tile_size)
                            sprite_group.add(sprite)

                        if type == 'constraints':
                            sprite = Tile((x, y), tile_size)
                            sprite_group.add(sprite)

                        if type == 'coins':
                            sprite = Tile((x, y), tile_size)
                            sprite_group.add(sprite)

                        if type == 'flower':
                            sprite = Tile((x, y), tile_size)
                            sprite_group.add(sprite)

                        if type == 'mushroom':
                            sprite = Tile((x, y), tile_size)
                            sprite_group.add(sprite)

            return sprite_group

        def enemy_wall_collision(self):
            for enemy in self.enemy_sprites.sprites():
                if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False):
                    enemy.reverse()

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

        def scroll_x(self):
            player = self.player.sprite
            player_x = player.rect.centerx
            direction_x = player.direction.x

            if player_x < screen_width / 4 and direction_x < 0:
                self.world_shift = 8
                player.speed = 0
            elif player_x > screen_width - (screen_width / 4) and direction_x > 0:
                self.world_shift = -8
                player.speed = 0
            else:
                self.world_shift = 0
                player.speed = 8

        def horizontal_movement_collision(self):
            player = self.player.sprite
            player.rect.x += player.direction.x * player.speed
            collidable_sprites= self.terrain_sprites.sprites()
            for sprite in collidable_sprites:
                if sprite.rect.colliderect(player.rect):
                    if player.direction.x < 0:
                        player.rect.left = sprite.rect.right
                        player.touching_left = True
                        self.current_x = player.rect.left
                    elif player.direction.x > 0:
                        player.rect.right = sprite.rect.left
                        player.touching_right = True
                        self.current_x = player.rect.right

            if player.touching_left and (player.rect.left < self.current_x or player.direction.x >= 0):
                player.touching_left = False
            if player.touching_right and (player.rect.right > self.current_x or player.direction.x <= 0):
                player.touching_right = False

        def vertical_movement_collision(self):
            player = self.player.sprite
            player.apply_gravity()
            collidable_sprites = self.terrain_sprites.sprites()
            for sprite in collidable_sprites:
                if sprite.rect.colliderect(player.rect):
                    if player.direction.y > 0:
                        player.rect.bottom = sprite.rect.top
                        player.direction.y = 0
                        player.touching_ground = True
                    elif player.direction.y < 0:
                        player.rect.top = sprite.rect.bottom
                        player.direction.y = 0
                        player.touching_ceiling = True

            if player.touching_ground and player.direction.y < 0 or player.direction.y > 1:
                player.touching_ground = False
            if player.touching_ceiling and player.direction.y > 0:
                player.touching_ceiling = False

        def check_death(self):
            if self.player.sprite.rect.top > screen_height:
                self.hit_sound.play()
                self.create_info_screen(self.current_level)

        def check_win(self):
            if pygame.sprite.spritecollide(self.player.sprite, self.goal, False):
                self.create_info_screen(self.next_level)

        def check_coin_collision(self):
            collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coins, True)
            if collided_coins:
                self.coin_sound.play()
                for coin in collided_coins:
                    self.update_coins(1)

        def check_mushroom_collision(self):
            collided_mushrooms = pygame.sprite.spritecollide(self.player.sprite, self.mushrooms, True)
            player = self.player.sprite
            if collided_mushrooms:
                self.mushroom_sound.play()
                player.cur_health = 2

        def check_flower_collision(self):
            collided_flowers = pygame.sprite.spritecollide(self.player.sprite, self.flowers, True)
            player = self.player.sprite
            if collided_flowers:
                self.flower_sound.play()
                player.cur_health = 3

        def check_enemy_collision(self):
            enemy_collisions = pygame.sprite.spritecollide(self.player.sprite, self.enemy_sprites, False)

            if enemy_collisions:
                for enemy in enemy_collisions:
                    enemy_center = enemy.rect.centery
                    enemy_top = enemy.rect.top
                    player_bottom = self.player.sprite.rect.bottom
                    if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
                        self.stomp_sound.play()
                        self.player.sprite.direction.y = -15
                        explosion_sprite = ParticleEffect(enemy.rect.center, 'explosion')
                        self.explosion_sprites.add(explosion_sprite)
                        enemy.kill()
                    else:
                         #self.player.sprite.take_dmg(-1)
                         print('damage turned off')

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