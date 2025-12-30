import pygame
import os
from character import Player
from enemy import EnemyWalk, EnemyDead
from level import Level
from map_loader import load_level_json, parse_level

class Gameplay:
    def __init__(self, screen_size, ui_manager=None):
        self.screen_width, self.screen_height = screen_size
        self.ui = ui_manager
        
        self.internal_state = "ACTION" 
        self.current_level_index = 1
        
        self.max_lives = 6
        self.lives = self.max_lives
        self.game_over = False
        self.victory = False
        self.paused = False
        
        try: pygame.mixer.quit()
        except: pass
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        self.sound_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sounds")
        self.sfx = {}
        
        def load_sfx(name):
            p = os.path.join(self.sound_dir, name)
            if os.path.exists(p): 
                s = pygame.mixer.Sound(p)
                s.set_volume(0.6)
                return s
            return None 

        self.sfx["jump"] = load_sfx("jump.wav")
        self.sfx["coin"] = load_sfx("coin.wav")
        self.sfx["hit"] = load_sfx("hit.wav")
        self.sfx["die"] = load_sfx("die.wav")
        self.sfx["win"] = load_sfx("win.wav")
        self.sfx["gameover"] = load_sfx("gameover.wav") 
        
        self.heart_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.heart_surf, (255, 50, 50), (10, 10), 8)
        pygame.draw.circle(self.heart_surf, (255, 50, 50), (20, 10), 8)
        pygame.draw.polygon(self.heart_surf, (255, 50, 50), [(2, 14), (28, 14), (15, 28)])
        
        self.font = pygame.font.SysFont("arial", 22) 
        self.font_big = pygame.font.SysFont("arial", 40, bold=True)

        self.mouse_pressed_prev = False
        self.level = None
        self.player = None
        self.active_enemies = []
        self.pits = []
        
        self.is_invincible = False
        self.invincible_timer = 0
        
        self.load_level(1)

    def play_sfx(self, name):
        if self.sfx.get(name): self.sfx[name].play()

    def play_music_file(self, filename):
        pass 

    def load_level(self, index):
        print(f"--- Loading Level {index} ---")
        self.current_level_index = index
        
        try:
            path = os.path.join("assets", "tiles", f"level{index}.json")
            data = load_level_json(path)
            parsed = parse_level(data)
            self.level = Level(parsed, index)
            
            current_skin = "nhanvat1"
            if self.ui and hasattr(self.ui, 'shop') and self.ui.shop:
                shop_skin = self.ui.shop.get_equipped_skin()
                if shop_skin: current_skin = shop_skin
            
            current_coins = 0
            if self.ui and hasattr(self.ui, 'shop') and self.ui.shop:
                current_coins = self.ui.shop.get_coins()

            sx, sy = self.level.spawn_point
            self.player = Player(sx, sy, skin=current_skin)

            self.player.coins = current_coins 

            self.player.rect.size = (20, 28) 
            self.player.rect.center = self.player.rect.center
            self.player.speed = 4 
            
            self.player.on_death = self.respawn_at_checkpoint 
            self.player.on_reach_goal = self.on_level_complete

            self.pits = list(self.level.pits) 
            self.level.pits = [] 

            self.active_enemies = []
            for (ex, ey) in self.level.enemies:
                self.active_enemies.append(EnemyWalk(ex, ey))
            self.level.enemies = [] 
            self.level.offset_x = 0
            
            self.game_over = False
            self.victory = False
            self.paused = False
            self.lives = self.max_lives
            self.internal_state = "ACTION"
            
        except Exception as e:
            print(f"Error loading level: {e}")
            if self.ui: self.ui.state = "menu"

    def update(self, keys):
        mouse_pressed = pygame.mouse.get_pressed()[0]
        is_click = mouse_pressed and not self.mouse_pressed_prev
        self.mouse_pressed_prev = mouse_pressed
        mouse_pos = pygame.mouse.get_pos()
        
        self.update_game_action(keys, is_click, mouse_pos)

    def update_game_action(self, keys, is_click, mouse_pos):
        if not self.game_over and not self.victory:
            if keys[pygame.K_ESCAPE] and not self.paused:
                self.paused = True
            
            pause_btn_rect = pygame.Rect(self.screen_width - 120, 10, 100, 36)
            if is_click and pause_btn_rect.collidepoint(mouse_pos) and not self.paused:
                self.paused = True
            
            if self.paused:
                box_w, box_h = 360, 220
                box_left = self.screen_width // 2 - box_w // 2
                box_top = self.screen_height // 2 - box_h // 2
                
                rect_resume = pygame.Rect(box_left + 40, box_top + 90, box_w - 80, 44)
                rect_menu = pygame.Rect(box_left + 40, box_top + 148, box_w - 80, 44)

                if is_click:
                    if rect_resume.collidepoint(mouse_pos):
                        self.paused = False
                    elif rect_menu.collidepoint(mouse_pos):
                        if self.ui: self.ui.state = "menu"
                return 

        if self.game_over or self.victory:
            btn_w, btn_h = 200, 50
            center_x, center_y = self.screen_width // 2, self.screen_height // 2 

            rect_top = pygame.Rect(center_x - btn_w//2, center_y - 30, btn_w, btn_h)
            rect_bot = pygame.Rect(center_x - btn_w//2, center_y + 40, btn_w, btn_h)
            
            if is_click:
                if rect_top.collidepoint(mouse_pos):
                    if self.victory and self.current_level_index < 6:
                        self.load_level(self.current_level_index + 1)
                    else:
                        self.load_level(1) 
                
                elif rect_bot.collidepoint(mouse_pos):
                    if self.ui: self.ui.state = "menu"
            return


        if self.ui and hasattr(self.ui, 'shop') and self.ui.shop:
            shop_skin = self.ui.shop.get_equipped_skin()
            if shop_skin and self.player.skin != shop_skin:
                self.player.skin = shop_skin
                self.player.load_animations()
                self.player.current_anim = self.player.anims.get("idle", self.player.current_anim)

        if self.is_invincible and pygame.time.get_ticks() - self.invincible_timer > 2000:
            self.is_invincible = False 

        old_coin = self.player.coins
        self.update_player_physics(keys)
        
        if self.player.rect.topleft == self.level.spawn_point and self.lives < self.max_lives: return 


        for i, enemy in enumerate(self.active_enemies):
            if isinstance(enemy, EnemyDead):
                enemy.update(1)
                continue 
            self.move_enemy_smart(enemy, self.level.all_solids, self.pits)
            if self.player.rect.colliderect(enemy.rect):
                if self.player.vel_y > 0 and self.player.rect.bottom < enemy.rect.centery + 15:
                    corpse = EnemyDead(enemy.rect.x, enemy.rect.y)
                    self.active_enemies[i] = corpse
                    self.player.vel_y = -8
                    self.play_sfx("hit") 
                else:
                    self.player.vel_y = -5
                    self.take_damage()

        self.level.update(self.player)

        for pit in self.pits:
            if self.player.rect.colliderect(pit.inflate(-10, -10)):
                self.player.vel_y = -9
                self.player.on_ground = False
                self.take_damage()

        if self.player.coins > old_coin:
            if self.ui and self.ui.shop: 
                diff = self.player.coins - old_coin
                self.ui.shop.state["coins"] += diff
            self.play_sfx("coin") 

        self.level.update_camera(self.player, self.screen_width)

    def draw(self, screen):
        self.draw_game_action(screen)

    def draw_game_action(self, screen):
        if not self.level: return
        self.level.draw(screen)
        cam_x = self.level.offset_x
        
        for pit in self.pits:
            if self.level.img_pit: screen.blit(self.level.img_pit, (pit.x - cam_x, pit.y))
            else: pygame.draw.rect(screen, (0, 0, 0), pit.move(-cam_x, 0))
            
        for enemy in self.active_enemies:
            img = self.level.enemy_walk_frames[0] if self.level.enemy_walk_frames else None
            draw_pos = (enemy.rect.x - cam_x, enemy.rect.y)
            if img:
                if hasattr(enemy, 'smart_dir') and enemy.smart_dir == -1: img = pygame.transform.flip(img, True, False)
                if isinstance(enemy, EnemyDead):
                    dead_img = pygame.transform.scale(img, (img.get_width(), img.get_height() // 2))
                    screen.blit(dead_img, (draw_pos[0], draw_pos[1] + img.get_height() // 2))
                else:
                    screen.blit(img, draw_pos)
            else: 
                pygame.draw.rect(screen, (200, 50, 50), (*draw_pos, 32, 32))

        should_draw = True
        if self.is_invincible and (pygame.time.get_ticks() // 100) % 2 == 0: should_draw = False
        if should_draw:
            img = self.player.current_anim.get_image()
            if not self.player.facing_right: img = pygame.transform.flip(img, True, False)
            off_x = (self.player.rect.width - img.get_width()) // 2
            off_y = (self.player.rect.height - img.get_height()) // 2
            screen.blit(img, (self.player.rect.x - cam_x + off_x, self.player.rect.y + off_y - 8))

        for i in range(self.lives): screen.blit(self.heart_surf, (10 + i * 35, self.screen_height - 40))
        
        if self.ui:
            self.ui.draw_hud() 
            if self.paused:
                self.ui.draw_pause()

        if self.game_over or self.victory:
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            center_x, center_y = self.screen_width // 2, self.screen_height // 2
            txt = self.font_big.render("GAME OVER" if self.game_over else "VICTORY!", True, (255, 50, 50) if self.game_over else (50, 255, 50))
            screen.blit(txt, txt.get_rect(center=(center_x, center_y - 80)))
            
            mouse_pos = pygame.mouse.get_pos()
            btn_w, btn_h = 200, 50
            
            rect_top = pygame.Rect(center_x - btn_w//2, center_y - 30, btn_w, btn_h)
            top_col = (100, 200, 100)
            if rect_top.collidepoint(mouse_pos): top_col = (120, 220, 120)
            pygame.draw.rect(screen, top_col, rect_top, border_radius=10)
            pygame.draw.rect(screen, (220, 220, 220), rect_top, width=2, border_radius=10)
            
            top_text = "Play Again"
            if self.victory: top_text = "Play Again" 
            
            lbl_top = self.font.render(top_text, True, (255, 255, 255))
            screen.blit(lbl_top, lbl_top.get_rect(center=rect_top.center))

            rect_bot = pygame.Rect(center_x - btn_w//2, center_y + 40, btn_w, btn_h)
            bot_col = (180, 80, 80)
            if rect_bot.collidepoint(mouse_pos): bot_col = (200, 100, 100)
            pygame.draw.rect(screen, bot_col, rect_bot, border_radius=10)
            pygame.draw.rect(screen, (220, 220, 220), rect_bot, width=2, border_radius=10)
            lbl_bot = self.font.render("Exit to Menu", True, (255, 255, 255))
            screen.blit(lbl_bot, lbl_bot.get_rect(center=rect_bot.center))

    def respawn_at_checkpoint(self):
        self.lives -= 1
        if self.lives > 0:
            self.play_sfx("die") 
            self.player.rect.topleft = self.level.spawn_point
            self.player.vel_x = 0
            self.player.vel_y = 0
            self.player.state = "idle"
            self.is_invincible = False
            self.level.update_camera(self.player, self.screen_width)
        else: 
            self.play_sfx("gameover") 
            self.game_over = True

    def take_damage(self):
        if self.is_invincible: return 
        self.lives -= 1
        if self.lives > 0: 
            self.play_sfx("hit") 
            self.is_invincible = True
            self.invincible_timer = pygame.time.get_ticks()
        else: 
            self.play_sfx("gameover") 
            self.game_over = True

    def on_level_complete(self):
        print(f"Level {self.current_level_index} Complete!")
        self.play_sfx("win") 
        if self.ui and hasattr(self.ui, 'shop') and self.ui.shop: 
            self.ui.shop.unlock_level(self.current_level_index + 1)
        
        if self.current_level_index < 6:
            self.load_level(self.current_level_index + 1)
        else:
            self.victory = True 

    def update_player_physics(self, keys):
        p = self.player
        solids = self.level.all_solids
        p.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: 
            p.vel_x = -p.speed
            p.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: 
            p.vel_x = p.speed
            p.facing_right = True
        
        p.rect.x += p.vel_x
        if p.rect.left < 0: p.rect.left = 0
        for t in solids:
            if p.rect.colliderect(t):
                if p.vel_x > 0: p.rect.right = t.left
                elif p.vel_x < 0: p.rect.left = t.right
        
        p.vel_y += 0.8
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and p.on_ground:
            p.vel_y = p.jump_power
            p.on_ground = False
            self.play_sfx("jump") 
             
        p.rect.y += p.vel_y
        p.on_ground = False
        for t in solids:
            if p.rect.colliderect(t):
                if p.vel_y > 0: 
                    p.rect.bottom = t.top
                    p.vel_y = 0
                    p.on_ground = True
                elif p.vel_y < 0: 
                    p.rect.top = t.bottom
                    p.vel_y = 0
        
        if p.rect.top > self.screen_height: self.respawn_at_checkpoint()

        if not p.on_ground: p.state = "jump" if p.vel_y < 0 else "fall"
        elif p.vel_x != 0: p.state = "run"
        else: p.state = "idle"
        p.current_anim = p.anims.get(p.state, p.anims["idle"])
        p.current_anim.update()
    
    def move_enemy_smart(self, e, solids, spikes):
        if not hasattr(e, 'smart_dir'): e.smart_dir = 1
        if not hasattr(e, 'smart_speed'): e.smart_speed = 1 
        
        nx = e.rect.x + (e.smart_dir * e.smart_speed)
        tr = e.rect.copy()
        tr.x = nx
        
        hit = False
        for t in solids:
            if tr.colliderect(t): 
                hit = True
                break
        
        if not hit:
            for spike in spikes:
                if tr.colliderect(spike.inflate(-10, -10)): 
                    hit = True
                    break

        cp = (tr.right + 2, tr.bottom + 2) if e.smart_dir > 0 else (tr.left - 2, tr.bottom + 2)
        grounded = False
        for t in solids:
            if t.collidepoint(cp): 
                grounded = True
                break
            
        if hit or not grounded: e.smart_dir *= -1
        else: e.rect.x = nx
        e.direction = e.smart_dir