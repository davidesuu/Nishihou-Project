import os
import pygame
import sys
import pygamepal
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
        self.sprite_sheet = Spritesheet('images\sproutsland\Characters\Basic_Spritesheet.png')
        self.image = self.sprite_sheet.get_image(17, 16 , 14, 16, 3, black)
        self.rect = self.image.get_frect()
        self.rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.direction = pygame.math.Vector2()
        self.speed = 300

        #cooldown 
        self.can_attack = True
        self.attack_cooldown_duration = 400
        self.attack_time = 0

    

        #MASK 
        self.mask = pygame.mask.from_surface(self.image)


    def attack_timer(self):
        if not self.can_attack:
            current_time = pygame.time.get_ticks()
            if current_time - self.attack_time >= self.attack_cooldown_duration:
                self.can_attack = True


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
        if pygame.sprite.spritecollide(self, friend_sprites, False, pygame.sprite.collide_mask):
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
        if recent_key[pygame.K_SPACE] and self.can_attack:
            Sword(sword_surf, self.rect.midtop, all_sprites)
            self.can_attack = False
            self.attack_time = pygame.time.get_ticks()
        self.attack_timer()

        self.holding()

#sword class
class Sword(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
        # Disappear after a short time
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 100  # Sword will exist for 100 milliseconds

    def update(self, dt):
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
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
        self.rect = self.rect.inflate(10,10)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2()  # Direção que o player envia
        self.speed = 290  

        #Mask
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        # Move apenas se player estiver apertando E e perto
        if self.direction.length_squared() != 0:
            move_vec = self.direction.normalize() * self.speed * dt
            self.pos += move_vec
            self.rect.center = self.pos



class Camera:
    def __init__(self, width, height):
        self.offset = pygame.Vector2(0, 0)
        self.width = width
        self.height = height
        self.target = None


    def set_target(self, target):
        self.target = target

    def update(self, window_width, window_height, map_width, map_height):
        if self.target:
            self.offset.x = self.target.rect.centerx - window_width // 2
            self.offset.y = self.target.rect.centery - window_height // 2

            # Limita a câmera aos limites do mapa
            self.offset.x = max(0, min(self.offset.x, map_width - window_width))
            self.offset.y = max(0, min(self.offset.y, map_height - window_height))

    def apply(self, target):
        # retorna a posição do target ajustada pela câmera
        return target.rect.topleft - self.offset


class TransitionManager:
    def __init__(self):
        self.transition = None

    def start_transition(self, from_surface, to_surface, duration=1000, easing=None):
        easing = easing if easing else pygamepal.easeLinear
        self.transition = pygamepal.TransitionFade(
            from_surface,
            to_surface,
            duration=duration,
            easingFunction=easing
        )

    def update_draw(self, display_surface):
        if self.transition:
            if not self.transition.finished:
                self.transition.update()
                self.transition.draw(display_surface)
                return False  # transição em andamento
            else:
                self.transition = None
                return True   # transição terminou
        return True  # sem transição, continua normal


def display_score():
    font = pygame.font.Font(None, 36)
    current_time = pygame.time.get_ticks() // 10
    score_text = font.render(str(current_time), True, (255, 255, 255))
    score_rect = score_text.get_frect(topleft=(10, 10))
    display_surface.blit(score_text, score_rect)
    corner = pygame.draw.rect(display_surface, "red",score_rect.inflate(20,20), 5,10)



mapTexture = pygame.image.load(os.path.join('images','map.png'))
mapTexture = pygame.transform.scale(mapTexture, (WINDOW_WIDTH, WINDOW_HEIGHT))
transition_manager = TransitionManager()


        
#Spritesheets
sword_spritesheet = Spritesheet('images/sword_sprite.png') 

#surfaces
sword_surf = Spritesheet.get_image(sword_spritesheet,15,10,10,5,5, black)

#plain surface
surf = pygame.Surface((100,100))
x, y = 100, 100
surf.fill(('blue'))
surf2 = pygame.Surface((1120,1024))
surf2.fill(('red'))

#Creating Sprites
all_sprites = pygame.sprite.Group()
player = Player(all_sprites)
friend_sprites = pygame.sprite.Group()
friend = Friend_npc(all_sprites, friend_sprites)
bouncing_sprite = BouncingSprite(all_sprites)



MAP_WIDTH, MAP_HEIGHT = 1120, 1024  # defina o tamanho real do mapa
camera = Camera(MAP_WIDTH, MAP_HEIGHT)
camera.set_target(player)

for i in range(10):
    RandomSprite(all_sprites)



#Time event
bullet_event = pygame.event.custom_type()
pygame.time.set_timer(bullet_event, 500)


while running:
    #delta time
    dt = clock.tick()/1000  # FPS

    #event loop
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l and transition_manager.transition is None:
                transition_manager.start_transition(surf, surf2, duration=1000)
        if event.type == pygame.QUIT:
            running = False
            
  #drawing the game
    # Atualizações

    all_sprites.update(dt)
    camera.update(WINDOW_WIDTH, WINDOW_HEIGHT, MAP_WIDTH, MAP_HEIGHT)

    # Desenho
    display_surface.fill('darkgray')
    display_surface.blit(mapTexture, (-camera.offset.x, -camera.offset.y))

    # Se houver transição, ela desenha por cima e controla bloqueio de jogo
    transicao_finalizada = transition_manager.update_draw(display_surface)
    

    if transicao_finalizada:
    # SE NÃO estiver em transição, desenhe normalmente seu jogo
        display_surface.fill('darkgray')
        display_surface.blit(mapTexture, (-camera.offset.x, -camera.offset.y))
        for sprite in all_sprites:
            display_surface.blit(sprite.image, camera.apply(sprite))
    display_score()



    
    pygame.display.update()


pygame.quit()


