import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Game - Full Loop")

clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 24)
BIG_FONT = pygame.font.SysFont("Arial", 40)

# COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)
GREEN = (0, 200, 0)
RED = (200, 50, 50)

GROUND_Y = HEIGHT - 50

# GAME STATES
START = 0
PLAYING = 1
GAME_OVER = 2

state = START

# PLAYER
dino_x = 80
dino_y = GROUND_Y - 50
dino_width = 40
dino_height_stand = 50
dino_height_duck = 25

velocity_y = 0
gravity = 0.8
jump_power = -14

is_jumping = False
is_ducking = False

# SPEED
base_speed = 6
speed = base_speed
speed_increase = 0.002

# OBSTACLES
obstacles = []
obstacle_timer = 0

# SCORE
score = 0
high_score = 0

def get_dino_rect():
    height = dino_height_duck if is_ducking else dino_height_stand
    y = dino_y + (dino_height_stand - height)
    return pygame.Rect(dino_x, y, dino_width, height)

def reset_game():
    global obstacles, speed, score, dino_y, velocity_y, is_jumping, is_ducking
    obstacles = []
    speed = base_speed
    score = 0
    dino_y = GROUND_Y - dino_height_stand
    velocity_y = 0
    is_jumping = False
    is_ducking = False

def spawn_obstacle():
    obs_type = random.choice([1, 2])

    if obs_type == 1:
        size = random.randint(30, 60)
        y = GROUND_Y - size
        color = BLACK
    else:
        size = random.randint(30, 60)
        y = GROUND_Y - size - 30
        color = RED

    return {
        "x": WIDTH,
        "y": y,
        "size": size,
        "type": obs_type,
        "color": color
    }

running = True

while running:
    clock.tick(60)
    screen.fill(WHITE)

    # ---------------- INPUT ----------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if state == START:
                if event.key == pygame.K_SPACE:
                    state = PLAYING

            elif state == PLAYING:
                if event.key == pygame.K_SPACE:
                    if not is_jumping:
                        velocity_y = jump_power
                        is_jumping = True

                if event.key == pygame.K_DOWN:
                    is_ducking = True

            elif state == GAME_OVER:
                if event.key == pygame.K_r:
                    reset_game()
                    state = PLAYING

        if event.type == pygame.KEYUP:
            if state == PLAYING:
                if event.key == pygame.K_DOWN:
                    is_ducking = False

    # ---------------- GAME LOGIC ----------------
    if state == PLAYING:

        # physics
        velocity_y += gravity
        dino_y += velocity_y

        if dino_y >= GROUND_Y - dino_height_stand:
            dino_y = GROUND_Y - dino_height_stand
            velocity_y = 0
            is_jumping = False

        # speed scaling
        speed += speed_increase

        # spawn obstacles
        obstacle_timer += 1
        spawn_rate = max(45, 90 - int(speed * 3))

        if obstacle_timer > spawn_rate:
            obstacles.append(spawn_obstacle())
            obstacle_timer = 0

        # move obstacles
        for obs in obstacles:
            obs["x"] -= speed

        obstacles = [o for o in obstacles if o["x"] > -50]

        # collision
        dino_rect = get_dino_rect()

        for obs in obstacles:
            obs_rect = pygame.Rect(obs["x"], obs["y"], obs["size"], obs["size"])
            if dino_rect.colliderect(obs_rect):
                state = GAME_OVER
                if score > high_score:
                    high_score = score

        # score
        score += 1

    # ---------------- DRAW ----------------

    pygame.draw.line(screen, GRAY, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)

    # START SCREEN
    if state == START:
        text = BIG_FONT.render("Press SPACE to Start", True, BLACK)
        screen.blit(text, (WIDTH//2 - 180, HEIGHT//2 - 20))

    # GAME OVER SCREEN
    elif state == GAME_OVER:
        text = BIG_FONT.render("GAME OVER", True, BLACK)
        screen.blit(text, (WIDTH//2 - 100, HEIGHT//2 - 60))

        restart = FONT.render("Press R to Restart", True, BLACK)
        screen.blit(restart, (WIDTH//2 - 110, HEIGHT//2))

        hs = FONT.render(f"High Score: {high_score}", True, BLACK)
        screen.blit(hs, (WIDTH//2 - 110, HEIGHT//2 + 30))

    # PLAYING
    else:
        # dino
        dino_rect = get_dino_rect()
        pygame.draw.rect(screen, GREEN, dino_rect)

        # obstacles
        for obs in obstacles:
            pygame.draw.rect(screen, obs["color"],
                             (obs["x"], obs["y"], obs["size"], obs["size"]))

        # score
        score_text = FONT.render(f"Score: {score}", True, BLACK)
        speed_text = FONT.render(f"Speed: {speed:.2f}", True, BLACK)

        screen.blit(score_text, (10, 10))
        screen.blit(speed_text, (10, 35))

    pygame.display.update()

pygame.quit()