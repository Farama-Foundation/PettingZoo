"""Various Constants used in Knights, Archers, Zombies."""
from enum import Enum


class Actions(Enum):
    """Actions available for each agent."""

    ACTION_FORWARD = 0
    ACTION_BACKWARD = 1
    ACTION_TURN_CCW = 2
    ACTION_TURN_CW = 3
    ACTION_ATTACK = 4
    ACTION_NONE = 5


# video options
FPS = 15
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
WALL_WIDTH = 100

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

MIN_ARC = -60
MAX_ARC = 60

# steps between when an archer attacks and can attack again
ARROW_TIMEOUT = 4
# steps between when a knight attacks and can do any action again
KNIGHT_TIMEOUT = 7
