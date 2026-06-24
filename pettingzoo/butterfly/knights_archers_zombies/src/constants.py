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
ZOMBIE_X_SPEED = 30

# player rotation rate
PLAYER_ANG_RATE = 10

# archer stuff
ARCHER_X, ARCHER_Y = 400, 610
ARCHER_SPEED = 25

# knight stuff
KNIGHT_X, KNIGHT_Y = 800, 610
KNIGHT_SPEED = 25

# arrow stuff
ARROW_SPEED = 45

# sword stuff
SWORD_SPEED = 20

MIN_ARC = -60
MAX_ARC = 60

# steps between when an archer attacks and can attack again
ARROW_TIMEOUT = 4
# steps between when a knight attacks and can do any action again
KNIGHT_TIMEOUT = 7
