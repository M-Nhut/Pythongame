import pygame


class DummyPlayer:
    def __init__(self, spawn_point, size=28):
        self.width = size
        self.height = size

        x, y = spawn_point
        self.rect = pygame.Rect(x, y, self.width, self.height)

        # physics
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 4
        self.jump_force = -12
        self.gravity = 0.6

        # state
        self.on_ground = False
        self.coins = 0
        self.dead = False
        self.win = False

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.vel_x = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = self.speed

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = self.jump_force
            self.on_ground = False

    def apply_gravity(self):
        self.vel_y += self.gravity
        if self.vel_y > 20:
            self.vel_y = 20

    def update(self, level):
        if self.dead or self.win:
            return

        self.handle_input()
        self.apply_gravity()

        # MOVE X
        self.rect.x += self.vel_x
        self.check_collision_x(level.all_solids)

        # MOVE Y
        self.rect.y += self.vel_y
        self.check_collision_y(level.all_solids)

    def check_collision_x(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vel_x > 0:
                    self.rect.right = p.left
                elif self.vel_x < 0:
                    self.rect.left = p.right

    def check_collision_y(self, platforms):
        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vel_y > 0:
                    self.rect.bottom = p.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = p.bottom
                    self.vel_y = 0

    # 2 hàm để Level gọi
    def on_death(self):
        print("Player died!")
        self.dead = True

    def on_reach_goal(self):
        print("Level completed!")
        self.win = True

    def draw(self, screen, offset_x):
        pygame.draw.rect(
            screen, (0, 120, 255),
            pygame.Rect(self.rect.x - offset_x, self.rect.y, self.rect.width, self.rect.height)
        )
