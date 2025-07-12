import pygame
import sys
import random
import hid  # hidapi
from pygame.locals import *

move_delay = 250

# Configuration
USE_CONTROLLER = True

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.FULLSCREEN)
pygame.display.set_caption("Snake")
pygame.mouse.set_visible(False)

# Colors
BLACK = (25, 0, 50)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (120, 120, 120)

# Font
font_large = pygame.font.SysFont('Courier New', 48, bold=True)
font_huge = pygame.font.SysFont('Courier New', 96, bold=True)

# Game area
CELL_SIZE = 60  # Bigger cells to take more space
GRID_WIDTH = 800 // CELL_SIZE
GRID_HEIGHT = 600 // CELL_SIZE

# Controller setup
if USE_CONTROLLER:
    try:
        controller = hid.device()
        controller.open(0x1c59, 0x0026) 
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
    joy_map = {
        (0x7F, 0x00): K_UP,
        (0x7F, 0xFF): K_DOWN,
        (0x00, 0x7F): K_LEFT,
        (0xFF, 0x7F): K_RIGHT,
    }
    idle = [0x7F, 0x7F, 0x80, 0x80, 0x80, 0x80, 0x00, 0x00]
    start_btn = 0x04

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.mouse.set_visible(True)
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.mouse.set_visible(True)
                pygame.quit()
                sys.exit()
            return event.key

    if controller_connected:
        data = controller.read(64)
        if data and data[:8] != idle:
            xy = tuple(data[:2])
            if xy in joy_map:
                return joy_map[xy]
            if data[6] == start_btn:
                return K_SPACE
    return None


def ready_screen():
    screen.fill(BLACK)
    draw_text("Ready?", font_large, WHITE, screen, screen.get_width() // 2, screen.get_height() // 2)
    pygame.display.update()
    while not check_input():
        pygame.time.wait(100)

def game_over_screen(score, snake, food):
    screen.fill(BLACK)
    for segment in snake:
        pygame.draw.rect(screen, GRAY, (segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, GRAY, (food[0]*CELL_SIZE, food[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    draw_text(f"{score}", font_huge, WHITE, screen, screen.get_width() // 2, screen.get_height() // 2)
    pygame.display.update()
    pygame.time.wait(3000)

def random_food(snake):
    while True:
        pos = [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)]
        if pos not in snake:
            return pos

def snake_game():
    snake = [[GRID_WIDTH // 2, GRID_HEIGHT // 2]]
    direction = [0, -1]
    food = random_food(snake)
    clock = pygame.time.Clock()
    score = 0
    
    last_move = pygame.time.get_ticks()

    while True:
        screen.fill(BLACK)

        # Draw snake
        for segment in snake:
            pygame.draw.rect(screen, GREEN, (segment[0]*CELL_SIZE, segment[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Draw food
        pygame.draw.rect(screen, RED, (food[0]*CELL_SIZE, food[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        pygame.display.update()
        input_key = check_input()
        if input_key == K_UP and direction != [0, 1]: direction = [0, -1]
        if input_key == K_DOWN and direction != [0, -1]: direction = [0, 1]
        if input_key == K_LEFT and direction != [1, 0]: direction = [-1, 0]
        if input_key == K_RIGHT and direction != [-1, 0]: direction = [1, 0]

        current_time = pygame.time.get_ticks()
        if current_time - last_move > move_delay:
            head = [snake[0][0] + direction[0], snake[0][1] + direction[1]]

            if head in snake or not (0 <= head[0] < GRID_WIDTH and 0 <= head[1] < GRID_HEIGHT):
                game_over_screen(score, snake, food)
                return

            snake.insert(0, head)
            if head == food:
                score += 1
                food = random_food(snake)
            else:
                snake.pop()

            last_move = current_time

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.mouse.set_visible(True)
                pygame.quit()
                sys.exit()

# Main loop
while True:
    ready_screen()
    snake_game()
