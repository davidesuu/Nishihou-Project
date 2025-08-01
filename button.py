import pygame

class Button():
    def __init__(self,x,y,image,scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def drawn(self,surface,pos):
        action = False

        #pegando a posicao do mouse na tela
        surface.blit(self.image, (self.rect.x, self.rect.y))

        mouse_click = pygame.mouse.get_pressed() 
        if self.rect.collidepoint(pos):
            if mouse_click[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True

        if mouse_click[0] == 0:
            self.clicked = False
        
        return action

