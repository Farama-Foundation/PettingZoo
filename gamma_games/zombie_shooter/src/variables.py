import pygame
from src.players import Knight, Archer

# Defining Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Game Constants
ZOMBIE_SPAWN = 20
SPAWN_STAB_RATE = 20
FPS = 15
WIDTH = 1280
HEIGHT = 720

# Dictionaries for holding new players and their weapons
archer_dict = {}
knight_dict = {}
arrow_dict = {}
sword_dict = {}

# Game Variables
count = 0
score = 0
run = True
arrow_spawn_rate = sword_spawn_rate = zombie_spawn_rate = 0
knight_player_num = archer_player_num = 0
archer_killed = False
knight_killed = False
sword_killed = False

# Initializing Pygame
pygame.init()
WINDOW = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("Zombies, Knights, Archers")
clock = pygame.time.Clock()

# Creating Sprite Groups
all_sprites = pygame.sprite.Group()
zombie_list = pygame.sprite.Group()
arrow_list = pygame.sprite.Group()
sword_list = pygame.sprite.Group()
archer_list = pygame.sprite.Group()
knight_list = pygame.sprite.Group()

# Create a Knight
blue_trigon = pygame.Surface((60, 60), pygame.SRCALPHA)
pygame.gfxdraw.filled_polygon(blue_trigon, [(0, 40), (25, 5), (25, 0), (35, 0), (35, 5), (60, 40)], BLUE)
knight_dict["knight{0}".format(knight_player_num)] = Knight(blue_trigon)
knight_list.add(knight_dict["knight{0}".format(knight_player_num)])
all_sprites.add(knight_dict["knight{0}".format(knight_player_num)])

# Create an Archer
red_trigon = pygame.Surface((60, 60), pygame.SRCALPHA)
pygame.gfxdraw.filled_polygon(red_trigon, [(0, 40), (25, 5), (25, 0), (35, 0), (35, 5), (60, 40)], RED)   # [(20, 0), (10, 20), (30, 20)]
archer_dict["archer{0}".format(archer_player_num)] = Archer(red_trigon)
archer_list.add(archer_dict["archer{0}".format(archer_player_num)])
all_sprites.add(archer_dict["archer{0}".format(archer_player_num)])

# Creating Zombies
zombie_radius = 20
circle = pygame.Surface((50, 50), pygame.SRCALPHA)
pygame.gfxdraw.filled_circle(circle, 20, 20, zombie_radius, GREEN)

# Creating Sword
sword_rect = pygame.Surface((4, 25), pygame.SRCALPHA)