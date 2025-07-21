import pygame
import sys
from spritesheet import Spritesheet
from random import randint





#Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.sprite_sheet = Spritesheet('../tomoni/images/main_sprite.png')
        self.image = self.sprite_sheet.get_image(21, 173 , 18, 23, 2)
        self.rect = self.image.get_frect()
        self.rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.direction = pygame.math.Vector2()
        self.speed = 300


    def holding(self):
        keys = pygame.key.get_pressed()
        if self.rect.colliderect(friend.rect) and keys[pygame.K_e]:
            friend.direction = self.direction
        else:
            friend.direction = pygame.math.Vector2()


    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction.length() > 0 else self.direction  #iguala a velocidade nas diagonais

    def movimento(self,dt): #separação horizontal e vertical p/ melhor colisão
        self.rect.x += self.direction.x * self.speed * dt
        self.colisao('horizontal')
        self.rect.y += self.direction.y * self.speed * dt
        self.colisao('vertical')

    def colisao(self, direcao):
        if pygame.sprite.spritecollide(self, friend_sprites, False):
            if direcao == 'horizontal': #colsisão horizontal
                if self.direction.x > 0: self.rect.right = friend.rect.left
                if self.direction.x < 0: self.rect.left = friend.rect.right
            else: #colsisão vertical
                if self.direction.y > 0: self.rect.bottom = friend.rect.top
                if self.direction.y < 0: self.rect.top = friend.rect.bottom

    def update(self, dt):

        self.input()
        self.movimento(dt)
        recent_key = pygame.key.get_just_pressed()
        if recent_key[pygame.K_SPACE]:
            print("Sword attack!")


        self.holding()

#random sprite class
class RandomSprite(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.sprite_sheet = Spritesheet('../tomoni/images/main_sprite.png')
        self.image = self.sprite_sheet.get_image(105, 340, 18, 20, 2)
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))


#bouncing sprite class
class BouncingSprite(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.sprite_sheet = Spritesheet('../tomoni/images/main_sprite.png')
        self.image = self.sprite_sheet.get_image(80,302,18,20,2)
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))
        self.direction = pygame.math.Vector2(1,1)
        self.speed = 200

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
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_frect(center= (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2()  # Direção que o player envia

        self.speed = 290  

    def update(self, dt):
        # Move apenas se player estiver apertando E e perto
        if self.direction.length_squared() != 0:
            move_vec = self.direction.normalize() * self.speed * dt
            self.pos += move_vec
            self.rect.center = self.pos

    



#general setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 800
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_icon(pygame.image.load('../tomoni\images\icon.png'))
pygame.display.set_caption("TOMONI")
running = True
clock = pygame.time.Clock()  # FPS



#plain surface
surf = pygame.Surface((100,100))
x, y = 100, 100
surf.fill(('blue'))

#player setup
all_sprites = pygame.sprite.Group()
friend_sprites = pygame.sprite.Group()
player = Player(all_sprites)
friend = Friend_npc(all_sprites, friend_sprites)

bouncing_sprite = BouncingSprite(all_sprites)

for i in range(10):
    RandomSprite(all_sprites)





#link sprite
player_direction = pygame.math.Vector2(1,1) #vector for movement
player_speed = 300



while running:
    #delta time
    dt = clock.tick()/1000  # FPS

    #event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            

    #drawing the game
    display_surface.fill(('darkgray'))
    display_surface.blit(surf, (x, y))

    



    all_sprites.update(dt)

    
    all_sprites.draw(display_surface)


    
    pygame.display.update()


pygame.quit()


