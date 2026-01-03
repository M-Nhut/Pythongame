import pygame
from ui import GameUI, DummyShop
from gameplay import Gameplay


pygame.init()
SCREEN_SIZE = (800, 380) 
screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()

shop = DummyShop()
shop.load_state()
ui = GameUI(shop_client=shop, size=SCREEN_SIZE)


game = Gameplay(SCREEN_SIZE, ui_manager=ui)

running = True
previous_ui_state = "menu"

while running:
    keys = pygame.key.get_pressed()
    
    ui._handle_events()
    if not ui.running:
        running = False

    if keys[pygame.K_r] and game.game_over:
        game.game_over = False
        game.load_level(game.current_level_index) 


    if ui.state == "menu":
        should_reset = (
            previous_ui_state in ["playing", "pause"] or  
            game.game_over or  
            game.victory
        )
        if should_reset:
            game.load_level(1)
            game.lives = game.max_lives  
            game.game_over = False
            game.victory = False
        ui.draw_menu()

    elif ui.state == "level_select":
        ui.draw_level_select()

    elif ui.state == "playing":
        if previous_ui_state != "playing":
            game.internal_state = "SELECT"
            if previous_ui_state == "level_select" and hasattr(ui, 'selected_level'):
                game.load_level(ui.selected_level)
                game.lives = game.max_lives
                game.game_over = False
                game.victory = False
            
        if keys[pygame.K_ESCAPE]:
            ui.state = "pause"
        else:
            game.update(keys)

        screen.fill((0, 0, 0)) 
        game.draw(screen)

        if game.internal_state == "ACTION":
            ui.draw_hud()

    elif ui.state == "shop":
        ui.draw_shop()
    
    elif ui.state == "pause":
        game.draw(screen)
        if game.internal_state == "ACTION":
             ui.draw_hud()
        ui.draw_pause()

    previous_ui_state = ui.state

    pygame.display.flip()
    clock.tick(60)

shop.save_state()
pygame.quit()