import os
import pygame
import sys
import pygamepal
import math
from spritesheet import Spritesheet
from random import randint

#general setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 800
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_icon(pygame.image.load('../tomoni\images\icon.png'))
pygame.display.set_caption("TOMONI")
running = True
clock = pygame.time.Clock()  # FPS

#Colors
black = (0,0,0)
green = '#108058'



#Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.sprite_sheet = Spritesheet('images\player_spritesheet.png')
        self.image = self.sprite_sheet.get_image(7, 5 , 23, 46, 1, black)
        self.rect = self.image.get_frect()
        self.rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.direction = pygame.math.Vector2() 
        self.speed = 300
        self.current_speed = 0

        #logica da vida
        self.lives = 7
        self.invicible = False
        self.invicible_time = 2000
        self.last_hit_time = 0
        
        #efeito piscando apos ser atingido
        self.frame_count = 0

        #cooldown 
        self.can_attack = True
        self.shoot_cooldown = 200   #mileseconds between the knives
        self.last_shot_time = 0

        #logica do raio da hitbox
        self.hitbox_radius = 4
        self.hitbox_image = pygame.image.load("images/hitbox.png").convert_alpha()
        self.hitbox_offset = pygame.Vector2(self.hitbox_image.get_width() // 2, self.hitbox_image.get_height() // 2)

        #velocidade da sakuya quando aperta shift
        self.slow_speed = 150


        #MASK 
        self.mask = pygame.mask.from_surface(self.image)



    def attack_timer(self):
        if not self.can_attack:
            current_time = pygame.time.get_ticks()
            if current_time - self.attack_time >= self.attack_cooldown_duration:
                self.can_attack = True


    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction.length() > 0 else self.direction  #iguala a velocidade nas diagonais

        if keys[pygame.K_LSHIFT]:
            self.current_speed = self.slow_speed
        else:
            self.current_speed = self.speed

    def movimento(self,dt):
        self.rect.x += self.direction.x * self.current_speed * dt
        self.rect.y += self.direction.y * self.current_speed * dt

    def draw_hitbox(self, surface):
        x = self.rect.centerx - self.hitbox_offset.x
        y = self.rect.centery - self.hitbox_offset.y
        surface.blit(self.hitbox_image, (x, y))



    def update(self, dt):

        self.input()
        self.movimento(dt)
        

        current_time = pygame.time.get_ticks()
        recent_key = pygame.key.get_pressed()
        if recent_key[pygame.K_SPACE]:
            if current_time - self.last_shot_time >= self.shoot_cooldown:
                Bullet(knives_surf, self.rect.midtop, all_sprites)
                self.last_shot_time = current_time
        
        if self.invicible:
            #efeito piscando
            self.frame_count += 1
            if self.frame_count%10 < 5:
                self.image.set_alpha(0)
            else:
                self.image.set_alpha(255)
            #tempo do iframe apos ser atingido
            now = pygame.time.get_ticks()
            if now - self.last_hit_time >= self.invicible_time:
                self.invicible = False



class Danmaku(pygame.sprite.Sprite):
    angle_global = 0  # variável de classe para controlar o ângulo da espiral

    def __init__(self,surf, pos, *groups):
        super().__init__(*groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        # Define o ângulo da bala com base em uma variável global crescente
        angle_rad = math.radians(Danmaku.angle_global)
        self.direction = pygame.Vector2(math.cos(angle_rad), math.sin(angle_rad))
        self.speed = 200
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 6000
        # Aumenta o ângulo global para o próximo projétil
        Danmaku.angle_global = (Danmaku.angle_global + 10) % 360

        #mask
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        move = self.direction * self.speed * dt
        self.rect.centerx += move.x
        self.rect.centery += move.y
        
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()

    
class Boss_fight(pygame.sprite.Sprite):
    def __init__(self, surf, groups, boss_sprites):
        super().__init__(groups,boss_sprites)
        self.image = surf
        self.rect = self.image.get_frect(center = (100,100))
        self.pos = pygame.Vector2(1,0)

        self.mask = pygame.mask.from_surface(self.image)

        self.cooldown = 2000
        self.speed = 500
    def update(self,dt):
        self.rect.x += self.pos.x * self.speed * dt
        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH 
            self.pos.x *= -1
        elif self.rect.left < 0:
            self.rect.left = 0
            self.pos.x *= -1

#Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
        self.speed = 300

        # Disappear after a short time
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 100  # Sword will exist for 100 milliseconds

    def update(self, dt):
        self.rect.y -= self.speed * dt
        if self.rect.bottom < 0:
            self.kill() 
    
#random sprite class
class RandomSprite(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.sprite_sheet = Spritesheet('../tomoni/images/main_sprite.png')
        self.image = self.sprite_sheet.get_image(105, 340, 18, 20, 2,black)
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))


#bouncing sprite class
class BouncingSprite(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.sprite_sheet = Spritesheet('../tomoni/images/main_sprite.png')
        self.image = self.sprite_sheet.get_image(80,302,18,20,2,black)
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))
        self.direction = pygame.math.Vector2(1,1)
        self.speed = 200
        self.size = self.image.get_size()

    def update(self, dt):
        self.rect.x += self.direction.x * self.speed * dt
        self.rect.y += self.direction.y * self.speed * dt
        #bounce the sprite on the edges of the screen
        if self.rect.left <= 0 or self.rect.right >= WINDOW_WIDTH:
            self.direction.x *= -1
        if self.rect.top <= 0 or self.rect.bottom >= WINDOW_HEIGHT:
            self.direction.y *= -1


# NPC
class Friend_npc(pygame.sprite.Sprite):
    def __init__(self, groups, friend_groups):
        super().__init__(groups, friend_groups)
        self.sprite_sheet = Spritesheet('images/Npc_Spritesheet.png')
        self.image = self.sprite_sheet.get_image(16,24,16,24,2,green)
        self.rect = self.image.get_frect(center= (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2()  # Direção que o player envia
        self.speed = 290  

        #Mask
        self.mask = pygame.mask.from_surface(self.image)
        self.mask_surf = self.mask.to_surface()
        self.image = self.mask_surf

    def update(self, dt):
        # Move apenas se player estiver apertando E e perto
        if self.direction.length_squared() != 0:
            move_vec = self.direction.normalize() * self.speed * dt
            self.pos += move_vec
            self.rect.center = self.pos



def display_score():
    font = pygame.font.Font(None, 36)
    current_time = pygame.time.get_ticks() // 10
    score_text = font.render(str(current_time), True, (255, 255, 255))
    score_rect = score_text.get_frect(topleft=(10, 10))
    display_surface.blit(score_text, score_rect)
    corner = pygame.draw.rect(display_surface, "red",score_rect.inflate(20,20), 5,10)


def collisions():
    if player.invicible:
        return 
    

    player_center = pygame.Vector2(player.rect.center)
    for danmaku in danmaku_sprites:
        danmaku_center = pygame.Vector2(danmaku.rect.center)
        distance = player_center.distance_to(danmaku_center)
        if distance < player.hitbox_radius:
                print("Colidiu!!")
                player.lives -= 1
                player.invicible = True
                player.last_hit_time = pygame.time.get_ticks()
                player.frame_count = 0
                player.rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT - 50)
    
                if player.lives <= 0:
                    player.kill()
#----------------------Player colisions------------------------------------------------------------------------------


    





mapTexture = pygame.image.load(os.path.join('images','map.png'))
mapTexture = pygame.transform.scale(mapTexture, (WINDOW_WIDTH, WINDOW_HEIGHT))



        
#Spritesheets
knives_spritesheet = Spritesheet('images/knives.png') 
danmaku_spritesheet = Spritesheet('images/danmaku_spritesheet.png')
cirno_spritesheet = Spritesheet('images/cirno_spritesheet.png')

#surfaces #14,46
knives_surf = knives_spritesheet.get_image(59,1,46,31,1, black)
danmaku_surf = danmaku_spritesheet.get_image(322,73,16,16,1,black)
cirno_surf = cirno_spritesheet.get_image(180,166,41,53,1,black)

#plain surface
surf = pygame.Surface((100,100))
x, y = 100, 100
surf.fill(('blue'))
surf2 = pygame.Surface((1120,1024))
surf2.fill(('red'))

#Creating Sprites
all_sprites = pygame.sprite.Group()
player = Player(all_sprites)
danmaku_sprites = pygame.sprite.Group()
friend_sprites = pygame.sprite.Group()
friend = Friend_npc(all_sprites, friend_sprites)
boss_sprites = pygame.sprite.Group()
cirno = Boss_fight(cirno_surf,all_sprites,boss_sprites)
bouncing_sprite = BouncingSprite(all_sprites)






for i in range(10):
    RandomSprite(all_sprites)



#Time event
danmaku_event = pygame.event.custom_type()
pygame.time.set_timer(danmaku_event, 100) #Isso vai definiro quao suave vai ser o padrao

while running:
    #delta time
    dt = clock.tick()/1000  # FPS

    #Teclas pressionadas
    keys = pygame.key.get_pressed()

    #event loop
    for event in pygame.event.get():
        if event.type == danmaku_event:
            center_pos = cirno.rect.center
            for i in range(2):  # Quantidade de danmaku no ataque
                center_pos = cirno.rect.center
                Danmaku(danmaku_surf, center_pos, (all_sprites,danmaku_sprites))

        if event.type == pygame.QUIT:
            running = False

            
  #drawing the game
    # Atualizações

    all_sprites.update(dt)


    display_surface.fill('darkgray')
    display_surface.blit(mapTexture, (0,0))
    for sprite in all_sprites:
        display_surface.blit(sprite.image, sprite.rect)
    if keys[pygame.K_LSHIFT]:
        player.draw_hitbox(display_surface)
       
    display_score()
    collisions()


    
    pygame.display.update()


pygame.quit()


