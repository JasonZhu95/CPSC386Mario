import pygame
from support import import_folder
from math import sin

fireball_group = pygame.sprite.Group()

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, surface, create_jump_particles, update_health, cur_health):
        super().__init__()
        self.import_character_assets()
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)
        self.fireball_group = fireball_group

        # FireballTimer
        self.previous_time = pygame.time.get_ticks()
        self.current_time = pygame.time.get_ticks()

        # health
        self.cur_health = cur_health
        self.update_health = update_health
        self.invincible = False
        self.invincible_duration = 400
        self.hurt_time = 0

        # Dust Particles
        self.import_dust_run_particles()
        self.dust_frame_index = 0
        self.dust_animation_speed = 0.15
        self.display_surface = surface
        self.create_jump_particles = create_jump_particles

        # Player Movement
        self.speed = 8
        self.direction = pygame.math.Vector2(0, 0)
        self.gravity = 0.8
        self.jump_speed = -22

        # Player Status
        self.status = 'idleSmall'
        self.facing_direction = True
        self.touching_ground = False
        self.touching_ceiling = False
        self.touching_left = False
        self.touching_right = False

        # Player Audio
        self.jump_sound = pygame.mixer.Sound('../audio/effects/jump.wav')

    def import_character_assets(self):
        character_path = '../graphics/character/'
        self.animations = {'idle':[],'run':[],'jump':[],'fall':[],'idleSmall':[],
                           'runSmall':[],'jumpSmall':[],'fallSmall':[],'idleFire':[],
                           'runFire':[],'jumpFire':[],'fallFire':[],'fire':[]}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def import_dust_run_particles(self):
        self.dust_run_particles = import_folder('../graphics/character/dust_particles/run')

    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        image = animation[int(self.frame_index)]
        if self.facing_direction:
            self.image = image
        else:
            flipped_image = pygame.transform.flip(image, True, False)
            self.image = flipped_image

        if self.invincible:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

        if self.touching_ground and self.touching_right:
            self.rect = self.image.get_rect(bottomright = self.rect.bottomright)
        elif self.touching_ground and self.touching_left:
            self.rect = self.image.get_rect(bottomleft = self.rect.bottomleft)
        elif self.touching_ground:
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
        elif self.touching_ceiling and self.touching_right:
            self.rect = self.image.get_rect(topright = self.rect.topright)
        elif self.touching_ceiling and self.touching_left:
            self.rect = self.image.get_rect(topleft = self.rect.topleft)
        elif self.touching_ceiling:
            self.rect = self.image.get_rect(midtop = self.rect.midtop)

    def run_dust_animation(self):
        if (self.status == 'run' or self.status == 'runSmall' or self.status == 'runFire') and self.touching_ground:
            self.dust_frame_index += self.dust_animation_speed
            if self.dust_frame_index >= len(self.dust_run_particles):
                self.dust_frame_index = 0

            dust_particle = self.dust_run_particles[int(self.dust_frame_index)]

            if self.facing_direction:
                pos = self.rect.bottomleft - pygame.math.Vector2(6,10)
                self.display_surface.blit(dust_particle, pos)
            else:
                pos = self.rect.bottomright - pygame.math.Vector2(6, 10)
                flipped_dust_particle = pygame.transform.flip(dust_particle, True, False)
                self.display_surface.blit(flipped_dust_particle, pos)

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.facing_direction = True
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.facing_direction = False
        else:
            self.direction.x = 0

        if keys[pygame.K_SPACE] and self.touching_ground:
            self.jump()
            self.create_jump_particles(self.rect.midbottom)

        if keys[pygame.K_z] and self.cur_health == 3:
            if self.current_time - self.previous_time > 300:
                self.previous_time = self.current_time
                self.status = 'fire'
                self.fireball_group.add(self.shoot_fireball())

    def get_status(self):
        if self.direction.y < 0:
            if self.cur_health == 1:
                self.status = 'jumpSmall'
            if self.cur_health == 2:
                self.status = 'jump'
            if self.cur_health == 3:
                self.status = 'jumpFire'
        elif self.direction.y > 1:
            if self.cur_health == 1:
                self.status = 'fallSmall'
            if self.cur_health == 2:
                self.status = 'fall'
            if self.cur_health == 3:
                self.status = 'fallFire'
        else:
            if self.direction.x != 0:
                if self.cur_health == 1:
                    self.status = 'runSmall'
                if self.cur_health == 2:
                    self.status = 'run'
                if self.cur_health == 3:
                    self.status = 'runFire'
            else:
                if self.cur_health == 1:
                    self.status = 'idleSmall'
                if self.cur_health == 2:
                    self.status = 'idle'
                if self.cur_health == 3:
                    self.status = 'idleFire'

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed
        self.jump_sound.play()

    def shoot_fireball(self):
        return Fireball(self.rect.x, self.rect.y, self.facing_direction)

    def take_dmg(self, amount):
        if not self.invincible:
            print("damage taken")
            self.cur_health = self.cur_health - 1
            self.update_health(amount)
            self.invincible = True
            self.hurt_time = pygame.time.get_ticks()

    def get_mushroom(self):
        if self.cur_health == 1:
            self.cur_health = 2
            self.update_health(1)

    def get_flower(self):
        if self.cur_health == 1:
            self.cur_health = 3
            self.update_health(2)

        if self.cur_health == 2:
            self.cur_health = 3
            self.update_health(1)

    def invincibility_timer(self):
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.hurt_time >= self.invincible_duration:
                self.invincible = False

    def wave_value(self):
        value = sin(pygame.time.get_ticks())
        if value >= 0:
            return 255
        else:
            return 0

    def update(self):
        self.get_input()
        self.get_status()
        self.animate()
        self.run_dust_animation()
        self.invincibility_timer()
        self.wave_value()
        self.fireball_group.update()
        self.fireball_group.draw(self.display_surface)
        self.current_time = pygame.time.get_ticks()

class Fireball(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, facing_direction):
        super().__init__()
        self.image = pygame.image.load('../graphics/enemy/fireball.png')
        self.facing_direction = facing_direction
        self.rect = self.image.get_rect(center = (pos_x, pos_y + 60))

    def update(self):
        if self.facing_direction:
            self.rect.x += 5
        else:
            self.rect.x -= 5

        self.rect.y += 3

        if self.rect.x >= 1920:
            self.kill()
        if self.rect.x <= 0:
            self.kill()
