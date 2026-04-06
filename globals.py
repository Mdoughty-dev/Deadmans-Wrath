import pygame

# Screen setup
WIDTH, HEIGHT = 1920, 1080
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

# Fonts (initialize pygame.font in main before import if needed)
pygame.font.init()
font = pygame.font.SysFont(None, 70)
small_font = pygame.font.SysFont(None, 50)

# Battle variables
player_name = "Maddo"
player_hp = 100
player_max_hp = 100
player_mp = 30
player_max_mp = 30
player_atb = 0
atb_max = 100
battle_menu_index = 0
menu_options = ["Attack", "Magic", "Item"]
magic_options = ["Hex", "Cure"]
magic_index = 0
player_turn = False
in_magic_menu = False
battle_log = ""

# Enemy variables
enemy_hp = 100
enemy_max_hp = 100
enemy_atb = 0
enemy_turn = False
enemy_attack_cycle = ["Knife Stab", "Knife Stab", "Knife Fury"]
enemy_attack_index = 0

# Player setup
player_speed = 5

# Camera offset
camera_x = 0

