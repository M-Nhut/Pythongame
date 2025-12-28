import os
import pygame


class Level:
    def __init__(self, parsed_data, level_index):
        self.level_index = level_index
        self.tile_size = parsed_data["tile_size"]

        # DATA TỪ MAP
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

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_dir = os.path.join(project_root, "assets")

        ts = self.tile_size

        # -----------------------------
        # LOAD TILE IMAGES
        # -----------------------------
        self.img_ground_top = self._try_load("ground_top.png", (ts, ts))
        self.img_ground_center = self._try_load("ground_center.png", (ts, ts))
        self.img_stone = self._try_load("stone.png", (ts, ts))
        self.img_pit = self._try_load("pit.png", (ts, ts))

        # -----------------------------
        # LOAD BACKGROUND
        # -----------------------------
        bg_name = f"background_{self.level_index}.png"
        self.img_bg = self._try_load(bg_name, (800, 380))

        # -----------------------------
        # PHÂN LOẠI GROUND
        # -----------------------------
        self._classify_ground_tiles()

    # LOAD IMAGE 
    def _try_load(self, name, size=None):
        candidates = [
            os.path.join(self.assets_dir, "tiles", name),
            os.path.join(self.assets_dir, name),
        ]

        for path in candidates:
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                if size:
                    img = pygame.transform.scale(img, size)
                return img

        print(f"[Warning] Missing asset: {name}")
        return None

    # PHÂN LOẠI GROUND TOP / CENTER

    def _classify_ground_tiles(self):
        ts = self.tile_size
        platform_positions = {(r.x, r.y) for r in self.platforms}

        self.ground_top = []
        self.ground_center = []

        for r in self.platforms:
            above = (r.x, r.y - ts)
            if above in platform_positions:
                self.ground_center.append(r)
            else:
                self.ground_top.append(r)

    def update(self, player):
        # Player rơi xuống hố
        for pit in self.pits:
            if player.rect.colliderect(pit):
                player.on_death()
                return

        # Ăn coin
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
            self.coins.remove(c)
            player.coins += 1

        # Chạm goal
        if self.goal_rect and player.rect.colliderect(self.goal_rect):
            player.on_reach_goal()

  
    def draw(self, screen):
        ox = self.offset_x
        ts = self.tile_size

        # Background
        if self.img_bg:
            screen.blit(self.img_bg, (0, 0))
        else:
            screen.fill((120, 190, 255))

        # Pits
        for r in self.pits:
            if self.img_pit:
                screen.blit(self.img_pit, (r.x - ox, r.y))
            else:
                pygame.draw.rect(screen, (0, 0, 0), r.move(-ox, 0))

        # Ground top
        for r in self.ground_top:
            if self.img_ground_top:
                screen.blit(self.img_ground_top, (r.x - ox, r.y))
            else:
                pygame.draw.rect(screen, (100, 180, 60), r.move(-ox, 0))

        # Ground center
        for r in self.ground_center:
            if self.img_ground_center:
                screen.blit(self.img_ground_center, (r.x - ox, r.y))
            else:
                pygame.draw.rect(screen, (120, 70, 20), r.move(-ox, 0))

        # Stone
        for r in self.stone_list:
            if self.img_stone:
                screen.blit(self.img_stone, (r.x - ox, r.y))
            else:
                pygame.draw.rect(screen, (140, 140, 140), r.move(-ox, 0))

        # Coins
        for cx, cy in self.coins:
            pygame.draw.circle(
                screen, (255, 215, 0),
                (int(cx - ox), int(cy)),
                ts // 4
            )

        # Enemies (placeholder)
        for ex, ey in self.enemies:
            pygame.draw.rect(
                screen, (200, 40, 40),
                pygame.Rect(ex - ox, ey, ts, ts)
            )

        # Spawn
        if self.spawn_point:
            sx, sy = self.spawn_point
            pygame.draw.rect(
                screen, (40, 200, 60),
                pygame.Rect(sx - ox, sy, ts, ts)
            )

        # Goal
        if self.goal_rect:
            pygame.draw.rect(
                screen, (0, 255, 0),
                pygame.Rect(
                    self.goal_rect.x - ox,
                    self.goal_rect.y,
                    self.goal_rect.width,
                    self.goal_rect.height
                ),
                3
            )

    # CAMERA
    def update_camera(self, player, screen_width):
        px = player.rect.centerx
        self.offset_x = max(0, px - screen_width // 2)
