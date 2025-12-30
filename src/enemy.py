import pygame
class EnemyBase:
    def __init__(self, x, y, w=32, h=32):
        self.rect = pygame.Rect(x, y, w, h)
        self.dead = False
        self.frame = 0
    def update(self, dt, platforms):
        pass
    def draw(self, surf, image):
        if not self.dead:
            surf.blit(image, self.rect.topleft)
class EnemyWalk(EnemyBase):
    def __init__(self, x, y, speed=1):
        super().__init__(x, y)
        self.speed = speed
        self.direction = 1  # 1: phải, -1: trái

    def update(self, dt, platforms):
        if self.dead:
            return
        # ====== DI CHUYỂN NGANG ======
        self.rect.x += self.speed * self.direction
        # ====== 1. ĐỤNG TƯỜNG → QUAY ĐẦU ======
        for p in platforms:
            if self.rect.colliderect(p):
                self.rect.x -= self.speed * self.direction
                self.direction *= -1
                return
        # ====== 2. MÉP VỰC → QUAY ĐẦU ======
        # điểm kiểm tra dưới chân phía trước
        foot_x = self.rect.centerx + self.direction * (self.rect.width // 2)
        foot_y = self.rect.bottom + 5
        foot_rect = pygame.Rect(foot_x, foot_y, 2, 2)
        on_ground = False
        for p in platforms:
            if foot_rect.colliderect(p):
                on_ground = True
                break
        if not on_ground:
            self.direction *= -1
class EnemyIdle(EnemyBase):
    def update(self, dt, platforms):
        pass  # đứng yên
class EnemyDead(EnemyBase):
    def update(self, dt, platforms):
        if self.frame < 10:
            self.frame += 1
        else:
            self.dead = True

