import pygame

# Internal game resolution
WIDTH = 1920
HEIGHT = 1080
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
DARK_RED = (125, 0, 0)
DARK_GRAY = (20, 20, 20)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 125)

# Game states
STATE_EXPLORE = "explore"
STATE_BATTLE = "battle"
STATE_BAR = "bar"
STATE_MENU = "menu"

pygame.font.init()
font = pygame.font.SysFont(None, 70)
small_font = pygame.font.SysFont(None, 50)

# Battle settings
atb_max = 100
menu_options = ["Attack", "Magic", "Conjure", "Item"]

# Shared items
items = [
    {"name": "Potion", "heal": 40, "quantity": 2},
    {"name": "Ether", "mp_restore": 20, "quantity": 1},
]

# Movement
player_speed = 5