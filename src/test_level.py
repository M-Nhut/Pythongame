# test_level.py – chạy test Level + DummyPlayer giống Mario
import pygame
from map_loader import load_level_json, parse_level
from level import Level
from dummy_player import DummyPlayer

SCREEN_W = 800     # màn hình nhỏ để thấy camera follow
SCREEN_H = 380

def run_level(index):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption(f"Level Test {index}")

    clock = pygame.time.Clock()

    # -------- LOAD LEVEL --------
    raw = load_level_json(f"levels/level{index}.json")
    parsed = parse_level(raw)
    level = Level(parsed, index)



    # -------- TẠO PLAYER --------
    player = DummyPlayer(level.spawn_point)

    running = True
    while running:

        # -------- SỰ KIỆN --------
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

        # -------- UPDATE GAME --------
        player.update(level)      # update player physics
        level.update(player)      # coin, pit, goal
        level.update_camera(player, SCREEN_W)  # camera follow

        # -------- DRAW --------
        screen.fill((120, 190, 255))  # background

        level.draw(screen)
        player.draw(screen, level.offset_x)

        # Debug text
        font = pygame.font.SysFont("Arial", 20)
        screen.blit(font.render(f"Coins: {player.coins}", True, (0,0,0)), (10, 10))

        pygame.display.flip()
        clock.tick(60)

        # Nếu player win hoặc chết → dừng
        if player.dead or player.win:
            pygame.time.wait(1200)
            running = False

    pygame.quit()


# Chạy level1 mặc định
if __name__ == "__main__":
    run_level(1)
