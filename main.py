import pygame
import sys
from spritesheet import Spritesheet


#general setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 800
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_icon(pygame.image.load('../tomoni\images\icon.png'))
pygame.display.set_caption("TOMONI")
running = True



#plain surface
surf = pygame.Surface((100,100))
x, y = 100, 100
surf.fill(('blue'))


#spritesheet test
sprite_test = Spritesheet('../tomoni/images/main_sprite.png')
link_sprite = sprite_test.get_image(21, 173 , 18, 23, 2)   


while running:
    #event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #drawing the game
    display_surface.fill(('darkgray'))
    x += 0.1
    display_surface.blit(surf, (x, y))
    display_surface.blit(link_sprite, (200, 200))
    pygame.display.update()


pygame.quit()


