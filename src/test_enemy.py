import pygame
from enemy import EnemyWalk, EnemyIdle
from items import Coin, Spike, BreakBlock, GoalFlag

pygame.init()
screen = pygame.display.set_mode((640, 360))
clock = pygame.time.Clock()

# ----- LOAD ASSET -----
def load_img(path):
    return pygame.transform.scale(pygame.image.load(path), (32, 32))

coin_imgs = [
    load_img("assets/items/coin1.png"),
    load_img("assets/items/coin2.png"),
    load_img("assets/items/coin3.png")
]

spike_img = load_img("assets/items/spike.png")
break_img = load_img("assets/items/break.png")
goal_img = load_img("assets/items/goal.png")

enemy_walk_img = load_img("assets/enemies/walk1.png")
enemy_idle_img = load_img("assets/enemies/idle.png")

# ----- CREATE OBJECT -----
player = pygame.Rect(100, 200, 28, 32)
coins = [Coin(200, 200, coin_imgs)]
spike = Spike(300, 200, spike_img)
breakblock = BreakBlock(350, 200, break_img)
goal = GoalFlag(500, 200, goal_img)

enemy = EnemyWalk(400, 200, speed=1)

coin_count = 0
running = True

# ----- GAME LOOP -----
while running:
    dt = clock.tick(60)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= 2
    if keys[pygame.K_RIGHT]:
        player.x += 2

    # ----- UPDATE -----
    enemy.update(dt)
    for c in coins: c.update(dt)

    # Print enemy position
    print("Enemy pos:", enemy.rect.x)

    # ----- COLLISION -----
    for c in coins:
        if not c.collected and player.colliderect(c.rect):
            c.collected = True
            coin_count += 1
            print("Coin +1 → total:", coin_count)

    if player.colliderect(spike.rect):
        print("player dead")
    
    if not breakblock.broken and player.colliderect(breakblock.rect):
        breakblock.broken = True
        print("Break block destroyed")

    if player.colliderect(goal.rect):
        print("Goal reached!")
    # ----- DRAW -----
    screen.fill((40, 40, 40))
    enemy.draw(screen, enemy_walk_img)
    for c in coins: c.draw(screen)
    spike.draw(screen)
    breakblock.draw(screen)
    goal.draw(screen)
    pygame.draw.rect(screen, (0, 200, 255), player)

    pygame.display.flip()

pygame.quit()
