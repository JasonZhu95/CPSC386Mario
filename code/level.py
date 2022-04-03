import pygame
from tiles import Tile, StaticTile
from settings import tile_size, screen_width, screen_height
from player import Player
from player import fireball_group
from particles import ParticleEffect
from support import import_csv_layout, import_tiled_layout
from game_data import levels
from enemy import Enemy


class Level:
        def __init__(self, current_level, surface, create_info_screen, update_coins, update_health, cur_health, increment_score, check_game_over, create_level, exited_portal):

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
            self.create_level = create_level

            # ui
            self.update_coins = update_coins
            self.increment_score = increment_score

            self.update_health = update_health
            self.check_game_over = check_game_over

            # level display
            self.font = pygame.font.Font(None, 40)
            self.text_surf = self.font.render(level_content, True, 'White')
            self.text_rect = self.text_surf.get_rect(center=(screen_width/2, screen_height/2))

            # goal
            self.goal = pygame.sprite.GroupSingle()

            portal_layout = import_csv_layout(level_data['portals'])
            self.portals = self.create_tile_group(portal_layout, 'entry_portals')

            exit_portal_layout = import_csv_layout(level_data['portals'])
            self.exit_portal = self.create_tile_group(exit_portal_layout, 'exit_portal')

            if current_level == 0 and exited_portal:
                self.player_start = self.exit_portal.rect.topleft 
                self.world_shift = -2000
            else:
                self.player_start = None

            # player
            self.player = pygame.sprite.GroupSingle()
            player_layout = import_csv_layout(level_data['player'])
            self.player_setup(player_layout, update_health, cur_health)

            # fireball
            self.fireball_group = fireball_group

            # flower and mushroom
            self.flowers = pygame.sprite.Group()
            self.mushrooms = pygame.sprite.Group()
            powerups_layout = import_csv_layout(level_data['powerups'])
            self.powerups_setup(powerups_layout)

            # Dust Setup
            self.dust_sprite = pygame.sprite.GroupSingle()
            self.player_on_ground = False

            # explosion
            self.explosion_sprites = pygame.sprite.Group()

            # background setup
            background_layout = import_csv_layout(level_data['background'])
            self.background_sprites = self.create_tile_group(background_layout, 'background')

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


        def run(self):

            self.enemy_wall_collision()
            self.display_surface.blit(self.text_surf, self.text_rect)

            # dust
            self.dust_sprite.update(self.world_shift)
            self.dust_sprite.draw(self.display_surface)

            # background
            self.background_sprites.draw(self.display_surface)
            self.background_sprites.update(self.world_shift)
            
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
            self.check_flower_collision()
            self.check_mushroom_collision()
            self.check_enemy_collision()
            self.check_enter_pipe()

            # goal
            self.goal.update(self.world_shift)

            # portal
            self.portals.update(self.world_shift)

        def player_setup(self, layout, update_health, cur_health):
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    x = col_index * tile_size
                    y = row_index * tile_size


                    if col == '0':
                        if self.player_start is not None:
                            sprite = Player(self.player_start, self.display_surface, self.create_jump_particles, update_health, cur_health)
                        else:
                            sprite = Player((x,y), self.display_surface, self.create_jump_particles, update_health, cur_health)
                        self.player.add(sprite)


                    if col == '1':
                        sprite = Tile((x, y), tile_size)
                        self.goal.add(sprite)

        def powerups_setup(self, layout):
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if col == '2':
                        mushroom_surface = pygame.image.load('../graphics/powerups/1UP_Mushroom.png').convert_alpha()
                        sprite = StaticTile((x, y), tile_size, mushroom_surface)
                        self.mushrooms.add(sprite)

                    if col == '3':
                        flower_surface = pygame.image.load('../graphics/powerups/Fire_Flower.png').convert_alpha()
                        sprite = StaticTile((x, y), tile_size,  flower_surface)
                        self.flowers.add(sprite)

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

                        if type == 'background':
                            background_tile_list = import_tiled_layout('../graphics/terrain/terrain_tiles.png')
                            tile_surface = background_tile_list[int(col)]  # get the tile for the current column value
                            sprite = StaticTile((x, y), tile_size, tile_surface)
                            sprite_group.add(sprite)

                        if type == 'constraints':
                            sprite = Tile((x, y), tile_size)
                            sprite_group.add(sprite)

                        if type == 'coins':
                            coins_tile_list = import_tiled_layout('../graphics/terrain/terrain_tiles.png')
                            tile_surface = coins_tile_list[int(col)]  # get the tile for the current column value
                            sprite = StaticTile((x, y), tile_size, tile_surface)
                            sprite_group.add(sprite)

                        if type == 'entry_portals' and col == '0':
                            sprite = Tile((x, y), tile_size)
                            sprite_group.add(sprite)

                        if type == 'exit_portal' and col == '1':
                            sprite = Tile((x, y), tile_size)
                            return sprite

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

            if player_x < screen_width / 2 and direction_x < 0:
                self.world_shift = 8
                player.speed = 0
            elif player_x > screen_width - (screen_width / 2) and direction_x > 0:
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
                self.cur_health = 0
                self.update_health(-3)
                self.check_game_over()

        def check_win(self):
            if pygame.sprite.spritecollide(self.player.sprite, self.goal, False):
                self.create_info_screen(0, win=True)


        def check_coin_collision(self):
            collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coins, True)
            if collided_coins:
                self.coin_sound.play()
                self.increment_score(200)
                for coin in collided_coins:
                    self.update_coins(1)

        def check_mushroom_collision(self):
            collided_mushrooms = pygame.sprite.spritecollide(self.player.sprite, self.mushrooms, True)
            if collided_mushrooms:
                self.mushroom_sound.play()
                self.increment_score(1000)
                self.player.sprite.get_mushroom()

        def check_flower_collision(self):
            collided_flowers = pygame.sprite.spritecollide(self.player.sprite, self.flowers, True)
            if collided_flowers:
                self.flower_sound.play()
                self.increment_score(1000)
                self.player.sprite.get_flower()

        def check_enter_pipe(self):

            portals = pygame.sprite.spritecollide(self.player.sprite, self.portals, False)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN]:
                print(self.player.sprite.rect.topleft)
            for portal in portals:
                if keys[pygame.K_DOWN]:
                    if self.current_level == 1:
                        self.create_level(self.next_level, True)
                    else:
                        self.create_level(self.next_level)
                    break

        def check_enemy_collision(self):
            enemy_collisions = pygame.sprite.spritecollide(self.player.sprite, self.enemy_sprites, False)
            fireball_collisions = pygame.sprite.groupcollide(self.fireball_group, self.enemy_sprites, True, True)

            if enemy_collisions:
                for enemy in enemy_collisions:
                    enemy_center = enemy.rect.centery
                    enemy_top = enemy.rect.top
                    player_bottom = self.player.sprite.rect.bottom
                    if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
                        self.increment_score(100)
                        self.stomp_sound.play()
                        self.player.sprite.direction.y = -15
                        explosion_sprite = ParticleEffect(enemy.rect.center, 'explosion')
                        self.explosion_sprites.add(explosion_sprite)
                        enemy.kill()
                    else:
                        self.player.sprite.take_dmg(-1)

            if fireball_collisions:
                for enemy in fireball_collisions:
                    self.increment_score(100)
                    explosion_sprite2 = ParticleEffect(enemy.rect.center, 'explosion')
                    self.explosion_sprites.add(explosion_sprite2)
                    enemy.kill()
