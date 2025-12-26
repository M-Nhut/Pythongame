import pygame
import json
import os
from pathlib import Path
from typing import Callable, List, Optional, Tuple

pygame.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
ASSET_PATH = os.path.join(PROJECT_ROOT, "assets", "ui")

FONT = pygame.font.SysFont("Berlin Sans FB Demi", 20)
BIGFONT = pygame.font.SysFont("arial", 36)


# -------- BUTTON--------
class Button:
    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        callback: Callable[[], None],
        img: Optional[pygame.Surface] = None,
        img_hover: Optional[pygame.Surface] = None,
        bg_color: Optional[Tuple[int, int, int]] = None,
    ):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.hover = False

        self.img = img
        self.img_hover = img_hover if img_hover else img
        self.use_image = img is not None

        self.bg_color = bg_color or (200, 220, 240)
        r, g, b = self.bg_color
        self.bg_hover = (min(255, r + 20), min(255, g + 20), min(255, b + 20))
        
        self.text_color = (204,30,30) if self.use_image else (20, 20, 20)

    def draw(self, surf: pygame.Surface):   
        if self.use_image:
            img = self.img_hover if self.hover and self.img_hover else self.img
            if img:
                surf.blit(img, self.rect)
        else:
            color = self.bg_hover if self.hover else self.bg_color
            pygame.draw.rect(surf, color, self.rect, border_radius=8)
            pygame.draw.rect(surf, (30, 30, 30), self.rect, width=2, border_radius=8)

        label = FONT.render(self.text, True, self.text_color)
        surf.blit(label, label.get_rect(center=self.rect.center))

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                try:
                    self.callback()
                except Exception as e:
                    print("[Button] callback error:", e)


# -------- MAIN UI --------
class GameUI:
    def __init__(self, shop_client=None, size=(800, 380)):
        self.size = size
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("UI Module")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"  
        self.shop = shop_client

        def load_img(name: str, scale: Optional[Tuple[int, int]] = None) -> Optional[pygame.Surface]:
            path = os.path.join(ASSET_PATH, name)
            if not os.path.exists(path):
                print("[MISSING]", path)
                return None
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, scale) if scale else img

        self.menu_bg = load_img("menu.jpg", self.size)
        self.shop_bg = load_img("shop.png", self.size)
        self.logo = load_img("Logo_game.png", (320, 140))
        self.btn_img = load_img("button.png", (220, 60))
        self.btn_hover = load_img("button_hover.png", (220, 60)) or self.btn_img
        self.coin_icon = load_img("coin.png", (50, 50))
        # ---- LOAD SKIN IMAGES ----
        self.skin_images = {}

        for skin_name in (self.shop.get_all_skins() if self.shop else []):
            img_path = os.path.join(ASSET_PATH, f"{skin_name}.png")
            if os.path.exists(img_path):
                self.skin_images[skin_name] = pygame.transform.scale(
                    pygame.image.load(img_path).convert_alpha(), (100,100)
                )
            else:
                print(f"[MISSING] Skin image: {img_path}")

        self.buttons: List[Button] = []
        self._create_main_menu()

        w, h = self.size
        self.pause_button = Button(pygame.Rect(w - 120, 10, 100, 36), "Pause", self.open_pause, bg_color=(200, 140, 140))

        self._pause_buttons: List[Button] = []

        self.shop_buttons: List[Button] = []

# -------- MAIN BUTTON --------
    def _create_main_menu(self):
        w, h = self.size
        btn_w, btn_h = 220, 60
        x = (w - btn_w) // 2
        start_y = 150
        gap = 60

        self.buttons = [
            Button(pygame.Rect(x, start_y, btn_w, btn_h), "P L A Y", self.start_game, self.btn_img, self.btn_hover),
            Button(pygame.Rect(x, start_y + gap, btn_w, btn_h), "S H O P", self.open_shop, self.btn_img, self.btn_hover),
            Button(pygame.Rect(x, start_y + 2 * gap, btn_w, btn_h), "Q U I T", self.quit, self.btn_img, self.btn_hover),
        ]

    def start_game(self):
        print("[UI] start_game")
        self.state = "playing"

    def open_shop(self):
        print("[UI] open_shop")
        self.state = "shop"

    def open_pause(self):
        print("[UI] open_pause")
        self.state = "pause"

    def back_to_menu(self):
        print("[UI] back_to_menu")
        self.state = "menu"

    def quit(self):
        print("[UI] quit")
        self.running = False

# -------- DRAW MENU --------
    def draw_menu(self):
        if self.menu_bg:
            self.screen.blit(self.menu_bg, (0, 0))
        else:
            self.screen.fill((30, 30, 50))

        if self.logo:
            rect = self.logo.get_rect(center=(self.size[0] // 2, 80))
            self.screen.blit(self.logo, rect)

        for b in self.buttons:
            b.draw(self.screen)

 
# -------- DRAW PAUSE--------
    def draw_pause(self):
        overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        box_w, box_h = 360, 220
        box = pygame.Rect(self.size[0] // 2 - box_w // 2, self.size[1] // 2 - box_h // 2, box_w, box_h)
        pygame.draw.rect(self.screen, (40, 44, 50), box, border_radius=10)
        pygame.draw.rect(self.screen, (20, 20, 20), box, width=3, border_radius=10)

        label = BIGFONT.render("PAUSED", True, (245, 245, 245))
        self.screen.blit(label, (box.centerx - label.get_width() // 2, box.top + 24))

        resume_rect = pygame.Rect(box.left + 40, box.top + 90, box_w - 80, 44)
        menu_rect = pygame.Rect(box.left + 40, box.top + 148, box_w - 80, 44)

        resume_btn = Button(resume_rect, "Resume", self._resume, bg_color=(140, 220, 140))
        menu_btn = Button(menu_rect, "Menu", self.back_to_menu, bg_color=(220, 140, 140))

        resume_btn.draw(self.screen)
        menu_btn.draw(self.screen)
        self._pause_buttons = [resume_btn, menu_btn]

    def _resume(self):
        print("[UI] resume")
        self.state = "playing"

    def draw_hud(self):
        pygame.draw.rect(self.screen, (28, 28, 36), pygame.Rect(8, 8, 260, 64), border_radius=8)
        coins = self.shop.get_coins() if self.shop else 0
        equipped = self.shop.get_equipped_skin() if self.shop else "None"
        self.screen.blit(FONT.render(f"Coins: {coins}", True, (240, 240, 180)), (18, 18))
        self.screen.blit(FONT.render(f"Skin: {equipped}", True, (210, 210, 210)), (18, 40))
        self.pause_button.draw(self.screen)

# -------- DRAW SHOP--------
    def draw_shop(self):
        if self.shop_bg:
            self.screen.blit(self.shop_bg, (0, 0))
        else:
            self.screen.fill((30, 30, 40))

        # --- COIN HUD in Shop ---
        hud_w, hud_h = 100, 40
        hud_rect = pygame.Rect(10, 10, hud_w, hud_h)

        # làm nền mờ (semi-transparent)
        hud_surf = pygame.Surface((hud_w, hud_h), pygame.SRCALPHA)
        hud_surf.fill((0, 0, 0, 140))  # màu đen mờ 120/255 opacity
        pygame.draw.rect(hud_surf, (200, 200, 200, 190), hud_surf.get_rect(), border_radius=10)

        # đổ nền lên màn hình
        self.screen.blit(hud_surf, (25, 15))

        # coin icon
        if self.coin_icon:
            self.screen.blit(self.coin_icon, (25, 10))  

        # text vàng giống style fantasy (vàng sáng + viền nhẹ)
        coins = str(self.shop.get_coins())

        # Shadow
        shadow = FONT.render(coins, True, (50, 30, 0))
        self.screen.blit(shadow, (62, 33))

        # Glow text vàng
        coins_text = FONT.render(coins, True, (255, 230, 120))
        self.screen.blit(coins_text, (60, 30))
        skins = self.shop.get_all_skins()
        owned = set(self.shop.get_owned_skins())
        equipped = self.shop.get_equipped_skin()

        cols = 4                 
        box_w, box_h = 120, 120
        gap = 20

        total_width = cols * box_w + (cols - 1) * gap
        start_x = (self.size[0] - total_width) // 2
        start_y = 90

        self.shop_buttons = []

        for i, skin_id in enumerate(skins):
            row = i // 4   
            col = i % 4

            rect = pygame.Rect(start_x + col*(box_w+gap), start_y + row*(box_h+110), box_w, box_h)


            pygame.draw.rect(self.screen, (70, 70, 70), rect, border_radius=10)

            if skin_id in self.skin_images:
                img = self.skin_images[skin_id]
                img_rect = img.get_rect(center=(rect.centerx, rect.centery-5))
                self.screen.blit(img, img_rect)
            else:
                label = FONT.render(skin_id, True, (255, 255, 255))
                self.screen.blit(label, label.get_rect(center=rect.center))

            btn_rect = pygame.Rect(rect.left, rect.bottom+8, box_w, 40)

            if skin_id in owned:
                txt = "Equipped" if skin_id == equipped else "Equip"
                btn = Button(btn_rect, txt, lambda s=skin_id: self._equip(s), bg_color=(90, 180, 90))
            else:
                btn = Button(btn_rect, "Buy (50)", lambda s=skin_id: self._buy(s), bg_color=(150,150,220))

            btn.draw(self.screen)
            self.shop_buttons.append(btn)


        back_btn = Button(pygame.Rect(self.size[0]-150, self.size[1]-60, 120, 45),
                        "Back", self.back_to_menu, bg_color=(180,80,80))
        back_btn.draw(self.screen)
        self.shop_buttons.append(back_btn)
    def _buy(self, skin_id):
        if not self.shop:
            print("[SHOP] no shop client")
            return
        ok, msg = self.shop.buy_skin(skin_id)
        print("[SHOP] buy ->", ok, msg)

    def _equip(self, skin_id):
        if not self.shop:
            print("[SHOP] no shop client")
            return
        ok, msg = self.shop.equip_skin(skin_id)
        print("[SHOP] equip ->", ok, msg)
# -------- MAIN LOOP--------
    def run(self):
        while self.running:
            self._handle_events()

            if self.state == "menu":
                self.draw_menu()
            elif self.state == "playing":
                self.screen.fill((30, 110, 70))
                self.draw_hud()
            elif self.state == "shop":
                self.draw_shop()
            elif self.state == "pause":
                self.screen.fill((30, 110, 70))
                self.draw_hud()
                self.draw_pause()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

# -------- EVENT -------
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.state == "menu":
                for b in self.buttons:
                    b.handle_event(event)

            elif self.state == "playing":
                self.pause_button.handle_event(event)

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.open_pause()

            elif self.state == "shop":
                for b in list(self.shop_buttons):
                    b.handle_event(event)

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.back_to_menu()

            elif self.state == "pause":
                for b in list(self._pause_buttons):
                    b.handle_event(event)

# ---------------- Dummy Shop ----------------
class DummyShop:
    def __init__(self, save_file: str = "shop_state.json"):
        self.save_file = Path(save_file)
        self.state = {
            "coins": 1000,
            "owned_skins": ["nhanvat1"],
            "equipped_skin": "nhanvat1",
            "unlocked_levels": [1],
        }
        self._all_skins = ["nhanvat1", "nhanvat2", "nhanvat3", "nhanvat4"]

    def save_state(self):
        try:
            with open(self.save_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("[Shop] save error:", e)

    def load_state(self):
        if self.save_file.exists():
            try:
                with open(self.save_file, "r", encoding="utf-8") as f:
                    self.state = json.load(f)
            except Exception as e:
                print("[Shop] load error:", e)

    def get_coins(self):
        return self.state.get("coins", 0)

    def get_owned_skins(self):
        return list(self.state.get("owned_skins", []))

    def get_equipped_skin(self):
        return self.state.get("equipped_skin")

    def get_all_skins(self):
        return list(self._all_skins)

    def buy_skin(self, skin_id: str):
        price = 50
        if skin_id in self.state["owned_skins"]:
            return False, "Already owned"
        if self.state["coins"] < price:
            return False, "Not enough coins"
        self.state["coins"] -= price
        self.state["owned_skins"].append(skin_id)
        self.save_state()
        return True, "Bought"

    def equip_skin(self, skin_id: str):
        if skin_id not in self.state["owned_skins"]:
            return False, "Skin not owned"
        self.state["equipped_skin"] = skin_id
        self.save_state()
        return True, "Equipped"

    def unlock_level(self, level: int):
        if level in self.state.get("unlocked_levels", []):
            return False, "Already unlocked"
        self.state.setdefault("unlocked_levels", []).append(level)
        self.save_state()
        return True, "Unlocked"

    def is_level_unlocked(self, level: int):
        return level in self.state.get("unlocked_levels", [])

