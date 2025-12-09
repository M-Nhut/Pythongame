import os
import pygame

class Level:
    def __init__(self, parsed_data, level_index):
        self.level_index = level_index
        self.tile_size = parsed_data["tile_size"]

        # Danh sách các thành phần của map
        self.platforms = parsed_data.get("platform_list", [])
        self.stone_list = parsed_data.get("stone_list", [])
        self.pits = parsed_data.get("pit_list", [])
        self.coins = parsed_data.get("coin_list", [])
        self.enemies = parsed_data.get("enemy_list", [])
        self.spawn_point = parsed_data.get("spawn_point")
        self.goal_rect = parsed_data.get("goal_rect")
        self.raw_tiles = parsed_data.get("raw_tiles", [])

        self.all_solids = self.platforms + self.stone_list

        self.ground_top = []
        self.ground_center = []

        self.offset_x = 0

        # PATH AN TOÀN
        base_dir = os.path.dirname(__file__)
        assets_dir = os.path.join(base_dir, "assets")

        def try_load(name, size=None):
            path = os.path.join(assets_dir, name)
            try:
                img = pygame.image.load(path).convert_alpha()
                if size:
                    img = pygame.transform.scale(img, size)
                return img
            except:
                print(f"[Warning] Không tìm thấy: {path}")
                return None

        ts = self.tile_size

        # TILE SPRITES
        self.img_ground_top = try_load("ground_top.png", (ts, ts))
        self.img_ground_center = try_load("ground_center.png", (ts, ts))
        self.img_stone = try_load("stone.png", (ts, ts))
        self.img_pit = try_load("pit.png", (ts, ts))

        # BACKGROUND THEO LEVEL
        bg_name = f"background_{self.level_index}.png"
        self.img_bg = try_load(bg_name, (800, 380))

        # Phân loại mặt đất
        self._classify_ground_tiles()

    # Phân tách ground
    def _classify_ground_tiles(self):
        ts = self.tile_size
        platform_positions = {(r.x, r.y) for r in self.platforms}

        self.ground_top = []
        self.ground_center = []

        for r in self.platforms:
            above_pos = (r.x, r.y - ts)
            if above_pos in platform_positions:
                self.ground_center.append(r)
            else:
                self.ground_top.append(r)

    # UPDATE
    def update(self, player):
        # 1. Player rơi vào hố
        for pit in self.pits:
            if player.rect.colliderect(pit):
                player.on_death()
                return

        # 2. Coin pickup
        collected = []
        for cx, cy in self.coins:
            coin_rect = pygame.Rect(
                cx - self.tile_size // 4,
                cy - self.tile_size // 4,
                self.tile_size // 2,
                self.tile_size // 2
            )
            if player.rect.colliderect(coin_rect):
                collected.append((cx, cy))

        for c in collected:
            if c in self.coins:
                self.coins.remove(c)
                player.coins += 1

        # 3. Goal
        if self.goal_rect and player.rect.colliderect(self.goal_rect):
            player.on_reach_goal()

    # DRAW
    def draw(self, screen):
        ox = self.offset_x
        ts = self.tile_size

        # BACKGROUND
        if self.img_bg:
            screen.blit(self.img_bg, (0, 0))
        else:
            screen.fill((120, 190, 255))

        # PITS
        for r in self.pits:
            if self.img_pit:
                screen.blit(self.img_pit, (r.x - ox, r.y))
            else:
                pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(r.x - ox, r.y, r.width, r.height))

        # GROUND TOP
        for r in self.ground_top:
            if self.img_ground_top:
                screen.blit(self.img_ground_top, (r.x - ox, r.y))
            else:
                pygame.draw.rect(screen, (100, 180, 60), pygame.Rect(r.x - ox, r.y, r.width, r.height))

        # GROUND CENTER
        for r in self.ground_center:
            if self.img_ground_center:
                screen.blit(self.img_ground_center, (r.x - ox, r.y))
            else:
                pygame.draw.rect(screen, (120, 70, 20), pygame.Rect(r.x - ox, r.y, r.width, r.height))

        # STONE
        for r in self.stone_list:
            if self.img_stone:
                screen.blit(self.img_stone, (r.x - ox, r.y))
            else:
                pygame.draw.rect(screen, (140, 140, 140), pygame.Rect(r.x - ox, r.y, r.width, r.height))

        # COINS
        for cx, cy in self.coins:
            pygame.draw.circle(screen, (255, 215, 0), (int(cx - ox), int(cy)), ts // 4)

        # ENEMIES
        for ex, ey in self.enemies:
            pygame.draw.rect(screen, (200, 40, 40), pygame.Rect(ex - ox, ey, ts, ts))

        # SPAWN
        if self.spawn_point:
            sx, sy = self.spawn_point
            pygame.draw.rect(screen, (40, 200, 60), pygame.Rect(sx - ox, sy, ts, ts))

        # GOAL
        if self.goal_rect:
            pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(self.goal_rect.x - ox, self.goal_rect.y, self.goal_rect.width, self.goal_rect.height), 3)

    # CAMERA
    def update_camera(self, player, screen_width):
        px = player.rect.centerx
        self.offset_x = max(0, px - screen_width // 2)