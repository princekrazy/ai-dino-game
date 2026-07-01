import pygame
import cv2
import mediapipe as mp
import random

# ---------------- INIT ----------------
pygame.init()

WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CV Dino - Polished Edition")

clock = pygame.time.Clock()

FONT = pygame.font.SysFont("Arial", 24)
BIG_FONT = pygame.font.SysFont("Arial", 48)

# ---------------- COLORS ----------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)
GREEN = (0, 200, 0)
RED = (200, 50, 50)

GROUND_Y = HEIGHT - 50

# ---------------- GAME STATES ----------------
START = 0
PLAYING = 1
GAME_OVER = 2

state = START

# ---------------- PLAYER ----------------
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
jump_lock = False

# ---------------- GAME FEEL ----------------
base_speed = 6
speed = base_speed
speed_increase = 0.002

score = 0
high_score = 0

# ---------------- OBSTACLES ----------------
obstacles = []
obstacle_timer = 0

# ---------------- CV ----------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

action_buffer = []

# ---------------- FUNCTIONS ----------------
def fingers_up(hand_landmarks):
    tips = [8, 12, 16, 20]
    fingers = []

    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        fingers.append(1)
    else:
        fingers.append(0)

    for tip in tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers


def get_dino_rect():
    height = dino_height_duck if is_ducking else dino_height_stand
    y = dino_y + (dino_height_stand - height)
    return pygame.Rect(dino_x, y, dino_width, height)


def reset_game():
    global obstacles, speed, score
    global dino_y, velocity_y, is_jumping, is_ducking, jump_lock

    obstacles = []
    speed = base_speed
    score = 0

    dino_y = GROUND_Y - dino_height_stand
    velocity_y = 0
    is_jumping = False
    is_ducking = False
    jump_lock = False


def spawn_obstacle():
    obs_type = random.choice([1, 2])

    if obs_type == 1:
        size = random.randint(30, 60)
        y = GROUND_Y - size
        color = BLACK
    else:
        size = random.randint(20, 40)
        y = GROUND_Y - size - 20
        color = RED

    return {"x": WIDTH, "y": y, "size": size, "color": color}


# ---------------- LOOP ----------------
running = True

while running:
    clock.tick(60)
    screen.fill(WHITE)

    # ---------------- EVENTS ----------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            # START SCREEN
            if state == START:
                if event.key == pygame.K_SPACE:
                    state = PLAYING

            # GAME OVER SCREEN
            elif state == GAME_OVER:
                if event.key == pygame.K_r:
                    reset_game()
                    state = PLAYING

    # ---------------- CV ----------------
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    action = None

    if ret:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks:
            for handLms in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

                fingers = fingers_up(handLms)
                total = sum(fingers)

                if total == 5:
                    action = "jump"
                elif total == 0:
                    action = "duck"

    cv2.imshow("Hand Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        running = False

    # ---------------- SMOOTHING ----------------
    action_buffer.append(action)
    if len(action_buffer) > 7:
        action_buffer.pop(0)

    jump_votes = action_buffer.count("jump")
    duck_votes = action_buffer.count("duck")

    final_action = None

    if jump_votes >= 5:
        final_action = "jump"
    elif duck_votes >= 5:
        final_action = "duck"

    # ---------------- GAME LOGIC ----------------
    if state == PLAYING:

        # jump
        if final_action == "jump" and not is_jumping and not jump_lock:
            velocity_y = jump_power
            is_jumping = True
            jump_lock = True

        # duck
        is_ducking = (final_action == "duck")

        # physics
        velocity_y += gravity
        dino_y += velocity_y

        if dino_y >= GROUND_Y - dino_height_stand:
            dino_y = GROUND_Y - dino_height_stand
            velocity_y = 0
            is_jumping = False
            jump_lock = False

        # speed
        speed += speed_increase

        # spawn
        obstacle_timer = obstacle_timer + 1
        spawn_rate = max(45, 90 - int(speed * 3))

        if obstacle_timer > spawn_rate:
            obstacles.append(spawn_obstacle())
            obstacle_timer = 0

        # move
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

        score += 1

    # ---------------- DRAW GAME ----------------

    pygame.draw.line(screen, GRAY, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)

    if state == START:
        title = BIG_FONT.render("CV DINO GAME", True, BLACK)
        hint = FONT.render("Press SPACE to start (use hand gestures in game)", True, BLACK)

        screen.blit(title, (WIDTH//2 - 180, HEIGHT//2 - 60))
        screen.blit(hint, (WIDTH//2 - 220, HEIGHT//2))

    elif state == PLAYING:
        dino_rect = get_dino_rect()
        pygame.draw.rect(screen, GREEN, dino_rect)

        for obs in obstacles:
            pygame.draw.rect(screen, obs["color"],
                             (obs["x"], obs["y"], obs["size"], obs["size"]))

        score_text = FONT.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

    elif state == GAME_OVER:
        over = BIG_FONT.render("GAME OVER", True, BLACK)
        restart = FONT.render("Press R to Restart", True, BLACK)
        hs = FONT.render(f"High Score: {high_score}", True, BLACK)

        screen.blit(over, (WIDTH//2 - 140, HEIGHT//2 - 80))
        screen.blit(restart, (WIDTH//2 - 120, HEIGHT//2))
        screen.blit(hs, (WIDTH//2 - 120, HEIGHT//2 + 40))

    pygame.display.update()

# ---------------- CLEANUP ----------------
cap.release()
cv2.destroyAllWindows()
pygame.quit()