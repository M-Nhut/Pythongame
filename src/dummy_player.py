import os
import pygame


class DummyPlayer:
    def __init__(self, spawn_point, size=28, skin="nhanvat1"):
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

        self.on_ground = False
        self.coins = 0
        self.dead = False
        self.win = False

        # PATH assets
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_dir = os.path.join(project_root, "assets")

        self.skin = skin
        self.frame_w = 32
        self.frame_h = 32

        # Load animations
        self.anims = {
            "idle": self._load_sheet_frames(os.path.join("characters", skin, "Idle (32x32).png")),
            "run":  self._load_sheet_frames(os.path.join("characters", skin, "Run (32x32).png")),
            "jump": self._load_sheet_frames(os.path.join("characters", skin, "Jump (32x32).png")),
            "fall": self._load_sheet_frames(os.path.join("characters", skin, "Fall (32x32).png")),
            "hit":  self._load_sheet_frames(os.path.join("characters", skin, "Hit (32x32).png")),
        }

        # Nếu sheet thiếu thì vẫn có fallback vẽ hình chữ nhật
        self.anim_speed_ms = 100  # tốc độ animation
        self.state = "idle"
        self.facing_right = True

    def _load_sheet_frames(self, rel_path):
        path = os.path.join(self.assets_dir, rel_path)
        if not os.path.exists(path):
            return []

        sheet = pygame.image.load(path).convert_alpha()
        sheet_w, sheet_h = sheet.get_size()

        cols = max(1, sheet_w // self.frame_w)
        rows = max(1, sheet_h // self.frame_h)

        frames = []
        for y in range(rows):
            for x in range(cols):
                rect = pygame.Rect(x * self.frame_w, y * self.frame_h, self.frame_w, self.frame_h)
                frame = pygame.Surface((self.frame_w, self.frame_h), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), rect)
                frame = pygame.transform.scale(frame, (self.width, self.height))
                frames.append(frame)

        return frames

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.vel_x = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -self.speed
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = self.speed
            self.facing_right = True

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

        # Cập nhật trạng thái animation
        if not self.on_ground:
            self.state = "jump" if self.vel_y < 0 else "fall"
        else:
            self.state = "run" if self.vel_x != 0 else "idle"

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

    def on_death(self):
        print("Player died (fall into pit)!")
        self.dead = True

    def on_reach_goal(self):
        print("Level completed!")
        self.win = True

    def draw(self, screen, offset_x):
        x = self.rect.x - offset_x
        y = self.rect.y

        frames = self.anims.get(self.state, [])
        if frames:
            t = pygame.time.get_ticks()
            idx = (t // self.anim_speed_ms) % len(frames)
            img = frames[idx]
            if not self.facing_right:
                img = pygame.transform.flip(img, True, False)
            screen.blit(img, (x, y))
        else:
            pygame.draw.rect(screen, (0, 120, 255), pygame.Rect(x, y, self.rect.width, self.rect.height))
