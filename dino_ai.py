import pygame
import cv2
import mediapipe as mp
import random

# ---------------- INIT ----------------
pygame.init()

GAME_WIDTH, HEIGHT = 900, 450
CAM_WIDTH = 350
screen = pygame.display.set_mode((GAME_WIDTH + CAM_WIDTH, HEIGHT))
pygame.display.set_caption("NeuroRun - Geometric Edition")

clock = pygame.time.Clock()

FONT = pygame.font.SysFont("consolas", 26)
BIG = pygame.font.SysFont("consolas", 64)

# ---------------- COLORS ----------------
BG = (245, 248, 255)
BLACK = (20, 20, 20)
RED = (220, 60, 60)
BLUE = (60, 160, 255)
GRAY = (180, 180, 180)

GROUND_Y = HEIGHT - 80
CEILING_Y = 290

# ---------------- GAME STATES ----------------
START, PLAYING, GAME_OVER = 0, 1, 2
state = START

# ---------------- PLAYER ----------------
x = 120
y = GROUND_Y - 25
vy = 0
gravity = 0.8
jump_power = -15

normal_radius = 18
duck_radius = 10
radius = normal_radius

is_jumping = False
jump_lock = False
is_ducking = False

# ---------------- GAME ----------------
speed = 7
score = 0
high_score = 0

obstacles = []
timer = 0

# ---------------- CV ----------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

buffer = []

# ---------------- HAND LOGIC ----------------
def fingers_up(hand):
    tips = [8, 12, 16, 20]
    f = []

    if hand.landmark[4].x < hand.landmark[3].x:
        f.append(1)
    else:
        f.append(0)

    for t in tips:
        f.append(1 if hand.landmark[t].y < hand.landmark[t-2].y else 0)

    return f

# ---------------- PLAYER RECT ----------------
def player_rect():
    return pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)

# ---------------- OBSTACLES ----------------
def spawn_obstacle():
    w = random.randint(20, 35)
    h = random.randint(35, 60)

    return {
        "x": GAME_WIDTH,
        "w": w,
        "h": h,
        "type": random.choice(["spike_up", "spike_down"])
    }

def draw_spike(o):
    x_pos = o["x"]
    w = o["w"]
    h = o["h"]

    if o["type"] == "spike_up":
        # ground spike
        pygame.draw.polygon(screen, RED, [
            (x_pos, GROUND_Y),
            (x_pos + w / 2, GROUND_Y - h),
            (x_pos + w, GROUND_Y)
        ])
    else:
        # ceiling spike (downward)
        pygame.draw.polygon(screen, RED, [
            (x_pos, CEILING_Y),
            (x_pos + w / 2, CEILING_Y + h),
            (x_pos + w, CEILING_Y)
        ])

# ---------------- LOOP ----------------
running = True

while running:
    clock.tick(60)
    screen.fill(BG)

    # -------- EVENTS --------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if state == START and event.key == pygame.K_SPACE:
                state = PLAYING

            if state == GAME_OVER and event.key == pygame.K_r:
                state = PLAYING
                obstacles.clear()
                score = 0
                speed = 7
                y = GROUND_Y - 25
                vy = 0
                is_jumping = False
                jump_lock = False

    # -------- CV --------
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    action = None

    if ret:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = hands.process(rgb)

        if res.multi_hand_landmarks:
            for h in res.multi_hand_landmarks:
                # mp_draw.draw_landmarks(frame, h, mp_hands.HAND_CONNECTIONS)

                f = fingers_up(h)
                s = sum(f)

                if s == 5:
                    action = "jump"
                elif s == 0:
                    action = "duck"

    # cv2.imshow("CV", frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break
    # Resize webcam
    frame_small = cv2.resize(frame, (CAM_WIDTH, HEIGHT))

# Convert BGR -> RGB
    frame_small = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB)

# Rotate because pygame and cv2 use different axes
    frame_small = cv2.transpose(frame_small)

# Convert to pygame surface
    cam_surface = pygame.surfarray.make_surface(frame_small)

# Draw on the right side
    screen.blit(cam_surface, (GAME_WIDTH, 0))
    

    buffer.append(action)
    if len(buffer) > 6:
        buffer.pop(0)

    final_jump = buffer.count("jump") >= 4
    final_duck = buffer.count("duck") >= 4

    # -------- GAME --------
    if state == PLAYING:

        # -------- STATE ----------
        is_ducking = final_duck and not is_jumping
        radius = duck_radius if is_ducking else normal_radius

        # -------- JUMP ----------
        if final_jump and not is_jumping and not jump_lock:
            vy = jump_power
            is_jumping = True
            jump_lock = True

        # -------- PHYSICS ----------
        vy += gravity
        y += vy

        if y >= GROUND_Y - radius:
            y = GROUND_Y - radius
            vy = 0
            is_jumping = False
            jump_lock = False

        # -------- SPAWN ----------
        timer += 1
        if timer > max(40, 90 - int(speed * 3)):
            obstacles.append(spawn_obstacle())
            timer = 0

        # -------- MOVE ----------
        for o in obstacles:
            o["x"] -= speed

        obstacles = [o for o in obstacles if o["x"] > -50]

        # -------- COLLISION ----------
        p = player_rect()

        for o in obstacles:

            if o["type"] == "spike_up":
                spike_rect = pygame.Rect(
                    o["x"],
                    GROUND_Y - o["h"],
                    o["w"],
                    o["h"]
                )
            else:
                spike_rect = pygame.Rect(
                    o["x"],
                    CEILING_Y,
                    o["w"],
                    o["h"]
                )

            if p.colliderect(spike_rect):
                state = GAME_OVER
                high_score = max(high_score, score)

        score += 1
        speed += 0.02

    # -------- DRAW --------
    pygame.draw.line(screen, GRAY, (0, GROUND_Y), (GAME_WIDTH, GROUND_Y), 3)

    if state == START:
        screen.blit(BIG.render("GEOMETRIC RUN", True, BLACK), (220, 150))
        screen.blit(FONT.render("close FIST to DUCK, show FIVE fingers to JUMP", True, BLACK), (120, 230))
        screen.blit(FONT.render("Press SPACE to start", True, BLACK), (370, 330))

    elif state == PLAYING:

        pygame.draw.circle(screen, BLUE, (x, int(y)), radius)

        for o in obstacles:
            draw_spike(o)

        screen.blit(FONT.render(f"Score: {score}", True, BLACK), (20, 20))

    elif state == GAME_OVER:
        screen.blit(BIG.render("CRASHED", True, RED), (280, 160))
        screen.blit(FONT.render("Press R to restart", True, BLACK), (320, 240))
        screen.blit(FONT.render(f"High Score: {high_score}", True, BLACK), (330, 280))

    pygame.display.update()

pygame.quit()
cap.release()
cv2.destroyAllWindows()
