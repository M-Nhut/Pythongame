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

        # PATH (Pythongame/assets/...)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assets_dir = os.path.join(project_root, "assets")

        ts = self.tile_size

        # TILE IMAGES (assets/tiles)
        self.img_ground_top = self._try_load(os.path.join("tiles", "ground_top.png"), (ts, ts))
        self.img_ground_center = self._try_load(os.path.join("tiles", "ground_center.png"), (ts, ts))
        self.img_stone = self._try_load(os.path.join("tiles", "stone.png"), (ts, ts))
        self.img_pit = self._try_load(os.path.join("tiles", "pit.png"), (ts, ts))

        # BACKGROUND (assets/tiles/background_{level}.png)
        bg_name = f"background_{self.level_index}.png"
        self.img_bg = self._try_load(os.path.join("tiles", bg_name), (800, 380))

        # COIN / ENEMY / GOAL 
        self.coin_frames = [
            self._try_load(os.path.join("items", "coin1.png"), (ts, ts)),
            self._try_load(os.path.join("items", "coin2.png"), (ts, ts)),
            self._try_load(os.path.join("items", "coin3.png"), (ts, ts)),
        ]
        self.coin_frames = [f for f in self.coin_frames if f is not None]

        self.goal_img = self._try_load(os.path.join("items", "goal.png"), (ts, ts))

        # Enemy: walk1/walk2 để animate, fallback idle
        self.enemy_walk_frames = [
            self._try_load(os.path.join("enemies", "walk1.png"), (ts, ts)),
            self._try_load(os.path.join("enemies", "walk2.png"), (ts, ts)),
        ]
        self.enemy_walk_frames = [f for f in self.enemy_walk_frames if f is not None]
        self.enemy_idle_img = self._try_load(os.path.join("enemies", "idle.png"), (ts, ts))

        self._classify_ground_tiles()

    # LOAD IMAGE (từ assets/)
    def _try_load(self, rel_path, size=None):
        path = os.path.join(self.assets_dir, rel_path)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            if size:
                img = pygame.transform.scale(img, size)
            return img
        # Không in tiếng Việt để tránh UnicodeEncodeError trên Windows
        return None

    # PHÂN LOẠI GROUND TOP/CENTER
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
    # UPDATE LOGIC
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
            if c in self.coins:
                self.coins.remove(c)
                player.coins += 1

        # Chạm goal
        if self.goal_rect and player.rect.colliderect(self.goal_rect):
            player.on_reach_goal()
    # DRAW
    def draw(self, screen):
        ox = self.offset_x
        ts = self.tile_size
        t = pygame.time.get_ticks()

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
                pygame.draw.rect(screen, (0, 0, 0), r.move(-ox, 0))

        # GROUND TOP
        for r in self.ground_top:
            if self.img_ground_top:
                screen.blit(self.img_ground_top, (r.x - ox, r.y))
            else:
                pygame.draw.rect(screen, (100, 180, 60), r.move(-ox, 0))

        # GROUND CENTER
        for r in self.ground_center:
            if self.img_ground_center:
                screen.blit(self.img_ground_center, (r.x - ox, r.y))
            else:
                pygame.draw.rect(screen, (120, 70, 20), r.move(-ox, 0))

        # STONE
        for r in self.stone_list:
            if self.img_stone:
                screen.blit(self.img_stone, (r.x - ox, r.y))
            else:
                pygame.draw.rect(screen, (140, 140, 140), r.move(-ox, 0))

        # COINS (animate coin1->coin2->coin3)
        for cx, cy in self.coins:
            if self.coin_frames:
                idx = (t // 120) % len(self.coin_frames)
                img = self.coin_frames[idx]
                screen.blit(img, (int(cx - ox - ts // 2), int(cy - ts // 2)))
            else:
                pygame.draw.circle(screen, (255, 215, 0), (int(cx - ox), int(cy)), ts // 4)

        # ENEMIES (animate walk1<->walk2, fallback idle)
        for ex, ey in self.enemies:
            if self.enemy_walk_frames:
                idx = (t // 180) % len(self.enemy_walk_frames)
                img = self.enemy_walk_frames[idx]
                screen.blit(img, (int(ex - ox), int(ey)))
            elif self.enemy_idle_img:
                screen.blit(self.enemy_idle_img, (int(ex - ox), int(ey)))
            else:
                pygame.draw.rect(screen, (200, 40, 40), pygame.Rect(ex - ox, ey, ts, ts))

        # GOAL
        if self.goal_rect:
            if self.goal_img:
                screen.blit(self.goal_img, (int(self.goal_rect.x - ox), int(self.goal_rect.y)))
            else:
                pygame.draw.rect(screen, (0, 255, 0), self.goal_rect.move(-ox, 0), 3)

    # CAMERA
    def update_camera(self, player, screen_width):
        px = player.rect.centerx
        self.offset_x = max(0, px - screen_width // 2)
