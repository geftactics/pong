import pygame
import time
import math

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

PADDLE_WIDTH = 20
PADDLE_HEIGHT = 100
PADDLE_SPEED = 10

BALL_SIZE = 20
BALL_SPEED_X = 5
BALL_SPEED_Y = 5

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (50, 50, 0)

# Game state
READY = 0
PLAYING = 1
GAME_OVER = 2

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong Game")

clock = pygame.time.Clock()

ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
ball_dir = [BALL_SPEED_X, BALL_SPEED_Y]
p1_pos = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
p2_pos = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
p1_score = 0
p2_score = 0
p1_ready_flag = False
p2_ready_flag = False
game_state = READY
winner = None

background_time = 0
def draw_background():
    global background_time
    background_time += 0.05
    for y in range(0, SCREEN_HEIGHT, 30):
        for x in range(0, SCREEN_WIDTH, 30):
            offset = math.sin(background_time + x * 0.05 + y * 0.05) * 5
            pygame.draw.circle(screen, DARK_GREEN, (x + int(offset), y), 2)

def reset_ball():
    global ball_pos, ball_dir
    ball_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
    ball_dir[0] = BALL_SPEED_X * (-1 if ball_dir[0] > 0 else 1)
    ball_dir[1] = BALL_SPEED_Y * (-1 if ball_dir[1] > 0 else 1)

def p1_up():
    global p1_pos
    if p1_pos > 0:
        p1_pos -= PADDLE_SPEED

def p1_down():
    global p1_pos
    if p1_pos < SCREEN_HEIGHT - PADDLE_HEIGHT:
        p1_pos += PADDLE_SPEED

def p2_up():
    global p2_pos
    if p2_pos > 0:
        p2_pos -= PADDLE_SPEED

def p2_down():
    global p2_pos
    if p2_pos < SCREEN_HEIGHT - PADDLE_HEIGHT:
        p2_pos += PADDLE_SPEED

def p1_ready():
    global p1_ready_flag
    p1_ready_flag = True

def p2_ready():
    global p2_ready_flag
    p2_ready_flag = True

def display_text(text, size, color, position):
    font = pygame.font.Font(None, size)
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=position)
    screen.blit(text_surf, text_rect)

def countdown():
    for i in range(3, 0, -1):
        screen.fill(BLACK)
        draw_background()
        display_text("Player 1", 48, GREEN if p1_ready_flag else RED, (200, SCREEN_HEIGHT // 2))
        display_text("Player 2", 48, GREEN if p2_ready_flag else RED, (SCREEN_WIDTH - 200, SCREEN_HEIGHT // 2))
        display_text(str(i), 72, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        pygame.display.flip()
        time.sleep(1)

def game_loop():
    global ball_pos, ball_dir, p1_score, p2_score, p1_ready_flag, p2_ready_flag, game_state, winner, p1_pos, p2_pos
    running = True

    while running:
        screen.fill(BLACK)
        draw_background()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            p1_up()
        if keys[pygame.K_s]:
            p1_down()
        if keys[pygame.K_UP]:
            p2_up()
        if keys[pygame.K_DOWN]:
            p2_down()
        if keys[pygame.K_a]:
            p1_ready()
        if keys[pygame.K_l]:
            p2_ready()

        if game_state == READY:
            display_text("READY?", 72, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
            display_text("Player 1", 48, GREEN if p1_ready_flag else RED, (200, SCREEN_HEIGHT // 2))
            display_text("Player 2", 48, GREEN if p2_ready_flag else RED, (SCREEN_WIDTH - 200, SCREEN_HEIGHT // 2))
            
            if p1_ready_flag and p2_ready_flag:
                countdown()
                game_state = PLAYING
                p1_ready_flag = p2_ready_flag = False
                p1_score = p2_score = 0
                p1_pos = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
                p2_pos = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
                reset_ball()
        
        elif game_state == PLAYING:
            pygame.draw.rect(screen, GREEN, (50, p1_pos, PADDLE_WIDTH, PADDLE_HEIGHT))
            pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH - 50 - PADDLE_WIDTH, p2_pos, PADDLE_WIDTH, PADDLE_HEIGHT))
            pygame.draw.ellipse(screen, GREEN, (ball_pos[0], ball_pos[1], BALL_SIZE, BALL_SIZE))
            
            # movement
            ball_pos[0] += ball_dir[0]
            ball_pos[1] += ball_dir[1]
            
            # collision with top/bottom
            if ball_pos[1] <= 0 or ball_pos[1] >= SCREEN_HEIGHT - BALL_SIZE:
                ball_dir[1] = -ball_dir[1]

            # collision with paddles
            if (50 <= ball_pos[0] <= 50 + PADDLE_WIDTH and p1_pos < ball_pos[1] + BALL_SIZE // 2 < p1_pos + PADDLE_HEIGHT) or \
               (SCREEN_WIDTH - 50 - PADDLE_WIDTH <= ball_pos[0] + BALL_SIZE <= SCREEN_WIDTH - 50 and p2_pos < ball_pos[1] + BALL_SIZE // 2 < p2_pos + PADDLE_HEIGHT):
                ball_dir[0] = -ball_dir[0]

            # out of bounds
            if ball_pos[0] <= 0:
                p2_score += 1
                reset_ball()
            elif ball_pos[0] >= SCREEN_WIDTH - BALL_SIZE:
                p1_score += 1
                reset_ball()

            display_text(f"{p1_score} - {p2_score}", 48, GREEN, (SCREEN_WIDTH // 2, 50))

            if p1_score >= 5:
                winner = "Player 1"
                game_state = GAME_OVER
                end_time = time.time()
            elif p2_score >= 5:
                winner = "Player 2"
                game_state = GAME_OVER
                end_time = time.time()

        elif game_state == GAME_OVER:
            display_text(f"{winner} WINS!", 72, GREEN, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            if time.time() - end_time > 10:
                game_state = READY
                p1_ready_flag = False
                p2_ready_flag = False
                p1_score = 0
                p2_score = 0
                p1_pos = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
                p2_pos = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
                reset_ball()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    game_loop()
