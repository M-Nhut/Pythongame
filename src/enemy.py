import pygame

class EnemyBase:
    def __init__(self, x, y, w=32, h=32):
        self.rect = pygame.Rect(x, y, w, h)
        self.dead = False
        self.frame = 0

    def update(self, dt):
        pass

    def draw(self, surf, image):
        surf.blit(image, self.rect.topleft)

class EnemyWalk(EnemyBase):
    def __init__(self, x, y, speed=1):
        super().__init__(x, y)
        self.speed = speed
        self.direction = 1

    def update(self, dt):
        if not self.dead:
            self.rect.x += self.speed * self.direction
            # đảo chiều khi va phải map boundary giả lập
            if self.rect.x < 0 or self.rect.x > 600:
                self.direction *= -1

class EnemyIdle(EnemyBase):
    def update(self, dt):
        pass  # Đứng yên

class EnemyDead(EnemyBase):
    def update(self, dt):
        if self.frame < 10:
            self.frame += 1
        else:
            self.dead = True
