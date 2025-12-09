import pygame

class Coin:
    def __init__(self, x, y, images):
        self.images = images
        self.frame = 0
        self.rect = pygame.Rect(x, y, 32, 32)
        self.collected = False

    def update(self, dt):
        self.frame = (self.frame + 0.1) % len(self.images)

    def draw(self, surf):
        if not self.collected:
            surf.blit(self.images[int(self.frame)], self.rect.topleft)

class Spike:
    def __init__(self, x, y, image):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.image = image

    def draw(self, surf):
        surf.blit(self.image, self.rect.topleft)

class BreakBlock:
    def __init__(self, x, y, image):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.image = image
        self.broken = False

    def draw(self, surf):
        if not self.broken:
            surf.blit(self.image, self.rect.topleft)

class GoalFlag:
    def __init__(self, x, y, image):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.image = image

    def draw(self, surf):
        surf.blit(self.image, self.rect.topleft)
