import pygame

class Spritesheet:
    def __init__(self, filename):
        self.filename = filename
        self.spritesheet = pygame.image.load(filename).convert_alpha()

    def get_image(self, x, y, width, height, scale, color):
        image = pygame.Surface((width, height)).convert_alpha()
        image.set_colorkey((color)) # Transparência preta
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        return image
