import pygame
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.character import Player

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("TEST CHARACTER - Nhom26")
clock = pygame.time.Clock()

# ĐỔI TÊN SKIN Ở ĐÂY ĐỂ TEST TỪNG NHÂN VẬT
player = Player(400, 500, skin="nhanvat3")

running = True
while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.update(keys)
    screen.fill((135, 206, 235))
    player.draw(screen)

    font = pygame.font.SysFont("arial", 30)
    info = font.render(f"Skin: {player.skin} | State: {player.state}", True, (255,255,255))
    screen.blit(info, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()