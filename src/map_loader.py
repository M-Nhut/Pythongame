# map_loader.py – Bản CHUẨN cho game Mario + Debug thông tin level

import json
import os
import pygame

TILE_EMPTY = '.'
TILE_PLATFORM = '#'
TILE_COIN = 'C'
TILE_ENEMY = 'E'
TILE_SPAWN = 'P'
TILE_GOAL = 'G'
TILE_PIT = '_'
TILE_STONE = 'S'


def load_level_json(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Level file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "tile_size" not in data:
        raise KeyError("tile_size missing")
    if "tiles" not in data:
        raise KeyError("tiles missing")

    return data


def parse_level(data):
    tile_size = data["tile_size"]
    tiles = data["tiles"]

    platform_list = []
    stone_list = []       # <-- thêm list cho S
    pit_list = []
    coin_list = []
    enemy_list = []
    spawn_point = None
    goal_rect = None

    height = len(tiles)
    width = max(len(r) for r in tiles)

    for y, row in enumerate(tiles):
        row = row.ljust(width, TILE_EMPTY)

        for x, ch in enumerate(row):
            px = x * tile_size
            py = y * tile_size

            if ch == TILE_PLATFORM:
                platform_list.append(pygame.Rect(px, py, tile_size, tile_size))

            elif ch == TILE_STONE:           # <-- xử lý 'S'
                stone_list.append(pygame.Rect(px, py, tile_size, tile_size))

            elif ch == TILE_PIT:
                pit_list.append(pygame.Rect(px, py, tile_size, tile_size))

            elif ch == TILE_COIN:
                coin_list.append((px + tile_size // 2, py + tile_size // 2))

            elif ch == TILE_ENEMY:
                enemy_list.append((px, py))

            elif ch == TILE_SPAWN:
                spawn_point = (px, py)

            elif ch == TILE_GOAL:
                goal_rect = pygame.Rect(px, py, tile_size, tile_size)

    if spawn_point is None:
        raise ValueError("Spawn P missing!")
    if goal_rect is None:
        raise ValueError("Goal G missing!")

    # --------------------------
    # DEBUG: IN THÔNG TIN LEVEL
    # --------------------------
    print("\n===== LEVEL INFO =====")
    print(f"Tile size: {tile_size}")
    print(f"Platforms (#): {len(platform_list)}")
    print(f"Stones (S): {len(stone_list)}")        # <-- in số lượng S
    print(f"Pits (_): {len(pit_list)}")

    print(f"Coins: {len(coin_list)}")
    for cx, cy in coin_list:
        print(f"  - Coin pixel=({cx},{cy}) tile=({cx//tile_size},{cy//tile_size})")

    print(f"Enemies: {len(enemy_list)}")
    for ex, ey in enemy_list:
        print(f"  - Enemy pixel=({ex},{ey}) tile=({ex//tile_size},{ey//tile_size})")

    print(f"Spawn: pixel={spawn_point} tile=({spawn_point[0]//tile_size},{spawn_point[1]//tile_size})")

    gx, gy = goal_rect.topleft
    print(f"Goal: pixel=({gx},{gy}) tile=({gx//tile_size},{gy//tile_size})")

    # In từng stone pixel/tile (nếu cần)
    for s in stone_list:
        print(f"  - Stone pixel=({s.x},{s.y}) tile=({s.x//tile_size},{s.y//tile_size})")

    print("======================\n")

    return {
        "tile_size": tile_size,
        "platform_list": platform_list,
        "stone_list": stone_list,   # <-- trả về stone_list
        "pit_list": pit_list,
        "coin_list": coin_list,
        "enemy_list": enemy_list,
        "spawn_point": spawn_point,
        "goal_rect": goal_rect,
        "raw_tiles": tiles
    }


# --------------------------
# PHẦN TEST NHIỀU LEVEL
# --------------------------
def test_level(index):
    path = f"levels/level{index}.json"
    print(f"--- TEST LEVEL {index} ---")
    data = load_level_json(path)
    parse_level(data)


if __name__ == "__main__":
    pygame.init()
    try:
        for lv in range(1, 7):
            test_level(lv)
    finally:
        pygame.quit()
