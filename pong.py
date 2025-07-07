import pygame
import time
import RPi.GPIO as GPIO

# Main config
WIN_SCORE = 5
BALL_SPEED = 3.5 # Initial value - override with keys 3/4/5/6


# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (25, 0, 50)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Paddle settings
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 100
PADDLE_SPEED = 10

# GPIO Pins for Hall Sensors and buttons
P1_SENSOR_A = 23
P1_SENSOR_B = 24
P2_SENSOR_A = 17
P2_SENSOR_B = 27
P1_START = 2
P2_START = 3

# Initialize GPIO
BOUNCE = 25
GPIO.setmode(GPIO.BCM)
GPIO.setup(P1_SENSOR_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(P1_SENSOR_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(P2_SENSOR_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(P2_SENSOR_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(P1_START, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(P2_START, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Ball settings
BALL_SIZE = 20
BALL_SPEED_X = BALL_SPEED
BALL_SPEED_Y = BALL_SPEED

# Game states
READY = 0
PLAYING = 1
GAME_OVER = 2

# Initialize screen
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen = pygame.display.set_mode((800, 600), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("BikePong")
pygame.mouse.set_visible(False)

# Clock for controlling frame rate
clock = pygame.time.Clock()

player_state = {
    "P1": {"last_trigger": None, "trigger_time": 0},
    "P2": {"last_trigger": None, "trigger_time": 0},
}

# Global game variables
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

def p1_ready(channel):
    global p1_ready_flag
    p1_ready_flag = True

def p2_ready(channel):
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
        display_text("Player 1", 48, GREEN if p1_ready_flag else RED, (200, SCREEN_HEIGHT // 2))
        display_text("Player 2", 48, GREEN if p2_ready_flag else RED, (SCREEN_WIDTH - 200, SCREEN_HEIGHT // 2))
        display_text(str(i), 256, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        pygame.display.flip()
        time.sleep(1)

def handle_sensor_trigger(player, sensor):
    current_time = time.time()
    state = player_state[player]

    if state["trigger_time"] and current_time - state["trigger_time"] > 0.10:
        print(f"{player} IDLE RESET")
        state["last_trigger"] = None
        state["trigger_count"] = 0

    # Initial trigger
    if state["last_trigger"] is None:
        print(f"{player} initial trigger: {sensor}")
        state["last_trigger"] = sensor
        state["trigger_time"] = current_time
        state["trigger_count"] = 1
        return

    # Determine direction based on last trigger
    if sensor == "A" and state["last_trigger"] == "B":
        print(f"{player} FWD motion (A -> B).")
        if player == "P1":
            p1_down()
            p1_down()
            p1_down()
        elif player == "P2":
            p2_down()
            p2_down()
            p2_down()
    elif sensor == "B" and state["last_trigger"] == "A":
        print(f"{player} REV motion (B -> A).")
        if player == "P1":
            p1_up()
            p1_up()
            p1_up()
        elif player == "P2":
            p2_up()
            p2_up()
            p2_up()

    # Update state
    state["last_trigger"] = sensor
    state["trigger_time"] = current_time
    state["trigger_count"] += 1

    # Reset state after two triggers
    if state["trigger_count"] >= 2:
        state["last_trigger"] = None
        state["trigger_count"] = 0


# GPIO callback functions
def p1_sensor_a_callback(channel):
    handle_sensor_trigger("P1", "A")

def p1_sensor_b_callback(channel):
    handle_sensor_trigger("P1", "B")

def p2_sensor_a_callback(channel):
    handle_sensor_trigger("P2", "A")

def p2_sensor_b_callback(channel):
    handle_sensor_trigger("P2", "B")

# Setup GPIO event detection
GPIO.add_event_detect(P1_SENSOR_A, GPIO.FALLING, callback=p1_sensor_a_callback, bouncetime=BOUNCE)
GPIO.add_event_detect(P1_SENSOR_B, GPIO.FALLING, callback=p1_sensor_b_callback, bouncetime=BOUNCE)
GPIO.add_event_detect(P2_SENSOR_A, GPIO.FALLING, callback=p2_sensor_a_callback, bouncetime=BOUNCE)
GPIO.add_event_detect(P2_SENSOR_B, GPIO.FALLING, callback=p2_sensor_b_callback, bouncetime=BOUNCE)
GPIO.add_event_detect(P1_START, GPIO.FALLING, callback=p1_ready, bouncetime=300)
GPIO.add_event_detect(P2_START, GPIO.FALLING, callback=p2_ready, bouncetime=300)


def game_loop():
    global ball_pos, ball_dir, p1_score, p2_score, p1_ready_flag, p2_ready_flag, game_state, winner, p1_pos, p2_pos, BALL_SPEED_X, BALL_SPEED_Y
    running = True

    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_3:
                    BALL_SPEED_X = 2.0
                    BALL_SPEED_Y = 2.0
                    ball_dir = [BALL_SPEED_X, BALL_SPEED_Y]
                elif event.key == pygame.K_4:
                    BALL_SPEED_X = 3.5
                    BALL_SPEED_Y = 3.5
                    ball_dir = [BALL_SPEED_X, BALL_SPEED_Y]
                elif event.key == pygame.K_5:
                    BALL_SPEED_X = 4.5
                    BALL_SPEED_Y = 4.5
                    ball_dir = [BALL_SPEED_X, BALL_SPEED_Y]
                elif event.key == pygame.K_6:
                    BALL_SPEED_X = 5.5
                    BALL_SPEED_Y = 5.5
                    ball_dir = [BALL_SPEED_X, BALL_SPEED_Y]
                elif event.key == pygame.K_7:
                    BALL_SPEED_X = 6.5
                    BALL_SPEED_Y = 6.5
                    ball_dir = [BALL_SPEED_X, BALL_SPEED_Y]
                elif event.key == pygame.K_8:
                    BALL_SPEED_X = 7.5
                    BALL_SPEED_Y = 7.5
                    ball_dir = [BALL_SPEED_X, BALL_SPEED_Y]
                elif event.key == pygame.K_9:
                    BALL_SPEED_X = 8.5
                    BALL_SPEED_Y = 8.5
                    ball_dir = [BALL_SPEED_X, BALL_SPEED_Y]
                
                # Update ball_dir when BALL_SPEED changes
                ball_dir = [BALL_SPEED if ball_dir[0] > 0 else -BALL_SPEED, 
                BALL_SPEED if ball_dir[1] > 0 else -BALL_SPEED]

        keys = pygame.key.get_pressed()
        # Player 1 controls (W/S)
        if keys[pygame.K_w]:
            p1_up()
        if keys[pygame.K_s]:
            p1_down()
        # Player 2 controls (UP/DOWN)
        if keys[pygame.K_UP]:
            p2_up()
        if keys[pygame.K_DOWN]:
            p2_down()
        # Ready buttons
        if keys[pygame.K_1]:
            p1_ready(True)
        if keys[pygame.K_2]:
            p2_ready(True)

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
            # Draw paddles and ball
            pygame.draw.rect(screen, WHITE, (50, p1_pos, PADDLE_WIDTH, PADDLE_HEIGHT))
            pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH - 50 - PADDLE_WIDTH, p2_pos, PADDLE_WIDTH, PADDLE_HEIGHT))
            pygame.draw.ellipse(screen, WHITE, (ball_pos[0], ball_pos[1], BALL_SIZE, BALL_SIZE))

            # Ball movement
            ball_pos[0] += ball_dir[0]
            ball_pos[1] += ball_dir[1]

            # Ball collision with top/bottom
            if ball_pos[1] <= 0 or ball_pos[1] >= SCREEN_HEIGHT - BALL_SIZE:
                ball_dir[1] = -ball_dir[1]

            # Ball collision with paddles
            if (50 <= ball_pos[0] <= 50 + PADDLE_WIDTH and p1_pos < ball_pos[1] + BALL_SIZE // 2 < p1_pos + PADDLE_HEIGHT) or \
               (SCREEN_WIDTH - 50 - PADDLE_WIDTH <= ball_pos[0] + BALL_SIZE <= SCREEN_WIDTH - 50 and p2_pos < ball_pos[1] + BALL_SIZE // 2 < p2_pos + PADDLE_HEIGHT):
                ball_dir[0] = -ball_dir[0]

            # Ball out of bounds
            if ball_pos[0] <= 0:
                p2_score += 1
                reset_ball()
            elif ball_pos[0] >= SCREEN_WIDTH - BALL_SIZE:
                p1_score += 1
                reset_ball()

            # Display score
            display_text(f"{p1_score} - {p2_score}", 48, WHITE, (SCREEN_WIDTH // 2, 50))

            # Check for win
            if p1_score >= WIN_SCORE:
                winner = "Player 1"
                game_state = GAME_OVER
                end_time = time.time()
            elif p2_score >= WIN_SCORE:
                winner = "Player 2"
                game_state = GAME_OVER
                end_time = time.time()

        elif game_state == GAME_OVER:
            display_text(f"{winner} WINS!", 72, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            if time.time() - end_time > 10:
                # Reset all game variables
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

    pygame.mouse.set_visible(True)
    pygame.quit()

if __name__ == "__main__":
    game_loop()
