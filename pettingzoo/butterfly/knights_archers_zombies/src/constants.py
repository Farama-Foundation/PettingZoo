# video options
FPS = 15
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_UNITS = 15

# zombie speeds
ZOMBIE_Y_SPEED = 5
ZOMBIE_Y_SPEED = ZOMBIE_Y_SPEED * 15.0 / FPS
if ZOMBIE_Y_SPEED % 1.0 != 0.0:
    raise ValueError(
        f"FPS of {FPS} leads to decimal place value of {ZOMBIE_Y_SPEED} for zombie_y_speed."
    )
ZOMBIE_Y_SPEED = int(ZOMBIE_Y_SPEED)

ZOMBIE_X_SPEED = 30
ZOMBIE_X_SPEED = ZOMBIE_X_SPEED * 15.0 / FPS
if ZOMBIE_X_SPEED % 1.0 != 0.0:
    raise ValueError(
        f"FPS of {FPS} leads to decimal place value of {ZOMBIE_X_SPEED} for zombie_x_speed."
    )
ZOMBIE_X_SPEED = int(ZOMBIE_X_SPEED)

# player rotation rate
PLAYER_ANG_RATE = 10
PLAYER_ANG_RATE = PLAYER_ANG_RATE * 15.0 / FPS
if PLAYER_ANG_RATE % 1.0 != 0.0:
    raise ValueError(
        f"FPS of {FPS} leads to decimal place value of {PLAYER_ANG_RATE} for angle_rate."
    )
PLAYER_ANG_RATE = int(PLAYER_ANG_RATE)

# archer stuff
ARCHER_X, ARCHER_Y = 400, 610

ARCHER_SPEED = 25
ARCHER_SPEED = ARCHER_SPEED * 15.0 / FPS
if ARCHER_SPEED % 1.0 != 0.0:
    raise ValueError(
        f"FPS of {FPS} leads to decimal place value of {ARCHER_SPEED} for archer_speed."
    )
ARCHER_SPEED = int(ARCHER_SPEED)

# knight stuff
KNIGHT_X, KNIGHT_Y = 800, 610

KNIGHT_SPEED = 25
KNIGHT_SPEED = KNIGHT_SPEED * 15.0 / FPS
if KNIGHT_SPEED % 1.0 != 0.0:
    raise ValueError(
        f"FPS of {FPS} leads to decimal place value of {KNIGHT_SPEED} for knight_speed."
    )
KNIGHT_SPEED = int(KNIGHT_SPEED)

# arrow stuff
ARROW_SPEED = 45
ARROW_SPEED = ARROW_SPEED * 15.0 / FPS
if ARROW_SPEED % 1.0 != 0.0:
    raise ValueError(
        f"FPS of {FPS} leads to decimal place value of {ARROW_SPEED} for arrow_speed."
    )
ARROW_SPEED = int(ARROW_SPEED)

# sword stuff
SWORD_SPEED = 20
SWORD_SPEED = SWORD_SPEED * 15.0 / FPS
if SWORD_SPEED % 1.0 != 0.0:
    raise ValueError(
        f"FPS of {FPS} leads to decimal place value of {SWORD_SPEED} for sword_speed."
    )
SWORD_SPEED = int(SWORD_SPEED)

MIN_PHASE = -3 / 15.0 * FPS
if MIN_PHASE % 1.0 != 0.0:
    raise ValueError(
        f"FPS of {FPS} leads to decimal place value of {MIN_PHASE} for min_phase."
    )
MIN_PHASE = int(MIN_PHASE)

MAX_PHASE = 3 / 15.0 * FPS
if MAX_PHASE % 1.0 != 0.0:
    raise ValueError(
        f"FPS of {FPS} leads to decimal place value of {MAX_PHASE} for max_phase."
    )
MAX_PHASE = int(MAX_PHASE)

ARROW_TIMEOUT = 3
SWORD_TIMEOUT = 0
