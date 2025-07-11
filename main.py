import pygame
import sys
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



#plain surface
surf = pygame.Surface((100,100))
x, y = 100, 100
surf.fill(('blue'))


#spritesheet test
sprite_test = Spritesheet('../tomoni/images/main_sprite.png')


sprite_aleatorio = sprite_test.get_image(1,337,18,23,2)


sprite_aleatorio_2 = sprite_test.get_image(43,75,17,22,2)
sprite_aleatorio_2_rect = sprite_aleatorio_2.get_frect()
sprite_aleatorio_2_rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
sprite_aleatorio_2_direction = pygame.math.Vector2(1,1) #vector for movement

#link sprite
link_sprite = sprite_test.get_image(21, 173 , 18, 23, 2) 
link_rect = link_sprite.get_frect()
link_rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
player_direction = pygame.math.Vector2(1,1) #vector for movement
player_speed = 300


#random position for the sprite 
position = [(randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)) for i in range(10)]
print(position)

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
    display_surface.blit(sprite_aleatorio_2, sprite_aleatorio_2_rect)
    for i in position:
        display_surface.blit(sprite_aleatorio, i)
    
    
    #sprite movement
    sprite_aleatorio_2_rect.x += sprite_aleatorio_2_direction.x * player_speed * dt
    sprite_aleatorio_2_rect.y += sprite_aleatorio_2_direction.y * player_speed * dt
    #bounce the sprite on the edges of the screen
    if sprite_aleatorio_2_rect.left <= 0 or sprite_aleatorio_2_rect.right >= WINDOW_WIDTH:
        sprite_aleatorio_2_direction.x *= -1
    if sprite_aleatorio_2_rect.top <= 0 or sprite_aleatorio_2_rect.bottom >= WINDOW_HEIGHT:
        sprite_aleatorio_2_direction.y *= -1



    #link movement
    key = pygame.key.get_pressed()
    player_direction.x = int(key[pygame.K_d]) - int(key[pygame.K_a])
    player_direction.y = int(key[pygame.K_s]) - int(key[pygame.K_w])
    player_direction = player_direction.normalize() if player_direction.length() > 0 else pygame.math.Vector2(0, 0)
    
    
    link_rect.center += player_direction * player_speed * dt
    display_surface.blit(link_sprite, link_rect)

    pygame.display.update()


pygame.quit()


