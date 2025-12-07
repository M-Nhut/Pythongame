import pygame
import os
from sprite import SpriteSheet
from animation import Animation

class Player:
    def __init__(self, x, y, skin="nhanvat1"):
        self.rect = pygame.Rect(x, y, 48, 48)
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 6
        self.jump_power = -15
        self.on_ground = False
        self.facing_right = True
        self.state = "idle"
        self.skin = skin

        self.anims = {}
        self.load_animations()

    def load_animations(self):
        size = (48, 48)
        folder = f"assets/characters/{self.skin}"

        # Idle sheet
        idle_path = f"{folder}/Idle (32x32).png"
        if os.path.exists(idle_path):
            idle_sheet = SpriteSheet(idle_path)
            self.anims["idle"] = Animation(idle_sheet.get_animation(0, 0, 32, 32, 10, size))

        # Run sheet
        run_path = f"{folder}/Run (32x32).png"
        if os.path.exists(run_path):
            run_sheet = SpriteSheet(run_path)
            self.anims["run"] = Animation(run_sheet.get_animation(0, 0, 32, 32, 12, size))

        # Các hành động còn lại (Jump, Fall, Hit, v.v.)
        for action in ["Jump", "Fall", "Hit", "Double Jump", "Wall Jump"]:
            action_path = f"{folder}/{action} (32x32).png"
            if os.path.exists(action_path):
                img = pygame.image.load(action_path).convert_alpha()
                img = pygame.transform.scale(img, size)
                key = action.lower().replace(" ", "_")
                self.anims[key] = Animation([img], loop=False)

        # Nếu thiếu thì dùng idle làm mặc định
        if "idle" not in self.anims:
            fallback = pygame.Surface((48, 48))
            fallback.fill((255, 0, 255))
            self.anims["idle"] = Animation([fallback])

        self.current_anim = self.anims["idle"]

    def update(self, keys):
        if self.state != "hit":
            self.vel_x = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vel_x = -self.speed
                self.facing_right = False
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vel_x = self.speed
                self.facing_right = True

            if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
                self.vel_y = self.jump_power
                self.on_ground = False

            self.vel_y += 0.8
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y
            if self.rect.bottom >= 600:
                self.rect.bottom = 600
                self.on_ground = True
                self.vel_y = 0

            if not self.on_ground:
                self.state = "jump" if self.vel_y < 0 else "fall"
            elif self.vel_x != 0:
                self.state = "run"
            else:
                self.state = "idle"

        self.current_anim = self.anims.get(self.state, self.anims["idle"])
        self.current_anim.update()

    def draw(self, screen):
        img = self.current_anim.get_image()
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        screen.blit(img, self.rect)