import pygame
import sys
import random
import hid # hidapi
from pygame.locals import *

# Configuration
USE_CONTROLLER = True

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 300, 600
BLOCK_SIZE = 30
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DIM_BLOCK_COLOR = (50, 50, 50)
COLORS = [
    (255, 0, 0),  # Red
    (0, 255, 0),  # Green
    (0, 0, 255),  # Blue
    (255, 255, 0),  # Yellow
    (0, 255, 255),  # Cyan
    (255, 0, 255)   # Magenta
]

# Fonts
font_large = pygame.font.SysFont('Arial', 48)
font_small = pygame.font.SysFont('Arial', 24)

# Tetrimino shapes
SHAPES = [
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1], [1, 1]],         # O
    [[1, 1, 1, 1]],           # I
    [[1, 1, 0], [0, 1, 1]],   # S
    [[0, 1, 1], [1, 1, 0]],   # Z
    [[1, 1, 1], [1, 0, 0]],   # L
    [[1, 1, 1], [0, 0, 1]]    # J
]

# Game variables
score = 0
grid = [[0 for _ in range(WIDTH // BLOCK_SIZE)] for _ in range(HEIGHT // BLOCK_SIZE)]
key_delay = {"left": 0, "right": 0}  # Prevents rapid movement

# Controller Setup (stubbed for now)
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
    """Draws text on the screen."""
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

def check_input():
    """Checks for user input from keyboard or controller."""
    key_map = {
        (1, 128, 128, 127, 127, 47,  0, 0): K_a,      # Example: Map to 'A' key
        (1, 128, 128, 127, 127, 31,  0, 0): K_b,      # Map to 'B' key
        (1, 128, 128, 127,   0, 15,  0, 0): K_UP,     # Map to 'UP' arrow
        (1, 128, 128, 127, 255, 15,  0, 0): K_DOWN,   # Map to 'DOWN' arrow
        (1, 128, 128,   0, 127, 15,  0, 0): K_LEFT,   # Map to 'LEFT' arrow
        (1, 128, 128, 255, 127, 15,  0, 0): K_RIGHT,  # Map to 'RIGHT' arrow
        (1, 128, 128, 127, 127, 15, 32, 0): K_SPACE,  # Start -> Space
        (1, 128, 128, 127, 127, 15, 16, 0): K_RETURN  # Select -> Enter
    }

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            return event.key

    if controller_connected:
        input_data = tuple(controller.read(64))
        if input_data and input_data in key_map:
            return key_map[input_data]

    return None

def rotate_tetrimino(tetrimino):
    """Rotates the Tetrimino shape clockwise."""
    rotated_shape = list(zip(*reversed(tetrimino['shape'])))
    return rotated_shape

def create_tetrimino():
    """Creates a new Tetrimino."""
    shape = random.choice(SHAPES)
    color = random.choice(COLORS)
    x = WIDTH // BLOCK_SIZE // 2 - len(shape[0]) // 2
    y = 0
    return {'shape': shape, 'color': color, 'x': x, 'y': y}

def draw_grid():
    """Draws the game grid."""
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, cell, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, BLACK, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_tetrimino(tetrimino):
    """Draws the active Tetrimino."""
    shape = tetrimino['shape']
    color = tetrimino['color']
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, color, ((tetrimino['x'] + x) * BLOCK_SIZE, (tetrimino['y'] + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, BLACK, ((tetrimino['x'] + x) * BLOCK_SIZE, (tetrimino['y'] + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def is_collision(tetrimino, dx, dy, rotated_shape=None):
    """Checks for collision with the grid or boundaries."""
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
    """Locks the Tetrimino into the grid."""
    shape = tetrimino['shape']
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                grid[tetrimino['y'] + y][tetrimino['x'] + x] = tetrimino['color']

def clear_lines():
    """Clears completed lines and updates the score."""
    global score
    full_lines = [y for y, row in enumerate(grid) if all(row)]
    for y in full_lines:
        del grid[y]
        grid.insert(0, [0 for _ in range(WIDTH // BLOCK_SIZE)])
    score += len(full_lines) * 10

def game_over_screen(final_score):
    """Displays the game over screen."""
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, DIM_BLOCK_COLOR, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    draw_text(f"Score: {final_score}", font_large, WHITE, screen, WIDTH // 2, HEIGHT // 2)
    pygame.display.update()
    pygame.time.wait(5000)

def ready_screen():
    """Displays the 'Ready?' screen."""
    screen.fill(BLACK)
    draw_text("Ready?", font_large, WHITE, screen, WIDTH // 2, HEIGHT // 2)
    pygame.display.update()
    while not check_input():
        pygame.time.wait(100)

def tetris_game():
    global score, grid
    grid = [[0 for _ in range(WIDTH // BLOCK_SIZE)] for _ in range(HEIGHT // BLOCK_SIZE)]
    score = 0
    tetrimino = create_tetrimino()
    drop_time = 500  # Initial drop time (ms)
    last_drop = pygame.time.get_ticks()
    last_move_time = {"left": 0, "right": 0, "down": 0, "up": 0}  # Add timers for key moves
    move_delay = 150  # 150 ms delay for left/right/down movements
    speed_increase_interval = 10000  # Every 10 seconds, decrease drop_time
    last_speed_increase = pygame.time.get_ticks()

    while True:
        screen.fill(BLACK)
        draw_grid()
        draw_tetrimino(tetrimino)
        draw_text(f"Score: {score}", font_small, WHITE, screen, 50, 20)
        pygame.display.update()

        input_key = check_input()
        current_time = pygame.time.get_ticks()

        # Handle input with delay
        if input_key == K_LEFT and not is_collision(tetrimino, -1, 0):
            if current_time - last_move_time["left"] > move_delay:
                tetrimino['x'] -= 1
                last_move_time["left"] = current_time

        if input_key == K_RIGHT and not is_collision(tetrimino, 1, 0):
            if current_time - last_move_time["right"] > move_delay:
                tetrimino['x'] += 1
                last_move_time["right"] = current_time

        if input_key == K_DOWN and not is_collision(tetrimino, 0, 1):
            if current_time - last_move_time["down"] > move_delay:
                tetrimino['y'] += 1

        if input_key == K_UP:
            rotated_shape = rotate_tetrimino(tetrimino)
            if not is_collision(tetrimino, 0, 0, rotated_shape):
                if current_time - last_move_time["up"] > move_delay:
                    tetrimino['shape'] = rotated_shape
                    last_move_time["up"] = current_time

        if input_key == K_SPACE:
            while not is_collision(tetrimino, 0, 1):
                tetrimino['y'] += 1

        # Automatic drop
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

        # Increase speed after a certain time (or score threshold)
        if current_time - last_speed_increase > speed_increase_interval:
            if drop_time > 100:  # Minimum drop_time to avoid going too fast
                drop_time -= 30  # Reduce drop_time by 50ms every 10 seconds
            last_speed_increase = current_time

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()


# Main execution loop
while True:
    ready_screen()
    tetris_game()
