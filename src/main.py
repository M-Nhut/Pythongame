import pygame
import sys
import os
import json
import traceback
from pathlib import Path

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 380
FPS = 60

# Font chữ
FONT_BTN = pygame.font.SysFont("Berlin Sans FB Demi", 22)
if not pygame.font.get_fonts():
    FONT_BTN = pygame.font.SysFont("arial", 22, bold=True)
    
FONT_TITLE = pygame.font.SysFont("Berlin Sans FB Demi", 60)
if not pygame.font.get_fonts():
    FONT_TITLE = pygame.font.SysFont("arial", 60, bold=True)

# --- Hàm tìm đường dẫn ---
def get_paths():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    assets_dir = os.path.join(project_root, "assets")
    
    return {
        "root": project_root,
        "assets": assets_dir,
        "tiles": os.path.join(assets_dir, "tiles"),
        "items": os.path.join(assets_dir, "items"),
        "enemies": os.path.join(assets_dir, "enemies"),
        "characters": os.path.join(assets_dir, "characters"),
        "sounds": os.path.join(assets_dir, "sounds"),
        "ui": os.path.join(assets_dir, "ui"),
        "shop_file": os.path.join(project_root, "shop_state.json")
    }

PATHS = get_paths()

# --- QUẢN LÝ SHOP ---
class ShopManager:
    def __init__(self, save_file):
        self.save_file = Path(save_file)
        self.all_skins = ["nhanvat1", "nhanvat2", "nhanvat3", "nhanvat4"]
        self.default_state = {
            "coins": 0,
            "max_level": 1,
            "owned_skins": ["nhanvat1"],
            "equipped_skin": "nhanvat1"
        }
        self.state = self.default_state.copy()
        self.load()

    def load(self):
        if self.save_file.exists():
            try:
                with open(self.save_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for key in self.default_state:
                        if key not in data: data[key] = self.default_state[key]
                    self.state = data
            except: pass
        else:
            self.save()

    def save(self):
        try:
            with open(self.save_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f)
        except: pass

    def add_coin(self, amount):
        self.state["coins"] += amount
        self.save()

    def unlock_next_level(self, current_level_idx):
        if current_level_idx == self.state["max_level"]:
            self.state["max_level"] += 1
            self.save()

    def buy_skin(self, skin_id):
        price = 50 
        if skin_id in self.state["owned_skins"]: return
        if self.state["coins"] >= price:
            self.state["coins"] -= price
            self.state["owned_skins"].append(skin_id)
            self.save()

    def equip_skin(self, skin_id):
        if skin_id in self.state["owned_skins"]:
            self.state["equipped_skin"] = skin_id
            self.save()

# --- QUẢN LÝ ÂM THANH (ĐÃ NÂNG CẤP ĐỂ TỰ TÌM ĐUÔI FILE) ---
class SoundManager:
    def __init__(self):
        self.sounds = {}
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
            self._load("coin", "coin.wav")
            self._load("hit", "hit.wav")
            self._load("jump", "jump.wav")
            self._load("gameover", "gameover.wav")
        except: pass

    def _load(self, name, filename):
        path = os.path.join(PATHS["sounds"], filename)
        if os.path.exists(path):
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
                if name == "coin": self.sounds[name].set_volume(0.2)
            except: pass

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    # --- HÀM PHÁT NHẠC THÔNG MINH (MỚI) ---
    def play_bgm(self, filename_base):
        extensions = [".mp3", ".wav", ".ogg"]
        found_path = None
        
        # Nếu filename đã có đuôi thì dùng luôn
        if "." in filename_base:
            p = os.path.join(PATHS["sounds"], filename_base)
            if os.path.exists(p): found_path = p
        else:
            # Nếu chưa có đuôi, thử từng loại
            for ext in extensions:
                p = os.path.join(PATHS["sounds"], filename_base + ext)
                if os.path.exists(p):
                    found_path = p
                    break
        
        if found_path:
            try:
                pygame.mixer.music.load(found_path)
                pygame.mixer.music.set_volume(0.2)
                pygame.mixer.music.play(-1) # Lặp vô tận
            except Exception as e:
                print(f"Lỗi phát nhạc {found_path}: {e}")
        else:
            # Không tìm thấy nhạc thì thôi, không báo lỗi làm dừng game
            print(f"Chưa có file nhạc cho: {filename_base}")
    
    def stop_bgm(self):
        pygame.mixer.music.stop()

SFX = SoundManager()

# --- NÚT BẤM ---
class Button:
    def __init__(self, rect, text, callback, 
                 img=None, img_hover=None,
                 bg_color=(70, 130, 180), hover_color=(100, 160, 210), 
                 border_radius=15, text_color=(255, 255, 255), is_locked=False):
        self.rect = rect
        self.text = text
        self.callback = callback
        
        self.img = img
        self.img_hover = img_hover if img_hover else img
        self.use_image = img is not None
        
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.border_radius = border_radius
        self.text_color = text_color
        self.hover = False
        self.is_locked = is_locked

    def draw(self, surf):
        if self.is_locked:
            pygame.draw.rect(surf, (60, 60, 70), self.rect, border_radius=self.border_radius)
            pygame.draw.rect(surf, (100, 100, 100), self.rect, width=2, border_radius=self.border_radius)
            cx, cy = self.rect.centerx, self.rect.centery
            pygame.draw.rect(surf, (150, 150, 150), (cx-10, cy-5, 20, 15)) 
            pygame.draw.arc(surf, (150, 150, 150), (cx-8, cy-15, 16, 15), 0, 3.14, 2)
            return

        if self.use_image:
            current_img = self.img_hover if self.hover else self.img
            if current_img:
                surf.blit(current_img, self.rect)
            txt_col = (204, 30, 30) if self.use_image else self.text_color
        else:
            color = self.hover_color if self.hover else self.bg_color
            pygame.draw.rect(surf, (0,0,0), (self.rect.x+2, self.rect.y+3, self.rect.w, self.rect.h), border_radius=self.border_radius)
            pygame.draw.rect(surf, color, self.rect, border_radius=self.border_radius)
            pygame.draw.rect(surf, (255, 255, 255), self.rect, width=2, border_radius=self.border_radius)
            txt_col = self.text_color
        
        current_font = FONT_BTN
        if self.text == "||":
            current_font = pygame.font.SysFont("arial", 24, bold=True)
        elif not self.use_image:
            current_font = pygame.font.SysFont("Berlin Sans FB Demi", 32)

        txt_surf = current_font.render(self.text, True, txt_col)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surf.blit(txt_surf, txt_rect)

    def handle_event(self, event):
        if self.is_locked: return
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback: self.callback()

# --- SPRITESHEET HELPER ---
class SpriteSheet:
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame, width, height, scale, color=(0, 0, 0)):
        image = pygame.Surface((width, height)).convert_alpha()
        image.fill((0,0,0,0))
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        image.set_colorkey(color)
        return image

def draw_heart(surface, x, y, color):
    pygame.draw.circle(surface, (50, 0, 0), (x - 5, y - 4), 8)
    pygame.draw.circle(surface, (50, 0, 0), (x + 5, y - 4), 8)
    points_shadow = [(x - 12, y - 1), (x + 12, y - 1), (x, y + 13)]
    pygame.draw.polygon(surface, (50, 0, 0), points_shadow)

    pygame.draw.circle(surface, color, (x - 5, y - 5), 7)
    pygame.draw.circle(surface, color, (x + 5, y - 5), 7)
    points = [(x - 12, y - 2), (x + 12, y - 2), (x, y + 12)]
    pygame.draw.polygon(surface, color, points)
    pygame.draw.circle(surface, (255, 200, 200), (x - 7, y - 7), 2)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, img_list):
        super().__init__()
        self.image = img_list[0] if img_list else pygame.Surface((32,32))
        self.rect = self.image.get_rect(topleft=(x,y))
        self.speed = 1
        self.direction = 1 
        self.img_list = img_list
        self.frame_index = 0
        self.animation_speed = 0.1

    def update(self, platforms):
        self.rect.x += self.speed * self.direction
        if self.img_list:
            self.frame_index = (self.frame_index + self.animation_speed) % len(self.img_list)
            self.image = self.img_list[int(self.frame_index)]
            if self.direction == -1:
                self.image = pygame.transform.flip(self.img_list[int(self.frame_index)], True, False)

        turn_around = False
        for p in platforms:
            if self.rect.colliderect(p): turn_around = True
        
        look_ahead_x = self.rect.right if self.direction == 1 else self.rect.left - 5
        look_ahead = pygame.Rect(look_ahead_x, self.rect.bottom + 5, 5, 5)
        on_ground = False
        for p in platforms:
            if look_ahead.colliderect(p):
                on_ground = True
                break
        if not on_ground: turn_around = True

        if turn_around:
            self.rect.x -= self.speed * self.direction 
            self.direction *= -1

    def draw(self, screen, offset_x):
        screen.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Player:
    def __init__(self, spawn, skin_name, shop):
        self.rect = pygame.Rect(spawn[0], spawn[1], 20, 30)
        self.spawn = spawn
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.lives = 6
        self.dead = False
        self.win = False
        self.invincible = False
        self.invincible_timer = 0
        self.shop = shop
        
        self.animations = {"idle": [], "run": []}
        self.frame_index = 0
        self.action = "idle"
        self.load_skin(skin_name)

    def load_skin(self, skin_name):
        folder = os.path.join(PATHS["characters"], skin_name)
        def load_sheet(action, count):
            path = os.path.join(folder, f"{action} (32x32).png")
            frames = []
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    sheet = SpriteSheet(img)
                    for i in range(count):
                        frames.append(sheet.get_image(i, 32, 32, 1.5))
                except: pass
            return frames

        self.animations["idle"] = load_sheet("Idle", 11)
        self.animations["run"] = load_sheet("Run", 12)
        
        if not self.animations["idle"]:
            surf = pygame.Surface((48, 48))
            surf.fill((0, 0, 255))
            self.animations["idle"] = [surf]
            self.animations["run"] = [surf]

    def update(self, level_data):
        if self.dead or self.win: return
        if self.invincible:
            if pygame.time.get_ticks() - self.invincible_timer > 2000:
                self.invincible = False

        keys = pygame.key.get_pressed()
        self.vel_x = 0
        
        # --- HỖ TRỢ CẢ MŨI TÊN VÀ WASD ---
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: 
            self.vel_x = -4
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: 
            self.vel_x = 4
            self.facing_right = True
        
        # Nhảy bằng SPACE hoặc W
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = -13
            self.on_ground = False
            SFX.play("jump")

        new_action = "run" if self.vel_x != 0 else "idle"
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
        
        self.frame_index = (self.frame_index + 0.2) % len(self.animations[self.action])
        self.vel_y = min(self.vel_y + 0.6, 20)

        # Collision X
        self.rect.x += self.vel_x
        
        # --- CHẶN DI CHUYỂN RA KHỎI MÀN HÌNH ---
        map_width = level_data["width"] * level_data["tile_size"]
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > map_width: self.rect.right = map_width
        
        solids = level_data["platforms"] + level_data["stones"]
        for p in solids:
            if self.rect.colliderect(p):
                if self.vel_x > 0: self.rect.right = p.left
                elif self.vel_x < 0: self.rect.left = p.right
        
        # Collision Y
        self.rect.y += self.vel_y
        self.on_ground = False
        for p in solids:
            if self.rect.colliderect(p):
                if self.vel_y > 0:
                    self.rect.bottom = p.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = p.bottom
                    self.vel_y = 0
        
        if self.rect.y > 450:
            self.take_damage(force_respawn=True)

    def take_damage(self, force_respawn=False):
        if self.invincible and not force_respawn: return
        self.lives -= 1
        
        if force_respawn: SFX.play("hit")
        else: SFX.play("hit")

        if self.lives > 0:
            if force_respawn:
                self.rect.topleft = self.spawn
                self.vel_y = 0
            else:
                self.vel_y = -8
                self.invincible = True
                self.invincible_timer = pygame.time.get_ticks()
        else:
            SFX.play("gameover")
            self.dead = True

    def add_coin(self):
        self.shop.add_coin(1)
        SFX.play("coin")

    def draw(self, screen, offset_x):
        if self.invincible and (pygame.time.get_ticks() // 100) % 2 == 0: return
        img = self.animations[self.action][int(self.frame_index)]
        if not self.facing_right: img = pygame.transform.flip(img, True, False)
        screen.blit(img, (self.rect.x - offset_x - 14, self.rect.y - 18))

class Level:
    def __init__(self, data, level_index):
        self.data = data
        self.ts = data["tile_size"]
        self.offset_x = 0
        self.level_index = level_index
        self.imgs = {}
        
        def ld(k, f, n, s=None):
            p = os.path.join(f, n)
            if os.path.exists(p):
                i = pygame.image.load(p).convert_alpha()
                if s: i = pygame.transform.scale(i, s)
                self.imgs[k] = i
        
        ld("bg", PATHS["tiles"], f"background_{level_index}.png", (800, 380))
        ld("top", PATHS["tiles"], "ground_top.png", (self.ts, self.ts))
        ld("cen", PATHS["tiles"], "ground_center.png", (self.ts, self.ts))
        ld("stone", PATHS["tiles"], "stone.png", (self.ts, self.ts))
        ld("pit", PATHS["tiles"], "pit.png", (self.ts, self.ts))
        ld("goal", PATHS["items"], "goal.png", (40, 40))

        self.coin_imgs = []
        for i in range(1, 4):
            p = os.path.join(PATHS["items"], f"coin{i}.png")
            if os.path.exists(p):
                self.coin_imgs.append(pygame.transform.scale(pygame.image.load(p).convert_alpha(), (32, 32)))
        self.coin_frame = 0

        ep = os.path.join(PATHS["enemies"], "walk1.png")
        self.enemy_imgs = []
        if os.path.exists(ep):
            self.enemy_imgs = [pygame.transform.scale(pygame.image.load(ep).convert_alpha(), (32, 32))]

        self.ground_top = []
        self.ground_center = []
        plat_set = {(r.x, r.y) for r in self.data["platforms"]}
        for r in self.data["platforms"]:
            if (r.x, r.y - self.ts) in plat_set: self.ground_center.append(r)
            else: self.ground_top.append(r)
        
        self.active_enemies = pygame.sprite.Group()
        for ex, ey in self.data["enemies"]:
            self.active_enemies.add(Enemy(ex, ey, self.enemy_imgs))

    def update(self, player):
        self.coin_frame = (self.coin_frame + 0.15) % len(self.coin_imgs) if self.coin_imgs else 0

        for pit in self.data["pits"]:
            if player.rect.colliderect(pit.inflate(-10,-10)):
                player.take_damage(force_respawn=True)
        
        collected = []
        for c in self.data["coins"]:
            cx, cy = c
            if player.rect.colliderect(pygame.Rect(cx-10, cy-10, 20, 20)):
                collected.append(c)
        for c in collected:
            if c in self.data["coins"]:
                self.data["coins"].remove(c)
                player.add_coin()

        solids = self.data["platforms"] + self.data["stones"]
        for enemy in self.active_enemies:
            enemy.update(solids)
            if player.rect.colliderect(enemy.rect.inflate(-6, -6)):
                if player.vel_y > 0 and player.rect.bottom < enemy.rect.centery + 15:
                    enemy.kill() 
                    player.vel_y = -8
                    SFX.play("jump") 
                else:
                    player.take_damage()

        if self.data["goal"].colliderect(player.rect):
            player.win = True

    def draw(self, screen):
        ox = self.offset_x
        if self.imgs.get("bg"): screen.blit(self.imgs["bg"], (0,0))
        else: screen.fill((135, 206, 235))

        def dr(k, r, c):
            if self.imgs.get(k): screen.blit(self.imgs[k], (r.x-ox, r.y))
            else: pygame.draw.rect(screen, c, (r.x-ox, r.y, r.w, r.h))

        for r in self.data["pits"]: dr("pit", r, (50,0,0))
        for r in self.ground_center: dr("cen", r, (139,69,19))
        for r in self.ground_top: dr("top", r, (34,139,34))
        for r in self.data["stones"]: dr("stone", r, (128,128,128))
        
        cimg = self.coin_imgs[int(self.coin_frame)] if self.coin_imgs else None
        for cx, cy in self.data["coins"]:
            if cimg: screen.blit(cimg, cimg.get_rect(center=(cx-ox, cy)))
            else: pygame.draw.circle(screen, (255,215,0), (int(cx-ox), int(cy)), 10)
        
        for e in self.active_enemies: e.draw(screen, ox)
        dr("goal", self.data["goal"], (0,255,0))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Python Bros")
        self.clock = pygame.time.Clock()
        self.shop = ShopManager(PATHS["shop_file"])
        self.state = "menu"
        self.level_idx = 1
        self.game_level = None
        self.player = None
        
        SFX.play_bgm("menu.mp3")

        # UI Assets
        self.bg_menu = None
        self.shop_bg = None 
        self.logo = None
        self.btn_img = None
        self.btn_hover = None
        self.skin_imgs = {}
        self.coin_icon_hud = None
        
        def ld_ui(n, s=None):
            p = os.path.join(PATHS["ui"], n)
            if os.path.exists(p):
                i = pygame.image.load(p).convert_alpha()
                if s: i = pygame.transform.scale(i, s)
                return i
            return None

        self.bg_menu = ld_ui("menu.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.shop_bg = ld_ui("shop.png", (SCREEN_WIDTH, SCREEN_HEIGHT)) 
        self.logo = ld_ui("Logo_game.png", (300, 130))
        self.btn_img = ld_ui("button.png", (220, 60))
        self.btn_hover = ld_ui("button_hover.png", (220, 60))
        
        for s in ["nhanvat1", "nhanvat2", "nhanvat3", "nhanvat4"]:
            img = ld_ui(f"{s}.png", (80, 80))
            if img: self.skin_imgs[s] = img
            
        self.coin_icon_hud = ld_ui("coin.png", (30, 30))
        if not self.coin_icon_hud:
            try:
                rc = pygame.image.load(os.path.join(PATHS["items"], "coin1.png")).convert_alpha()
                self.coin_icon_hud = pygame.transform.scale(rc, (30, 30))
            except: pass

        self.level_buttons = []
        self.init_buttons()

    def init_buttons(self):
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        start_y = 150
        gap = 70
        
        self.btn_play = Button(pygame.Rect(cx-110, start_y, 220, 60), "P L A Y", 
                               lambda: self.set_state("level_select"), 
                               img=self.btn_img, img_hover=self.btn_hover)
        
        self.btn_shop = Button(pygame.Rect(cx-110, start_y + gap, 220, 60), "S H O P", 
                               lambda: self.set_state("shop"),
                               img=self.btn_img, img_hover=self.btn_hover)
        
        self.btn_quit = Button(pygame.Rect(cx-110, start_y + gap*2, 220, 60), "Q U I T", 
                               lambda: sys.exit(),
                               img=self.btn_img, img_hover=self.btn_hover)
        
        # --- LEVEL SELECT (6 LEVELS) ---
        self.level_buttons = []
        max_lv = self.shop.state["max_level"]
        
        btn_w, btn_h = 80, 80
        btn_gap = 40
        total_w = (btn_w * 3) + (btn_gap * 2)
        start_lx = (SCREEN_WIDTH - total_w) // 2
        start_ly = 130
        
        for i in range(1, 7):
            is_locked = i > max_lv
            row = (i - 1) // 3
            col = (i - 1) % 3
            lx = start_lx + col * (btn_w + btn_gap)
            ly = start_ly + row * (btn_h + btn_gap)
            
            btn = Button(pygame.Rect(lx, ly, btn_w, btn_h), str(i), 
                         lambda l=i: self.start_specific_level(l),
                         bg_color=(46, 204, 113) if not is_locked else (80, 80, 80),
                         hover_color=(88, 214, 141),
                         border_radius=20, is_locked=is_locked)
            self.level_buttons.append(btn)

        self.btn_back_lvl = Button(pygame.Rect(50, 320, 100, 40), "BACK", lambda: self.set_state("menu"), bg_color=(150, 50, 50))

        self.btn_resume = Button(pygame.Rect(cx-110, cy-10, 220, 55), "RESUME", lambda: self.set_state("playing"), bg_color=(46, 204, 113), border_radius=25)
        self.btn_menu_p = Button(pygame.Rect(cx-110, cy+60, 220, 55), "MENU", lambda: self.go_menu(), bg_color=(230, 126, 34), border_radius=25)
        
        self.btn_replay = Button(pygame.Rect(cx-110, cy-10, 220, 55), "REPLAY", lambda: self.restart_level(), bg_color=(46, 204, 113), border_radius=25)
        self.btn_menu_go = Button(pygame.Rect(cx-110, cy+60, 220, 55), "MENU", lambda: self.go_menu(), bg_color=(231, 76, 60), border_radius=25)
        
        # --- NÚT PAUSE BIỂU TƯỢNG (||) ---
        self.btn_pause_small = Button(pygame.Rect(SCREEN_WIDTH-60, 20, 40, 40), "||", lambda: self.set_state("pause"), bg_color=(200, 80, 80), border_radius=10)
        
        self.btn_back = Button(pygame.Rect(SCREEN_WIDTH-130, 10, 110, 40), "BACK", lambda: self.set_state("menu"), bg_color=(150, 50, 50))

    def set_state(self, new_state):
        menu_group = ["menu", "shop", "level_select"]
        if self.state in menu_group and new_state == "playing":
            SFX.stop_bgm()
        elif self.state not in menu_group and new_state in menu_group:
            SFX.play_bgm("menu.mp3")

        self.state = new_state
        if new_state == "level_select":
            self.init_buttons()

    # --- HÀM CẬP NHẬT CON TRỎ CHUỘT ---
    def update_cursor(self):
        mouse_pos = pygame.mouse.get_pos()
        any_hovered = False
        active_buttons = []

        # Xác định các nút đang hiển thị dựa trên trạng thái
        if self.state == "menu":
            active_buttons = [self.btn_play, self.btn_shop, self.btn_quit]
        elif self.state == "level_select":
            active_buttons = self.level_buttons + [self.btn_back_lvl]
        elif self.state == "shop":
            active_buttons = [self.btn_back]
            # Kiểm tra thủ công các nút "mua skin" 
            start_x, start_y = 60, 80
            for i in range(4):
                x = start_x + i * 180
                rect = pygame.Rect(x, start_y, 160, 220)
                btn_rect = pygame.Rect(rect.left + 10, rect.bottom - 55, 140, 45)
                if btn_rect.collidepoint(mouse_pos):
                    any_hovered = True
                    break
        elif self.state == "playing":
            active_buttons = [self.btn_pause_small]
        elif self.state == "pause":
            active_buttons = [self.btn_resume, self.btn_menu_p]
        elif self.state == "game_over":
            active_buttons = [self.btn_replay, self.btn_menu_go]

        # Kiểm tra hover trên các nút tiêu chuẩn
        if not any_hovered:
            for btn in active_buttons:
                # Chỉ hiện tay nếu nút không bị khóa
                if btn.rect.collidepoint(mouse_pos) and not btn.is_locked:
                    any_hovered = True
                    break

        # Đặt con trỏ
        if any_hovered:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def go_menu(self):
        self.set_state("menu")
        self.game_level = None

    def start_specific_level(self, level):
        self.level_idx = level
        self.game_level = None
        self.set_state("playing")

    def restart_level(self):
        self.game_level = None
        self.set_state("playing")

    def load_level_data(self):
        path = os.path.join(PATHS["tiles"], f"level{self.level_idx}.json")
        if not os.path.exists(path): return None
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            
            ts = data.get("tile_size", 32)
            tiles = data.get("tiles", [])
            width = max(len(r) for r in tiles)
            
            ld = {
                "platforms": [], "stones": [], "pits": [], "coins": [],
                "enemies": [], "spawn": None, "goal": None,
                "tile_size": ts, "width": width, "height": len(tiles)
            }
            
            for y, row in enumerate(tiles):
                row = row.ljust(width, '.')
                for x, ch in enumerate(row):
                    r = pygame.Rect(x*ts, y*ts, ts, ts)
                    if ch=='#': ld["platforms"].append(r)
                    elif ch=='S': ld["stones"].append(r)
                    elif ch=='_': ld["pits"].append(r)
                    elif ch=='C': ld["coins"].append((r.centerx, r.centery))
                    elif ch=='E': ld["enemies"].append((r.x, r.y))
                    elif ch=='P': ld["spawn"] = (r.x, r.y)
                    elif ch=='G': ld["goal"] = r
            
            if not ld["spawn"]: ld["spawn"] = (100, 300)
            if not ld["goal"]: ld["goal"] = pygame.Rect(0,0,32,32)
            return ld
        except: return None

    def update(self):
        if self.state == "playing":
            if not self.game_level:
                parsed = self.load_level_data()
                if parsed:
                    self.game_level = Level(parsed, self.level_idx)
                    skin = self.shop.state["equipped_skin"]
                    self.player = Player(self.game_level.data["spawn"], skin, self.shop)
                    
                    # --- MỚI THÊM: PHÁT NHẠC NỀN CHO TỪNG LEVEL ---
                    SFX.play_bgm(f"level{self.level_idx}")
                else:
                    print(f"Chưa có map level {self.level_idx}")
                    self.set_state("level_select")

            if self.player and self.game_level:
                self.player.update(self.game_level.data)
                self.game_level.update(self.player)
                self.game_level.offset_x = max(0, self.player.rect.centerx - SCREEN_WIDTH // 2)

                if self.player.dead:
                    self.state = "game_over"
                elif self.player.win:
                    self.shop.unlock_next_level(self.level_idx)
                    self.level_idx += 1
                    path_next = os.path.join(PATHS["tiles"], f"level{self.level_idx}.json")
                    if not os.path.exists(path_next):
                        print("Hết màn chơi!")
                        self.set_state("level_select")
                    else:
                        self.game_level = None

    def draw(self):
        # 1. MENU
        if self.state == "menu":
            if self.bg_menu: self.screen.blit(self.bg_menu, (0,0))
            else: self.screen.fill((40, 40, 50))
            if self.logo: self.screen.blit(self.logo, self.logo.get_rect(center=(SCREEN_WIDTH//2, 80)))
            self.btn_play.draw(self.screen)
            self.btn_shop.draw(self.screen)
            self.btn_quit.draw(self.screen)

        # 2. LEVEL SELECT
        elif self.state == "level_select":
            if self.bg_menu: self.screen.blit(self.bg_menu, (0,0))
            else: self.screen.fill((30, 30, 40))
            
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0,0))
            
            t = FONT_TITLE.render("SELECT LEVEL", True, (255, 255, 255))
            self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, 60)))
            
            for btn in self.level_buttons:
                btn.draw(self.screen)
            self.btn_back_lvl.draw(self.screen)

        # 3. SHOP
        elif self.state == "shop":
            if self.shop_bg: self.screen.blit(self.shop_bg, (0,0))
            else: self.screen.fill((30, 30, 40))
            
            hud_surf = pygame.Surface((120, 40), pygame.SRCALPHA)
            hud_surf.fill((0, 0, 0, 140))
            pygame.draw.rect(hud_surf, (200, 200, 200), hud_surf.get_rect(), width=2, border_radius=10)
            self.screen.blit(hud_surf, (20, 10))
            
            coins = self.shop.state["coins"]
            if self.coin_icon_hud: self.screen.blit(self.coin_icon_hud, (25, 18))
            lbl = FONT_BTN.render(str(coins), True, (255, 230, 100))
            self.screen.blit(lbl, (60, 20))
            
            self.btn_back.draw(self.screen)
            
            skins = self.shop.all_skins
            owned = self.shop.state["owned_skins"]
            equipped = self.shop.state["equipped_skin"]
            
            start_x, start_y = 60, 80
            for i, sid in enumerate(skins):
                x = start_x + i * 180
                rect = pygame.Rect(x, start_y, 160, 220)
                
                card_surf = pygame.Surface((160, 220), pygame.SRCALPHA)
                card_surf.fill((0, 0, 0, 150))
                self.screen.blit(card_surf, (x, start_y))
                
                color = (50, 200, 50) if sid == equipped else (200, 200, 200)
                pygame.draw.rect(self.screen, color, rect, width=2, border_radius=15)
                
                if sid in self.skin_imgs:
                    img = self.skin_imgs[sid]
                    self.screen.blit(img, img.get_rect(center=(rect.centerx, rect.centery - 40)))
                
                nm = FONT_BTN.render(sid, True, (255, 255, 255))
                self.screen.blit(nm, nm.get_rect(center=(rect.centerx, rect.centery + 10)))
                
                btn_rect = pygame.Rect(rect.left + 10, rect.bottom - 55, 140, 45)
                if sid in owned:
                    txt = "EQUIPPED" if sid == equipped else "EQUIP"
                    bg = (46, 204, 113) if sid == equipped else (52, 152, 219)
                else:
                    txt = "BUY (50)"
                    bg = (231, 76, 60)
                pygame.draw.rect(self.screen, bg, btn_rect, border_radius=20)
                pygame.draw.rect(self.screen, (255,255,255), btn_rect, width=2, border_radius=20)
                l = FONT_BTN.render(txt, True, (255,255,255))
                self.screen.blit(l, l.get_rect(center=btn_rect.center))

        # 4. PLAYING / PAUSE / GAME OVER
        else:
            self.screen.fill((0, 0, 0))
            if self.game_level and self.player:
                self.game_level.draw(self.screen)
                self.player.draw(self.screen, self.game_level.offset_x)
            
            self.btn_pause_small.draw(self.screen)
            
            if self.player:
                # --- HUD CĂN CHỈNH LẠI ---
                hud_bg = pygame.Surface((140, 45), pygame.SRCALPHA)
                pygame.draw.rect(hud_bg, (0, 0, 0, 160), hud_bg.get_rect(), border_radius=22) 
                pygame.draw.rect(hud_bg, (255, 215, 0), hud_bg.get_rect(), width=2, border_radius=22)
                self.screen.blit(hud_bg, (20, 20))

                total = self.shop.state["coins"]
                
                if self.coin_icon_hud:
                    self.screen.blit(self.coin_icon_hud, (30, 28))
                    text_x = 70
                else:
                    text_x = 40
                
                # --- CANH GIỮA TEXT COIN ---
                txt = FONT_BTN.render(f"{total}", True, (255, 255, 255))
                txt_shadow = FONT_BTN.render(f"{total}", True, (0, 0, 0))
                
                # Tính toán Y để text nằm giữa khung
                txt_rect = txt.get_rect(midleft=(text_x, 43))
                txt_shadow_rect = txt_shadow.get_rect(midleft=(text_x + 2, 45))
                
                self.screen.blit(txt_shadow, txt_shadow_rect)
                self.screen.blit(txt, txt_rect)
                
                for i in range(self.player.lives):
                    draw_heart(self.screen, 35 + i*30, 85, (230, 50, 50))

            if self.state == "pause" or self.state == "game_over":
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180)) 
                self.screen.blit(overlay, (0,0))
                
                cx = SCREEN_WIDTH // 2
                
                if self.state == "pause":
                    t = FONT_TITLE.render("PAUSED", True, (255, 255, 255))
                    self.screen.blit(t, t.get_rect(center=(cx, 100)))
                    self.btn_resume.draw(self.screen)
                    self.btn_menu_p.draw(self.screen)
                
                elif self.state == "game_over":
                    t = FONT_TITLE.render("GAME OVER", True, (231, 76, 60))
                    self.screen.blit(t, t.get_rect(center=(cx, 100)))
                    self.btn_replay.draw(self.screen)
                    self.btn_menu_go.draw(self.screen)

        pygame.display.flip()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "playing": self.set_state("pause")
                    elif self.state == "shop": self.set_state("menu")
                    elif self.state == "level_select": self.set_state("menu")

            if self.state == "menu":
                self.btn_play.handle_event(event)
                self.btn_shop.handle_event(event)
                self.btn_quit.handle_event(event)
            
            elif self.state == "level_select":
                self.btn_back_lvl.handle_event(event)
                for btn in self.level_buttons:
                    btn.handle_event(event)

            elif self.state == "shop":
                self.btn_back.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    skins = self.shop.all_skins
                    owned = self.shop.state["owned_skins"]
                    start_x, start_y = 60, 80
                    for i, sid in enumerate(skins):
                        x = start_x + i * 180
                        rect = pygame.Rect(x, start_y, 160, 220)
                        btn_rect = pygame.Rect(rect.left + 10, rect.bottom - 55, 140, 45)
                        if btn_rect.collidepoint(event.pos):
                            if sid in owned: self.shop.equip_skin(sid)
                            else: self.shop.buy_skin(sid)

            elif self.state == "playing":
                self.btn_pause_small.handle_event(event)
            
            elif self.state == "pause":
                self.btn_resume.handle_event(event)
                self.btn_menu_p.handle_event(event)
                
            elif self.state == "game_over":
                self.btn_replay.handle_event(event)
                self.btn_menu_go.handle_event(event)

    def run(self):
        while True:
            self.update_cursor()
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()