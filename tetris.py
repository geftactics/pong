import pygame
import sys
import random
import hid  # hidapi
from pygame.locals import *

# Configuration
USE_CONTROLLER = True

# Initialize Pygame
pygame.init()

# Playfield dimensions (fixed 10x20 blocks)
WIDTH, HEIGHT = 300, 600
BLOCK_SIZE = 30
screen = pygame.display.set_mode((800, 600), pygame.FULLSCREEN)
pygame.display.set_caption("Tetris")

# Offset to center playfield
offset_x = (screen.get_width() - WIDTH) // 2
offset_y = (screen.get_height() - HEIGHT) // 2

# Colors
WHITE = (255, 255, 255)
BLACK = (25, 0, 50)
DIM_BLOCK_COLOR = (50, 50, 50)
COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (0, 255, 255),
    (255, 0, 255)
]

# Fonts (blocky, LED-friendly)
font_huge = pygame.font.SysFont('', 200, bold=False)
font_large = pygame.font.SysFont('', 96, bold=False)
font_small = pygame.font.SysFont('', 72, bold=False)

# Tetrimino shapes
SHAPES = [
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1], [1, 1]],
    [[1, 1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]]
]

score = 0
grid = [[0 for _ in range(WIDTH // BLOCK_SIZE)] for _ in range(HEIGHT // BLOCK_SIZE)]

if USE_CONTROLLER:
    try:
        controller = hid.device()
        controller.open(0x0810, 0xe501)
        controller.set_nonblocking(True)
        controller_connected = True
    except Exception as e:
        controller_connected = False
        print("Controller not connected.", e)
else:
    controller_connected = False

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

def check_input():
    key_map = {
        (1, 128, 128, 127, 127, 47,  0, 0): K_a,
        (1, 128, 128, 127, 127, 31,  0, 0): K_b,
        (1, 128, 128, 127,   0, 15,  0, 0): K_UP,
        (1, 128, 128, 127, 255, 15,  0, 0): K_DOWN,
        (1, 128, 128,   0, 127, 15,  0, 0): K_LEFT,
        (1, 128, 128, 255, 127, 15,  0, 0): K_RIGHT,
        (1, 128, 128, 127, 127, 15, 32, 0): K_SPACE,
        (1, 128, 128, 127, 127, 15, 16, 0): K_RETURN
    }
    try:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                return event.key
    except Exception as e:
        print("Event error:", e)
        pygame.event.clear()

    if controller_connected:
        while True:
            input_data = tuple(controller.read(64))
            if not input_data:
                break
            if input_data in key_map:
                return key_map[input_data]
    return None

def rotate_tetrimino(tetrimino):
    return list(zip(*reversed(tetrimino['shape'])))

def create_tetrimino():
    shape = random.choice(SHAPES)
    color = random.choice(COLORS)
    x = WIDTH // BLOCK_SIZE // 2 - len(shape[0]) // 2
    y = 0
    return {'shape': shape, 'color': color, 'x': x, 'y': y}

def draw_grid():
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, cell,
                                 (offset_x + x * BLOCK_SIZE, offset_y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, BLACK,
                                 (offset_x + x * BLOCK_SIZE, offset_y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_tetrimino(tetrimino):
    for y, row in enumerate(tetrimino['shape']):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, tetrimino['color'],
                    (offset_x + (tetrimino['x'] + x) * BLOCK_SIZE,
                     offset_y + (tetrimino['y'] + y) * BLOCK_SIZE,
                     BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, BLACK,
                    (offset_x + (tetrimino['x'] + x) * BLOCK_SIZE,
                     offset_y + (tetrimino['y'] + y) * BLOCK_SIZE,
                     BLOCK_SIZE, BLOCK_SIZE), 1)

def is_collision(tetrimino, dx, dy, rotated_shape=None):
    shape = rotated_shape if rotated_shape else tetrimino['shape']
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                new_x = tetrimino['x'] + x + dx
                new_y = tetrimino['y'] + y + dy
                if new_x < 0 or new_x >= WIDTH // BLOCK_SIZE or new_y >= HEIGHT // BLOCK_SIZE or (new_y >= 0 and grid[new_y][new_x]):
                    return True
    return False

def lock_tetrimino(tetrimino):
    for y, row in enumerate(tetrimino['shape']):
        for x, cell in enumerate(row):
            if cell:
                grid[tetrimino['y'] + y][tetrimino['x'] + x] = tetrimino['color']

def clear_lines():
    global score
    full_lines = [y for y, row in enumerate(grid) if all(row)]
    for y in full_lines:
        del grid[y]
        grid.insert(0, [0 for _ in range(WIDTH // BLOCK_SIZE)])
    score += len(full_lines) * 10

def game_over_screen(final_score):
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, DIM_BLOCK_COLOR, (offset_x + x * BLOCK_SIZE, offset_y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    draw_text(f"{final_score}", font_large, WHITE, screen, screen.get_width() // 2, screen.get_height() // 2)
    pygame.display.update()
    pygame.time.wait(5000)

def ready_screen():
    screen.fill(BLACK)
    draw_text("Ready?", font_large, WHITE, screen, screen.get_width() // 2, screen.get_height() // 2)
    pygame.display.update()
    while True:
        input_key = check_input()
        if input_key == K_SPACE:
            break
        pygame.time.wait(100)

def tetris_game():
    global score, grid
    grid = [[0 for _ in range(WIDTH // BLOCK_SIZE)] for _ in range(HEIGHT // BLOCK_SIZE)]
    score = 0
    tetrimino = create_tetrimino()
    drop_time = 500
    last_drop = pygame.time.get_ticks()
    last_move_time = {"left": 0, "right": 0, "down": 0, "up": 0}
    move_delay = 150
    speed_increase_interval = 5000
    last_speed_increase = pygame.time.get_ticks()

    while True:
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, (offset_x - 2, offset_y - 2, WIDTH + 4, HEIGHT + 4), 2)

        draw_grid()
        draw_tetrimino(tetrimino)
        draw_text(f"{score}", font_small, WHITE, screen, offset_x + WIDTH + 60, offset_y + 30)
        pygame.display.update()

        input_key = check_input()
        current_time = pygame.time.get_ticks()

        if input_key == K_LEFT and not is_collision(tetrimino, -1, 0):
            if current_time - last_move_time["left"] > move_delay:
                tetrimino['x'] -= 1
                last_move_time["left"] = current_time

        if input_key == K_RIGHT and not is_collision(tetrimino, 1, 0):
            if current_time - last_move_time["right"] > move_delay:
                tetrimino['x'] += 1
                last_move_time["right"] = current_time

        # Removed soft drop from DOWN key since it now does hard drop
        pass

        if input_key == K_UP:
            rotated_shape = rotate_tetrimino(tetrimino)
            if not is_collision(tetrimino, 0, 0, rotated_shape):
                if current_time - last_move_time["up"] > move_delay:
                    tetrimino['shape'] = rotated_shape
                    last_move_time["up"] = current_time

        # Use DOWN for hard drop (traditional Tetris control)
        if input_key == K_DOWN:
            while not is_collision(tetrimino, 0, 1):
                tetrimino['y'] += 1

        if current_time - last_drop > drop_time:
            if not is_collision(tetrimino, 0, 1):
                tetrimino['y'] += 1
            else:
                lock_tetrimino(tetrimino)
                clear_lines()
                tetrimino = create_tetrimino()
                if is_collision(tetrimino, 0, 0):
                    game_over_screen(score)
                    return
            last_drop = current_time

        if current_time - last_speed_increase > speed_increase_interval:
            if drop_time > 200:
                drop_time -= 30
            last_speed_increase = current_time

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

while True:
    ready_screen()
    tetris_game()
